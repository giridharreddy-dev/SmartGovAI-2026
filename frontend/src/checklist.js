export function checklistForScheme(scheme) {
  if (Array.isArray(scheme.checklist)) {
    return scheme.checklist.map(doc => ({ ...doc, ...doc.name, key: 'doc:' + doc.id }))
  }
  // Cached catalog responses from before the ID rollout still work offline.
  if (scheme.operations?.required_documents?.length) {
    return scheme.operations.required_documents.map(doc => ({
      ...doc, ...doc.name, key: 'ops:' + (doc.name.en || doc.name.te),
    }))
  }
  return (scheme.documents || []).map((doc, index) => ({
    ...doc, key: String(index), mandatory: doc.optional ? false : null,
  }))
}

export function reconcileChecklist(checks = {}, aliases = {}) {
  const merged = { ...checks }
  for (const [oldKey, id] of Object.entries(aliases)) {
    if (!Object.hasOwn(checks, oldKey)) continue
    const key = 'doc:' + id
    if (!Object.hasOwn(merged, key)) merged[key] = Boolean(checks[oldKey])
    delete merged[oldKey]
  }
  return merged
}
