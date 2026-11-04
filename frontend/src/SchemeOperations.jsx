import { ChevronDown } from 'lucide-react'
import { localized, officialUrl, sectionText } from './content.js'

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

export default function SchemeOperations({ scheme, lang, t, checks, setCheck }) {
  const data = scheme.operations
  const eligibility = fieldRows(data?.eligibility, eligibilityFields, lang)
  const benefits = fieldRows(data?.benefits, benefitsFields, lang)
  const application = fieldRows(data?.application_process, applicationFields, lang)
  const details = (items, fallback) => items?.length
    ? items.map(item => localized(item, lang)).filter(Boolean)
    : (sectionText(scheme, fallback, lang) || '').split(/\n+/).map(line => line.trim()).filter(Boolean)
  const criteria = details(data?.eligibility?.criteria, 'eligibility')
  const payouts = details(data?.benefits?.details, 'benefits')
  const steps = details(data?.application_process?.steps, 'steps')
  const amount = localized(data?.benefits?.coverage_amount, lang)
  const cashless = data?.benefits?.cashless
  const portal = officialUrl(data?.application_process?.official_url)
  const source = officialUrl(scheme.source?.url)
  const documents = data ? data.required_documents.map(doc => ({
    key: 'ops:' + (doc.name.en || doc.name.te), name: localized(doc.name, lang),
    purpose: localized(doc.purpose, lang), mandatory: doc.mandatory,
  })) : (scheme.documents || []).map((doc, key) => ({
    key, name: localized(doc, lang), mandatory: doc.optional ? false : null,
  }))
  const documentNote = sectionText(scheme, 'documents', lang)
  const missing = <p className="operation-missing">{t('operationsMissing')}{source && <> <a href={source} target="_blank" rel="noreferrer">{t('source')}</a></>}</p>

  return <div className="scheme-operations">
    <details name={scheme.id + '-operations'}>
      <summary>{t('eligibility')}<ChevronDown size={16} aria-hidden="true" /></summary>
      <div className="operation-content">
        <Facts rows={eligibility} t={t} /><Lines text={criteria} />
        {!eligibility.length && !criteria.length && missing}
      </div>
    </details>
    <details name={scheme.id + '-operations'}>
      <summary>{t('requiredDocuments')}<ChevronDown size={16} aria-hidden="true" /></summary>
      <div className="operation-content">
        {documents.length > 0 && <ul className="operation-checks">
          {documents.map(doc => <li key={doc.key}><label>
            <input type="checkbox" checked={Boolean(checks[doc.key])} onChange={event => setCheck(doc.key, event.target.checked)} />
            <span>{doc.name}{doc.mandatory != null && <small>{t(doc.mandatory ? 'required' : 'optional')}</small>}
              {doc.purpose && <small>{doc.purpose}</small>}
            </span>
          </label></li>)}
        </ul>}
        {documentNote && <p>{documentNote}</p>}
        {documents.length > 0 && <p>{t('checklistNote')}</p>}
        {!documents.length && !documentNote && missing}
      </div>
    </details>
    <details name={scheme.id + '-operations'}>
      <summary>{t('benefits')}<ChevronDown size={16} aria-hidden="true" /></summary>
      <div className="operation-content">
        {amount && <span className="pill operation-amount">{amount}</span>}
        {cashless != null && <p>{t(cashless ? 'cashlessAvailable' : 'cashlessUnavailable')}</p>}
        <Facts rows={benefits} t={t} /><Lines text={payouts} />
        {!amount && cashless == null && !benefits.length && !payouts.length && missing}
      </div>
    </details>
    <details name={scheme.id + '-operations'}>
      <summary>{t('steps')}<ChevronDown size={16} aria-hidden="true" /></summary>
      <div className="operation-content">
        <Facts rows={application} t={t} /><Lines text={steps} ordered />
        {portal && <a href={portal} target="_blank" rel="noreferrer">{t('applicationPortal')}</a>}
        {!portal && source && (application.length > 0 || steps.length > 0) &&
          <a href={source} target="_blank" rel="noreferrer">{t('source')}</a>}
        {!portal && !application.length && !steps.length && missing}
      </div>
    </details>
  </div>
}
