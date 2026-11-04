import { ChevronDown } from 'lucide-react'
import { baselineSectionText, localized, officialUrl, sectionText } from './content.js'
import { checklistForScheme } from './checklist.js'

const eligibilityFields = ['target_group', 'age_range', 'income_ceiling', 'residence', 'caste_category', 'exclusions']
const benefitsFields = ['coverage_type', 'subsidy_percentage', 'disbursement']
const applicationFields = ['mode', 'nodal_agency', 'offline_office', 'verification']

function fieldRows(data, keys, lang) {
  return keys.map(key => {
    const value = data?.[key]
    const content = Array.isArray(value) ? value.map(item => localized(item, lang)).filter(Boolean) : [localized(value, lang)].filter(Boolean)
    return { key, content }
  }).filter(row => row.content.length)
}

function Facts({ rows, t }) {
  if (!rows.length) return null
  return <dl>{rows.map(({ key, content }) => <div key={key}>
    <dt>{t(key)}</dt>
    <dd>{content.length === 1 ? content[0] : <ul>{content.map((line, i) => <li key={i}>{line}</li>)}</ul>}</dd>
  </div>)}</dl>
}

function Lines({ text, ordered = false }) {
  const Tag = ordered ? 'ol' : 'ul'
  return text.length ? <Tag>{text.map((line, i) => <li key={i}>{line}</li>)}</Tag> : null
}

function BlockSummary({ label, status, t }) {
  return <summary><span>{t(label)}</span>
    <span className="operation-state" data-status={status}>{t('section.' + status)}</span>
    <ChevronDown size={16} aria-hidden="true" />
  </summary>
}

export default function SchemeOperations({ scheme, lang, t, checks, setCheck }) {
  const data = scheme.operations
  const eligibility = fieldRows(data?.eligibility, eligibilityFields, lang)
  const benefits = fieldRows(data?.benefits, benefitsFields, lang)
  const application = fieldRows(data?.application_process, applicationFields, lang)
  const details = (items, fallback, hasTyped) => items?.length
    ? items.map(item => localized(item, lang)).filter(Boolean)
    : (hasTyped ? '' : baselineSectionText(scheme, fallback, lang) || '').split(/\n+/).map(line => line.trim()).filter(Boolean)
  const amount = localized(data?.benefits?.coverage_amount, lang)
  const cashless = data?.benefits?.cashless
  const portal = officialUrl(data?.application_process?.official_url)
  const source = officialUrl(scheme.source?.url)
  const criteria = details(data?.eligibility?.criteria, 'eligibility', eligibility.length)
  const payouts = details(data?.benefits?.details, 'benefits', amount || cashless != null || benefits.length)
  const steps = details(data?.application_process?.steps, 'steps', portal || application.length)
  const documents = checklistForScheme(scheme)
  const status = key => scheme.section_statuses?.[key] || 'verification_pending'
  const docsStatus = status('required_documents')
  const components = scheme.programme_components || []
  const documentNote = sectionText(scheme, 'documents', lang)
  const missing = <p className="operation-missing">{t('operationsMissing')}{source && <> <a href={source} target="_blank" rel="noreferrer">{t('source')}</a></>}</p>

  return <div className="scheme-operations">
    <details name={scheme.id + '-operations'}>
      <BlockSummary label="eligibility" status={status('eligibility')} t={t} />
      <div className="operation-content">
        <Facts rows={eligibility} t={t} /><Lines text={criteria} />
        {!eligibility.length && !criteria.length && missing}
      </div>
    </details>
    <details name={scheme.id + '-operations'}>
      <BlockSummary label="requiredDocuments" status={docsStatus} t={t} />
      <div className="operation-content">
        {documents.length > 0 && <ul className="operation-checks">
          {documents.map(doc => <li key={doc.key}><label>
            <input type="checkbox" checked={Boolean(checks[doc.key])} onChange={event => setCheck(doc.key, event.target.checked)} />
            <span>{localized(doc, lang)}{doc.status === 'optional_at_initial_verification'
                ? <small>{t('optionalAtIntake')}</small>
                : doc.status === 'facility_specific'
                  ? <small>{t('confirmWithFacility')}</small>
                  : doc.verification_status === 'verification_pending'
                    ? <small>{t('section.verification_pending')}</small>
                    : doc.mandatory != null && <small>{t(doc.mandatory ? 'required' : 'optional')}</small>}
              {doc.purpose && <small>{localized(doc.purpose, lang)}</small>}
            </span>
          </label></li>)}
        </ul>}
        {documentNote && <p>{documentNote}</p>}
        {[...new Set(documents.map(doc => officialUrl(doc.source_url)).filter(Boolean))].map(url =>
          <a key={url} href={url} target="_blank" rel="noreferrer">{t('source')}</a>)}
        {documents.length > 0 && <p>{t('checklistNote')}</p>}
        {(docsStatus !== 'verified' || !documents.length) && <p className="operation-missing">
          {t(docsStatus === 'official_source_unspecified' ? 'documentsUnspecified' : 'documentsPending')}
          {source && <> <a href={source} target="_blank" rel="noreferrer">{t('source')}</a></>}
        </p>}
      </div>
    </details>
    <details name={scheme.id + '-operations'}>
      <BlockSummary label="benefits" status={status('benefits')} t={t} />
      <div className="operation-content">
        {amount && <span className="pill operation-amount">{amount}</span>}
        {cashless != null && <p>{t(cashless ? 'cashlessAvailable' : 'cashlessUnavailable')}</p>}
        <Facts rows={benefits} t={t} /><Lines text={payouts} />
        {!amount && cashless == null && !benefits.length && !payouts.length && missing}
      </div>
    </details>
    <details name={scheme.id + '-operations'}>
      <BlockSummary label="steps" status={status('application_process')} t={t} />
      <div className="operation-content">
        <Facts rows={application} t={t} /><Lines text={steps} ordered />
        {portal && <a href={portal} target="_blank" rel="noreferrer">{t('applicationPortal')}</a>}
        {!portal && source && (application.length > 0 || steps.length > 0) &&
          <a href={source} target="_blank" rel="noreferrer">{t('source')}</a>}
        {!portal && !application.length && !steps.length && missing}
      </div>
    </details>
    {components.length > 0 && <details name={scheme.id + '-operations'}>
      <summary><span>{t('programmeComponents')}</span><ChevronDown size={16} aria-hidden="true" /></summary>
      <div className="operation-content">
        {components.map(item => <section key={item.id}>
          <h4>{localized(item.title, lang)}</h4>
          <p>{localized(item.summary, lang)}</p>
          <a href={officialUrl(item.source_url)} target="_blank" rel="noreferrer">{t('source')}</a>
        </section>)}
      </div>
    </details>}
  </div>
}
