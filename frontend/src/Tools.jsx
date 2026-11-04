import { useEffect, useMemo, useRef, useState } from 'react'
import { ArrowRight, ArrowUpRight, FileText, LocateFixed, MapPin, Search, Sparkles } from 'lucide-react'
import { mergeSchemeMatches, schemeTitle, searchSchemes } from './content.js'

async function request(path, options = {}) {
  const response = await fetch(path, options)
  const body = await response.json().catch(() => ({}))
  if (!response.ok) throw Object.assign(new Error('Request failed'), { status: response.status, code: body.error_code })
  return body
}

async function protectedRequest(path, options, signal) {
  const { csrfToken } = await request('/studio/session', { cache: 'no-store', signal })
  return request(path, { ...options, method: 'POST', signal, headers: { ...options.headers, 'X-CSRFToken': csrfToken } })
}

export async function searchByMeaning(query, filters, signal) {
  const { ids } = await protectedRequest('/studio/search', {
    headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ query, ...filters }),
  }, signal)
  if (!Array.isArray(ids)) throw new Error('Missing search results')
  return ids
}

function useRequest() {
  const active = useRef(null)
  useEffect(() => () => active.current?.abort(), [])
  return () => {
    active.current?.abort()
    const controller = new AbortController()
    active.current = controller
    const timeout = setTimeout(() => controller.abort('timeout'), 85_000)
    return { controller, dispose: () => clearTimeout(timeout) }
  }
}

export function PanelHeader({ tag, title, desc }) {
  return <header className="panel-header"><span className="eyebrow">{tag}</span><h2>{title}</h2><p>{desc}</p></header>
}

export function Assistant({ schemes, lang, t, online, open }) {
  const [question, setQuestion] = useState('')
  const [result, setResult] = useState(null)
  const [busy, setBusy] = useState(false)
  const start = useRequest()
  async function ask(event) {
    event.preventDefault()
    const query = question.trim()
    if (!query || busy) return
    const local = searchSchemes(schemes, query, { partial: true }).slice(0, 5)
    const mode = event.nativeEvent.submitter?.value
    if (mode !== 'online' && mode !== 'meaning') return setResult({ matches: local })
    const { controller, dispose } = start()
    setBusy(true)
    setResult(null)
    try {
      if (mode === 'meaning') {
        const ids = await searchByMeaning(query, {}, controller.signal)
        const matches = ids.length ? mergeSchemeMatches(schemes, searchSchemes(schemes, query), [...ids, ...local.map(scheme => scheme.id)]) : local
        return setResult({ matches: matches.slice(0, 5), notice: ids.length ? '' : 'meaningNoMatches' })
      }
      const data = await protectedRequest('/chat', {
        headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ question: query, lang, catalog: 'studio' }),
      }, controller.signal)
      const names = new Set(data.matched_schemes?.map(item => item.scheme_name))
      setResult({ matches: schemes.filter(item => names.has(item.name)), answer: data.answer, ai: data.used_ai })
    } catch {
      if (!controller.signal.aborted || controller.signal.reason === 'timeout') {
        setResult({ matches: local, notice: mode === 'meaning' ? 'meaningUnavailable' : 'offlineAnswer' })
      }
    } finally { dispose(); setBusy(false) }
  }
  return <section className="work-panel">
    <PanelHeader tag={t('assistant')} title={t('assistantTitle')} desc={t('assistantDesc')} />
    <form className="tool-card" onSubmit={ask}>
      <label htmlFor="question">{t('question')}</label>
      <p className="muted" id="assistant-search-guide">{t('meaningGuide')}</p>
      <textarea id="question" rows={4} maxLength={500} required aria-describedby="assistant-search-guide" placeholder={t('questionHint')} value={question} onChange={event => setQuestion(event.target.value)} />
      <p className="muted">{t('meaningHint')}</p>
      <p className="muted">{t('aiPrivacy')}</p>
      <div className="action-row">
        <button className="button primary" disabled={busy || !question.trim()}><Search size={18} />{t('catalogSearch')}</button>
        <button className="button subtle" value="meaning" disabled={busy || !online || !question.trim()}><Search size={18} />{t('meaningSearch')}</button>
        <button className="button subtle" value="online" disabled={busy || !online || !question.trim()}><Sparkles size={18} />{t('ai')}</button>
      </div>
    </form>
    <div aria-live="polite" className="tool-result">{busy && <p>{t('waiting')}</p>}
      {result && <article className="tool-card">
        <h3>{t(result.ai ? 'aiResult' : 'catalogResult')}</h3>
        {result.notice && <p>{t(result.notice)}</p>}
        {result.answer && <p className="answer-text">{result.answer}</p>}
        {result.matches.length ? <ul className="result-links">{result.matches.map(scheme => <li key={scheme.id}>
          <button className="text-button" onClick={() => open(scheme)}>{schemeTitle(scheme, lang)}<ArrowRight size={16} /></button>
        </li>)}</ul> : !result.answer && <p>{t('noResults')}</p>}
      </article>}
    </div>
  </section>
}

export function PdfTools({ t, online, browse, open }) {
  const [file, setFile] = useState(null)
  const [consent, setConsent] = useState(false)
  const [busy, setBusy] = useState(false)
  const [status, setStatus] = useState('')
  const [summary, setSummary] = useState(null)
  const start = useRequest()
  async function submit(event) {
    event.preventDefault()
    if (!file || !consent || !online || busy) return
    if (!/\.pdf$/i.test(file.name) || file.size <= 0 || file.size > 5_000_000) return setStatus('pdfBad')
    const data = new FormData()
    data.append('document', file)
    data.append('consent', 'true')
    const { controller, dispose } = start()
    setBusy(true); setStatus(''); setSummary(null)
    try {
      const result = await protectedRequest('/simplify', { body: data }, controller.signal)
      if (!result.is_ai_generated || !result.simplified || !result.telugu) throw new Error('Missing summary')
      setSummary({ id: 'summary', ai: true, name: t('pdfSummary'), en: result.simplified, te: result.telugu, audio: result.voice_url })
    } catch (error) {
      if (!controller.signal.aborted || controller.signal.reason === 'timeout')
        setStatus(error.status === 503 ? 'pdfUnavailable' : error.status === 413 || error.code === 'INVALID_PDF' ? 'pdfBad' : 'pdfError')
    } finally { dispose(); setBusy(false) }
  }
  return <section className="work-panel">
    <PanelHeader tag={t('pdf')} title={t('pdfTitle')} desc={t('pdfDesc')} />
    <div className="pdf-grid">
      <form className="tool-card" onSubmit={submit}>
        <label htmlFor="public-pdf"><FileText size={20} /> {t('pdfFile')}</label>
        <input id="public-pdf" type="file" accept="application/pdf,.pdf" disabled={busy} onChange={event => {
          setFile(event.target.files[0] || null); setConsent(false); setStatus(''); setSummary(null)
        }} />
        <p className="muted">{t('pdfLimits')}</p>
        <label className="consent"><input type="checkbox" checked={consent} disabled={busy || !file} onChange={event => setConsent(event.target.checked)} /> {t('pdfConsent')}</label>
        <button className="button primary" disabled={!online || busy || !file || !consent}><Sparkles size={17} />{t(busy ? 'waiting' : 'simplify')}</button>
        {(!online || status) && <p role="status">{t(status || 'pdfUnavailable')}</p>}
        {summary && <div role="status"><button type="button" className="text-button" onClick={() => open(summary)}>{t('pdfSummary')} <ArrowRight size={17} /></button></div>}
      </form>
      <article className="tool-card pdf-aside"><FileText size={27} /><h3>{t('guide')}</h3><p>{t('checklistNote')}</p><button className="button subtle" onClick={browse}>{t('browse')} <ArrowRight size={17} /></button></article>
    </div>
  </section>
}

export function Care({ t, online }) {
  const [directory, setDirectory] = useState([])
  const [status, setStatus] = useState('loading')
  const [attempt, retry] = useState(0)
  const [district, setDistrict] = useState('')
  const [query, setQuery] = useState('')
  const [limit, setLimit] = useState(12)
  useEffect(() => {
    const controller = new AbortController()
    request('/studio/facilities.json', { signal: controller.signal })
      .then(({ facilities }) => { setDirectory(facilities); setStatus('') })
      .catch(() => { if (!controller.signal.aborted) setStatus('loadError') })
    return () => controller.abort()
  }, [attempt])
  const districts = useMemo(() => [...new Set(directory.map(place => place.district).filter(Boolean))].sort(), [directory])
  const term = query.trim().toLowerCase()
  const matches = useMemo(() => directory.filter(place => (!district || place.district === district) &&
    (!term || [place.name, place.village, place.mandal, place.type].join(' ').toLowerCase().includes(term))), [directory, district, term])
  return <section className="work-panel">
    <PanelHeader tag={t('facilitySource')} title={t('careTitle')} desc={t('careDesc')} />
    <div className="filter-row">
      <label className="search-box"><Search size={20} /><input aria-label={t('facilitySearch')} placeholder={t('facilitySearch')} value={query} onChange={event => { setQuery(event.target.value); setLimit(12) }} /></label>
      <select aria-label={t('district')} value={district} onChange={event => { setDistrict(event.target.value); setLimit(12) }}>
        <option value="">{t('districts')}</option>{districts.map(name => <option key={name}>{name}</option>)}
      </select>
    </div>
    {status ? <p role="status">{t(status)} {status === 'loadError' && <button className="text-button" onClick={() => { setStatus('loading'); retry(attempt + 1) }}>{t('retry')}</button>}</p> :
      <>
        <p className="count" aria-live="polite">{matches.length} {t('facilityResults')}</p>
        {!matches.length && <div className="empty"><MapPin size={26} /><p>{t('noFacilities')}</p></div>}
        <div className="cards">{matches.slice(0, limit).map(place => <article key={place.id} className="scheme-card facility-card">
          <span className="pill"><MapPin size={14} /> {place.type}</span><h3>{place.name}</h3>
          <p>{[place.mandal, place.district].filter(Boolean).join(' · ')}</p>
          <div className="action-row">{online && Number.isFinite(place.lat) && Number.isFinite(place.lng) ?
            <a className="text-button" href={`https://www.openstreetmap.org/?mlat=${place.lat}&mlon=${place.lng}#map=15/${place.lat}/${place.lng}`} target="_blank" rel="noreferrer">{t('map')} <ArrowUpRight size={15} /></a>
            : !online && <span className="muted"><LocateFixed size={14} /> {t('mapOffline')}</span>}</div>
        </article>)}</div>
        {matches.length > limit && <button className="button subtle more" onClick={() => setLimit(limit + 12)}>{t('showFacilities')} <ArrowRight size={17} /></button>}
      </>}
  </section>
}
