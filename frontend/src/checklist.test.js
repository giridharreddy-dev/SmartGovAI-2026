import assert from 'node:assert/strict'
import test from 'node:test'
import { checklistForScheme, reconcileChecklist } from './checklist.js'

test('saved checks follow stable IDs when documents are renamed or reordered', () => {
  const scheme = {
    checklist: [
      { id: 'new', name: { en: 'New document' } },
      { id: 'identity', name: { en: 'Renamed identity proof' } },
      { id: 'bank', name: { en: 'Bank details' } },
    ],
    checklist_aliases: { '0': 'bank', 'ops:Identity proof': 'identity' },
  }
  const old = { '0': true, 'ops:Identity proof': true, unknown: true, 'doc:bank': false }
  const checked = reconcileChecklist(old, scheme.checklist_aliases)
  assert.deepEqual(checked, { 'doc:bank': false, 'doc:identity': true, unknown: true })
  assert.deepEqual(checklistForScheme(scheme).map(doc => Boolean(checked[doc.key])), [false, true, false])
  assert.deepEqual(reconcileChecklist(checked, scheme.checklist_aliases), checked)
})
