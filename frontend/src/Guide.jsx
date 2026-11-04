import { useEffect, useId, useRef, useState } from 'react'
import { ArrowLeft, ArrowUpRight, Check, CircleHelp, FileText, Printer, Volume2, VolumeX, X } from 'lucide-react'
import { localized, officialUrl, sections, schemeTitle, sectionText } from './content.js'
import { checklistForScheme } from './checklist.js'

export function SchemeSource({ scheme, t }) {
  const url = officialUrl(scheme.source?.url)
  return <div className="source">
    <span>{scheme.source?.updated ? <>{t('updated')}: {scheme.source.updated}</> :
      scheme.source?.reviewed && <>{t('reviewed')}: {scheme.source.reviewed}</>}</span>
    {url ? <a href={url} target="_blank" rel="noreferrer">{scheme.source.label || t('source')} <ArrowUpRight size={15} aria-hidden="true" /></a>
      : <span>{t('sourceMissing')}</span>}
  </div>
}

export function DocumentSections({ scheme, lang, t }) {
  return <div className="document-sections">{sections.map(key => {
    const value = sectionText(scheme, key, lang)
    return value && <section key={key}><h3>{t(key)}</h3><p>{value}</p></section>
  })}</div>
}

function Printable({ scheme, lang, t, checks }) {
  const documents = checklistForScheme(scheme)
  return <article className="print-sheet" aria-label={t('guide')}>
    <header className="print-mast"><img src="/studio/mark.svg" width="42" height="42" alt="" /><div><strong>SmartGovAI</strong><span>{t('guide')}</span></div></header>
    <div className="print-title">
      <span>{scheme.region === 'National' ? t('national') : scheme.region}</span>
      <h2 lang={lang === 'te' && scheme.directoryEntry && !scheme.nameTe ? 'en' : undefined}>{schemeTitle(scheme, lang)}</h2>
    </div>
    <DocumentSections {...{ scheme, lang, t }} />
    {documents.length > 0 && <section className="print-checks">
      <h3>{t('checklist')}</h3>
      <ul>{documents.map(doc => <li key={doc.key}>
        <span className="print-box" aria-hidden="true">{checks[doc.key] ? '✓' : ''}</span>
        {localized(doc, lang)} {doc.verification_status === 'verification_pending' && <small>({t('section.verification_pending')})</small>}
        {doc.mandatory === false && <small>({t('optional')})</small>}
      </li>)}</ul>
    </section>}
    {scheme.source && <SchemeSource {...{ scheme, t }} />}
    <footer className="print-foot">{t(scheme.ai ? 'pdfNotice' : scheme.directoryEntry ? 'officialDetails' : 'guideDisclaimer')}</footer>
  </article>
}

export default function Guide({ scheme, lang, t, checks, answers, setCheck, setAnswer, clearAnswers, onClose }) {
  const dialog = useRef(null)
  const sheetTop = useRef(null)
  const previewButton = useRef(null)
  const returningFromPreview = useRef(false)
  const audio = useRef(null)
  const mounted = useRef(true)
  const playing = useRef(null)
  const [preview, setPreview] = useState(false)
  const [sound, setSound] = useState('idle')
  const titleId = useId()
  const documents = checklistForScheme(scheme)
  const recording = scheme.recordings?.[lang] ||
    ((scheme.audioLanguage || 'te') === lang ? scheme.audio : null)
  useEffect(() => {
    mounted.current = true
    dialog.current.showModal()
    return () => {
      mounted.current = false
      playing.current = null
      audio.current?.pause()
      window.speechSynthesis?.cancel()
    }
  }, [])
  useEffect(() => {
    if (preview) sheetTop.current?.focus()
    else if (returningFromPreview.current) {
      returningFromPreview.current = false
      previewButton.current?.focus()
    }
  }, [preview])

  function listen() {
    if (playing.current) {
      playing.current = null
      audio.current?.pause()
      window.speechSynthesis?.cancel()
      setSound('idle')
      return
    }
    const attempt = {}
    playing.current = attempt
    const active = () => mounted.current && playing.current === attempt
    const done = state => {
      if (!active()) return
      playing.current = null
      setSound(state)
    }
    function speak() {
      if (!active()) return
      if (!('speechSynthesis' in window) || !('SpeechSynthesisUtterance' in window)) return done('error')
      const voice = speechSynthesis.getVoices().find(voice => voice.lang.startsWith(lang) && voice.localService)
      if (!voice) return done('error')
      const title = lang === 'te' ? scheme.nameTe : scheme.name
      const content = scheme[lang]
      const msg = new SpeechSynthesisUtterance([title, content?.description, content?.benefits].filter(Boolean).join('. '))
      if (!msg.text) return done('error')
      msg.lang = lang === 'te' ? 'te-IN' : 'en-IN'
      msg.voice = voice
      msg.onend = () => done('idle')
      msg.onerror = () => done('error')
      speechSynthesis.speak(msg)
    }
    setSound('playing')
    if (recording) {
      audio.current = new Audio(recording)
      audio.current.addEventListener('ended', () => done('idle'), { once: true })
      audio.current.play().catch(speak)
    } else speak()
  }

  return <dialog ref={dialog} className={preview ? 'guide-dialog preview-mode' : 'guide-dialog'} aria-labelledby={titleId} onClose={onClose}
    onClick={event => { if (event.target === event.currentTarget) dialog.current.close() }}>
    <div className="dialog-inner">
      <div className="dialog-bar">
        {preview ? <button className="button subtle" onClick={() => { returningFromPreview.current = true; setPreview(false) }}><ArrowLeft size={16} /> {t('goBack')}</button> : <span className="eyebrow"><FileText size={15} /> SmartGovAI</span>}
        <button className="icon-button" aria-label={t('close')} onClick={() => dialog.current.close()}><X size={22} /></button>
      </div>
      {preview ? <>
        <div className="preview-actions">
          <div><h2 id={titleId} tabIndex={-1} ref={sheetTop}>{t('guide')}</h2><p>{t('printNote')}</p></div>
          <button className="button primary" onClick={async () => { await document.fonts?.ready; window.print() }}><Printer size={17} /> {t('print')}</button>
        </div>
        <Printable {...{ scheme, lang, t, checks }} />
      </> : <>
        <div className="detail-title">
          {scheme.region && <span className="pill">{scheme.region === 'National' ? t('national') : scheme.region}</span>}
          <h2 id={titleId} lang={lang === 'te' && scheme.directoryEntry && !scheme.nameTe ? 'en' : undefined}>{schemeTitle(scheme, lang)}</h2>
          {scheme.ai && <p role="note">{t('pdfNotice')}</p>}
          <div className="action-row">
            <button ref={previewButton} className="button primary" onClick={() => setPreview(true)}><FileText size={17} /> {t('preview')}</button>
            <button className="button subtle" onClick={listen}>{sound === 'playing' ? <VolumeX size={17} /> : <Volume2 size={17} />}{t(sound === 'playing' ? 'stop' : 'listen')}</button>
          </div>
          {sound === 'error' && <p role="status">{t('speechUnavailable')}</p>}
        </div>
        <DocumentSections {...{ scheme, lang, t }} />
        {documents.length > 0 && <section className="detail-panel">
          <h3><Check size={20} /> {t('checklist')}</h3>
          <p>{t('checklistNote')}</p>
          <progress value={documents.filter(doc => checks[doc.key]).length} max={documents.length} aria-label={t('checklist')} />
          <div className="checklist">{documents.map(doc => <label key={doc.key}><input type="checkbox" checked={!!checks[doc.key]} onChange={event => setCheck(doc.key, event.target.checked)} />
            {localized(doc, lang)} {doc.verification_status === 'verification_pending' && <small>({t('section.verification_pending')})</small>}
            {doc.mandatory === false && <small>({t('optional')})</small>}
          </label>)}</div>
        </section>}
        {scheme.directoryEntry ? <>
          <p className="detail-panel">{t('officialDetails')}</p>
          <SchemeSource {...{ scheme, t }} />
        </> : !scheme.ai && <>
          <section className="detail-panel">
            <h3><CircleHelp size={20} /> {t('selfCheck')}</h3>
            <p>{t('selfCheckNote')}</p>
            {scheme.questions.length ? <>
              {scheme.questions.map((question, index) => <fieldset key={index}><legend>{localized(question, lang)}</legend>
                <div className="radio-row">{['yes', 'no', 'unsure'].map(answer => <label key={answer}>
                  <input type="radio" name={`${titleId}-q${index}`} checked={answers[index] === answer} onChange={() => setAnswer(index, answer)} />{t(answer)}
                </label>)}</div>
              </fieldset>)}
              {Object.keys(answers).length > 0 && <button className="button subtle" onClick={clearAnswers}>{t('reset')}</button>}
            </> : <p>{t('noQuestions')}</p>}
          </section>
          <SchemeSource {...{ scheme, t }} />
        </>}
      </>}
    </div>
  </dialog>
}
