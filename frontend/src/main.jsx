import { createRoot } from 'react-dom/client'
import { useEffect, useMemo, useRef, useState } from 'react'
import {
  Ambulance, ArrowDown, ArrowRight, ArrowUpRight, Bookmark, CircleCheck, Compass, FileText,
  GitCompareArrows, HeartPulse, Languages, MapPin, Plus, Search, ShieldPlus, Sparkles, Wifi, WifiOff, X,
} from 'lucide-react'
import Guide, { SchemeSource } from './Guide.jsx'
import { Assistant, Care, PanelHeader, PdfTools } from './Tools.jsx'
import { localRead, localWrite, schemeTitle, searchSchemes, sectionText, translator } from './content.js'
import './style.css'

const nav = [['explore', Compass], ['saved', Bookmark], ['compare', GitCompareArrows], ['assistant', Sparkles], ['pdf', FileText], ['care', MapPin]]
const preferredRegions = ['Andhra Pradesh', 'National']
const spotlight = ['Ayushman Bharat PM-JAY (National Health Cover)', 'Poshan Abhiyaan', 'Ayushman Bharat Health Account (ABHA)']
const regionText = (value, t) => value === 'National' ? t('national') : value

function Header({ lang, setLang, t, panel, go, online, ready, saved, comparison }) {
  const status = !online ? 'offline' : ready ? 'offlineReady' : 'online'
  const Signal = online ? Wifi : WifiOff
  return <header className="site-header">
    <div className="header-inner">
      <a className="brand" href="#explore" onClick={event => { event.preventDefault(); go('explore', false); window.scrollTo(0, 0) }}>
        <img alt="" src="/studio/mark.svg" width="42" height="42" />
        <span><strong>SmartGovAI</strong><small>{t('subtitle')}</small></span>
      </a>
      <nav className="main-nav" aria-label="SmartGovAI">
        {nav.map(([id, Icon]) => <button key={id} aria-current={panel === id ? 'page' : undefined} onClick={() => go(id)}>
          <Icon size={15} /><span>{t(id)}</span>{((id === 'saved' && saved.length) || (id === 'compare' && comparison.length)) ? <b>{id === 'saved' ? saved.length : comparison.length}</b> : null}
        </button>)}
      </nav>
      <div className="header-tools">
        <span className="status" title={t(status)} aria-label={t(status)} role="status"><Signal size={17} /><span>{t(status)}</span></span>
        <button className="language" aria-label={lang === 'te' ? 'Switch to English' : 'తెలుగుకు మార్చండి'} onClick={() => setLang(lang === 'te' ? 'en' : 'te')}><Languages size={17} /><span lang={lang === 'te' ? 'en' : 'te'}>{lang === 'te' ? 'English' : 'తెలుగు'}</span></button>
      </div>
    </div>
  </header>
}

function Orbit() {
  return <svg className="orbit-art" viewBox="0 0 470 420" fill="none" aria-hidden="true">
    <defs>
      <radialGradient id="orb-fill"><stop stopColor="#386953" stopOpacity=".94"/><stop offset="1" stopColor="#1e4136"/></radialGradient>
      <linearGradient id="orb-outline" x1="0" x2="1" y1="0" y2="1"><stop stopColor="#b0c998"/><stop offset="1" stopColor="#386953"/></linearGradient>
      <linearGradient id="shield-tone" x1="0" x2="1" y1="0" y2="1"><stop stopColor="#477459"/><stop offset="1" stopColor="#244b3d"/></linearGradient>
    </defs>
    <circle cx="235" cy="211" r="176" stroke="#88aa91" strokeOpacity=".25" strokeDasharray="1 7"/>
    <circle cx="235" cy="211" r="154" stroke="#88aa91" strokeOpacity=".22"/>
    <circle cx="235" cy="211" r="128" fill="url(#orb-fill)" stroke="url(#orb-outline)" strokeOpacity=".6"/>
    <circle cx="235" cy="211" r="107" stroke="#a7c49d" strokeOpacity=".22"/>
    <path d="M235 63v296M80 211h310M119 107l232 208M120 315l231-208" stroke="#9db89b" strokeOpacity=".15" strokeDasharray="4 7"/>
    <g className="orbit-track">
      <circle cx="235" cy="35" r="6" fill="#e7b77e"/>
      <circle cx="390" cy="295" r="4" fill="#acd0b0"/>
      <circle cx="95" cy="315" r="3.5" fill="#e7b77e"/>
      <circle cx="65" cy="164" r="2.5" fill="#acd0b0"/>
    </g>
    <path d="M152 197h43l12-21 18 59 16-34h72" stroke="#d4e1be" strokeOpacity=".38" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
    <g className="shield-float">
      <path d="M235 140c19 13 38 19 61 23v46c0 34-23 58-61 76-38-18-61-42-61-76v-46c23-4 42-10 61-23Z" fill="url(#shield-tone)" stroke="#d8dba1" strokeWidth="1.7"/>
      <path d="M235 154c14 9 32 15 47 19v36c0 27-16 46-47 62-31-16-47-35-47-62v-36c15-4 33-10 47-19Z" stroke="#d6e6c2" strokeOpacity=".36"/>
      <path d="M235 190v45m-22-22h44" stroke="#f3d499" strokeWidth="7" strokeLinecap="round"/>
    </g>
    <path d="M90 93h15m-7.5-7.5v15m273 237h15m-7.5-7.5v15M352 74h13m-6.5-6.5v13M89 331h9m-4.5-4.5v9" stroke="#a9c3a3" strokeOpacity=".65" strokeLinecap="round"/>
  </svg>
}

function Hero({ t, go, browse, stats }) {
  return <>
    <section className="hero">
      <div className="hero-copy">
        <div className="hero-kicker"><span />{t('ap')}</div>
        <h1>{t('heroA')}<br /><em>{t('heroB')}</em></h1>
        <p>{t('intro')}</p>
        <div className="action-row">
          <button className="button hero-primary" onClick={browse}>{t('browse')} <ArrowDown size={18} /></button>
          <button className="button hero-secondary" onClick={() => go('assistant')}><Sparkles size={17} /> {t('ask')}</button>
        </div>
      </div>
      <div className="hero-visual"><Orbit /></div>
      <div className="quick-card">
        <span className="eyebrow">{t('quick')}</span>
        <a href="tel:108"><span className="quick-icon"><Ambulance size={19} /></span><span>{t('ambulance')}</span><strong>108</strong><ArrowUpRight size={15} /></a>
        <a href="tel:104"><span className="quick-icon"><HeartPulse size={19} /></span><span>{t('healthline')}</span><strong>104</strong><ArrowUpRight size={15} /></a>
      </div>
    </section>
    <div className="metrics">
      {[[ShieldPlus, stats.count, 'program'], [MapPin, stats.regions, 'coverage'], [Languages, 2, 'languages']].map(([Icon, value, key]) =>
        <div key={key}><span className="metric-icon"><Icon size={20} /></span><strong>{value ?? '—'}</strong><span>{t(key)}</span></div>)}
    </div>
  </>
}

function SchemeCard({ scheme, lang, t, onOpen, selected, pinned, toggleSave, toggleCompare, index }) {
  const Icon = [ShieldPlus, HeartPulse, FileText][index % 3]
  const title = schemeTitle(scheme, lang)
  return <article className="scheme-card">
    <div className="card-top"><div className={'card-icon tint-' + (index % 3)}><Icon size={22} /></div>
      <button className="icon-button save-button" title={t(pinned ? 'unsave' : 'save')} aria-label={t('save') + ': ' + title} aria-pressed={pinned} onClick={() => toggleSave(scheme.id)}><Bookmark size={19} fill={pinned ? 'currentColor' : 'none'} /></button>
    </div>
    <div className="card-body">
      <span className="pill">{regionText(scheme.region, t)}</span>
      <h3>{title}</h3>
      <p>{sectionText(scheme, 'description', lang) || sectionText(scheme, 'benefits', lang)}</p>
    </div>
    <div className="card-footer">
      <button className="text-button" aria-label={t('details') + ': ' + title} onClick={() => onOpen(scheme)}>{t('details')} <ArrowUpRight size={16} /></button>
      <button className="icon-button compare-button" title={t(selected ? 'removeCompare' : 'addCompare')} aria-label={t('compare') + ': ' + title} aria-pressed={selected} onClick={() => toggleCompare(scheme.id)}>{selected ? <CircleCheck size={19} /> : <Plus size={20} />}</button>
    </div>
  </article>
}

function Comparison({ items, lang, t, onOpen, toggleCompare }) {
  return <section className="work-panel">
    <PanelHeader tag="02 / SMARTGOVAI" title={t('compare')} desc={t(items.length < 2 ? 'compareEmpty' : 'guideDisclaimer')} />
    {!!items.length && <div className="comparison-grid">
      {items.map(scheme => <article className="tool-card comparison-card" key={scheme.id}>
        <div className="card-top"><span className="pill">{regionText(scheme.region, t)}</span><button className="icon-button" aria-label={t('removeCompare') + ': ' + schemeTitle(scheme, lang)} onClick={() => toggleCompare(scheme.id)}><X size={18} /></button></div>
        <h3>{schemeTitle(scheme, lang)}</h3>
        {['benefits', 'eligibility', 'documents', 'steps'].map(key => <section key={key}><h4>{t(key)}</h4><p>{sectionText(scheme, key, lang) || t('notListed')}</p></section>)}
        <SchemeSource {...{ scheme, t }} />
        <button className="text-button" onClick={() => onOpen(scheme)}>{t('details')} <ArrowUpRight size={16} /></button>
      </article>)}
    </div>}
  </section>
}

function useStored(key, initial, onError) {
  const [value, setValue] = useState(() => localRead(key, initial))
  return [value, next => {
    setValue(next)
    if (!localWrite(key, next)) onError()
  }]
}

function App() {
  const [notice, setNotice] = useState('')
  const storageError = () => setNotice('storageError')
  const [lang, setLang] = useStored('lang', 'te', storageError)
  const [saved, setSaved] = useStored('saved', [], storageError)
  const [comparison, setComparison] = useStored('comparison', [], storageError)
  const [checks, setChecks] = useStored('checks', {}, storageError)
  const [answers, setAnswers] = useStored('answers', {}, storageError)
  const [online, setOnline] = useState(navigator.onLine)
  const [ready, setReady] = useState(false)
  const [status, setStatus] = useState('loading')
  const [attempt, retry] = useState(0)
  const [schemes, setSchemes] = useState([])
  const [query, setQuery] = useState('')
  const [region, setRegion] = useState('')
  const [limit, setLimit] = useState(9)
  const [panel, setPanel] = useState(() => nav.some(([id]) => id === location.hash.slice(1)) ? location.hash.slice(1) : 'explore')
  const [detail, open] = useState(null)
  const main = useRef(null)
  const catalog = useRef(null)
  const t = translator(lang)
  useEffect(() => { document.documentElement.lang = lang === 'en' ? 'en' : 'te' }, [lang])
  useEffect(() => {
    const update = () => setOnline(navigator.onLine)
    const updatePanel = () => {
      const key = location.hash.slice(1)
      setPanel(nav.some(([id]) => id === key) ? key : 'explore')
      open(null)
    }
    addEventListener('online', update); addEventListener('offline', update); addEventListener('hashchange', updatePanel)
    const service = navigator.serviceWorker
    if (service) service.register('/studio/sw.js').then(() => service.ready).then(() => setReady(true)).catch(() => {})
    return () => { removeEventListener('online', update); removeEventListener('offline', update); removeEventListener('hashchange', updatePanel) }
  }, [])
  useEffect(() => {
    const controller = new AbortController()
    const timeout = setTimeout(() => controller.abort('timeout'), 15_000)
    fetch('/studio/catalog.json', { signal: controller.signal })
      .then(response => { if (!response.ok) throw new Error(); return response.json() })
      .then(data => { if (!Array.isArray(data.schemes)) throw new Error(); setSchemes(data.schemes); setStatus('') })
      .catch(() => { if (!controller.signal.aborted || controller.signal.reason === 'timeout') setStatus('loadError') })
      .finally(() => clearTimeout(timeout))
    return () => { clearTimeout(timeout); controller.abort() }
  }, [attempt])

  function go(next, focus = true) {
    setNotice('')
    setPanel(next)
    if (location.hash !== '#' + next) history.pushState(null, '', '#' + next)
    if (focus) requestAnimationFrame(() => { main.current.focus({ preventScroll: true }); main.current.scrollIntoView() })
  }
  function browse() {
    go('explore', false)
    requestAnimationFrame(() => { catalog.current?.focus({ preventScroll: true }); catalog.current?.scrollIntoView() })
  }
  const regions = useMemo(() => [...new Set(schemes.map(item => item.region).filter(Boolean))].sort((a, b) => {
    const rank = value => preferredRegions.includes(value) ? preferredRegions.indexOf(value) : preferredRegions.length
    return rank(a) - rank(b) || a.localeCompare(b)
  }), [schemes])
  const results = useMemo(() => {
    const ranked = searchSchemes(schemes.filter(scheme => !region || scheme.region === region), query)
    if (query.trim() || region) return ranked
    const rank = scheme => spotlight.includes(scheme.name) ? spotlight.indexOf(scheme.name) : spotlight.length + (scheme.region === 'Andhra Pradesh' ? 0 : scheme.region === 'National' ? 1 : 2)
    return [...ranked].sort((a, b) => rank(a) - rank(b))
  }, [schemes, region, query])
  function toggleSave(id) {
    setNotice('')
    setSaved(saved.includes(id) ? saved.filter(item => item !== id) : [...saved, id])
  }
  function toggleCompare(id) {
    setNotice('')
    if (!comparison.includes(id) && comparison.length === 3) return setNotice('compareLimit')
    setComparison(comparison.includes(id) ? comparison.filter(item => item !== id) : [...comparison, id])
  }
  function cards(items) {
    return <div className="cards">{items.map((scheme, index) => <SchemeCard key={scheme.id} {...{ scheme, index, lang, t, toggleSave, toggleCompare }}
      selected={comparison.includes(scheme.id)} pinned={saved.includes(scheme.id)} onOpen={open} />)}</div>
  }
  const loadNotice = <div className="empty" role="status"><p>{t(status)}</p>
    {status === 'loadError' && <button className="button subtle" onClick={() => { setStatus('loading'); retry(attempt + 1) }}>{t('retry')}</button>}</div>
  const pick = ids => ids.map(id => schemes.find(scheme => scheme.id === id)).filter(Boolean)

  return <>
    <div className="screen-app">
      <a className="skip" href="#main" onClick={event => { event.preventDefault(); main.current.focus() }}>{t('skip')}</a>
      <Header {...{ lang, setLang, t, panel, go, online, ready, saved, comparison }} />
      <main id="main" ref={main} tabIndex={-1}>
        {panel === 'explore' && <>
          <Hero {...{ t, go, browse }} stats={{ count: status ? null : schemes.length, regions: status ? null : regions.length }} />
          <section className="catalog work-panel" tabIndex={-1} ref={catalog}>
            <div className="catalog-head">
              <PanelHeader tag={t('choose')} title={t('catalog')} desc={t('catalogDesc')} />
              {comparison.length > 0 && <button className="button subtle" onClick={() => go('compare')}><GitCompareArrows size={18} /> {t('compare')} ({comparison.length})</button>}
            </div>
            {status ? loadNotice : <>
              <div className="filter-row">
                <label className="search-box"><Search size={20} /><input type="search" aria-label={t('search')} placeholder={t('placeholder')} value={query} onChange={event => { setQuery(event.target.value); setLimit(9) }} /></label>
                <select aria-label={t('region')} value={region} onChange={event => { setRegion(event.target.value); setLimit(9) }}>
                  <option value="">{t('anyRegion')}</option>{regions.map(item => <option value={item} key={item}>{regionText(item, t)}</option>)}
                </select>
              </div>
              <p className="count" aria-live="polite">{results.length} {t('results')}</p>
              {results.length ? cards(results.slice(0, limit)) : <div className="empty"><Search size={24} /><p>{t('noResults')}</p></div>}
              {results.length > limit && <button className="button subtle more" onClick={() => setLimit(limit + 9)}>{t('more')} <ArrowDown size={17} /></button>}
            </>}
          </section>
        </>}
        {panel === 'saved' && <section className="work-panel">
          <PanelHeader tag={t('localOnly')} title={t('saved')} desc={saved.length ? '' : t('savedEmpty')} />
          {status ? loadNotice : cards(pick(saved))}
        </section>}
        {panel === 'compare' && (status ? loadNotice : <Comparison {...{ lang, t, toggleCompare }} items={pick(comparison)} onOpen={open} />)}
        {panel === 'assistant' && (status ? loadNotice : <Assistant {...{ schemes, lang, t, online, open }} />)}
        {panel === 'pdf' && <PdfTools {...{ t, online, browse, open }} />}
        {panel === 'care' && <Care {...{ t, online }} />}
      </main>
      <footer className="site-footer">
        <span><img src="/studio/mark.svg" alt="" width="31" height="31" /><strong>SmartGovAI</strong></span>
        <p>{t('unofficial')}</p><a href="/classic/">{t('classic')} <ArrowUpRight size={15} /></a>
      </footer>
      {notice && <div className="toast" role="status">{t(notice)}<button className="icon-button" aria-label={t('close')} onClick={() => setNotice('')}><X size={18} /></button></div>}
    </div>
    {detail && <Guide key={detail.id} scheme={detail} {...{ lang, t }} onClose={() => open(null)}
      checks={checks[detail.id] || {}} answers={answers[detail.id] || {}}
      setCheck={(index, value) => setChecks({ ...checks, [detail.id]: { ...checks[detail.id], [index]: value } })}
      setAnswer={(index, value) => setAnswers({ ...answers, [detail.id]: { ...answers[detail.id], [index]: value } })}
      clearAnswers={() => { const next = { ...answers }; delete next[detail.id]; setAnswers(next) }} />}
  </>
}

createRoot(document.getElementById('root')).render(<App />)
