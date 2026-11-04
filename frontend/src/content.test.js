import assert from 'node:assert/strict'
import test from 'node:test'
import { mergeSchemeMatches, officialUrl, searchSchemes, sectionText } from './content.js'

const catalog = [
  { name: 'Poshan Abhiyaan', nameTe: 'పోషణ్ అభియాన్', region: 'National', keywords: ['nutrition'], en: { benefits: 'Supports child nutrition' } },
  { name: 'Mission Indradhanush', nameTe: 'మిషన్ ఇంద్రధనుష్', region: 'National', keywords: ['vaccination'], en: { description: 'Child health and vaccination' } },
]

test('directory search keeps Telugu combining marks and finds benefits in both languages', () => {
  assert.deepEqual(searchSchemes(catalog, 'పోషణ్').map(item => item.name), ['Poshan Abhiyaan'])
  assert.deepEqual(searchSchemes(catalog, 'child nutrition').map(item => item.name), ['Poshan Abhiyaan'])
  assert.deepEqual(searchSchemes(catalog, 'child unknown'), [])
})

test('assistant search ignores question filler and returns the strongest catalog match first', () => {
  assert.equal(searchSchemes(catalog, 'Which schemes are for child vaccination?', { partial: true })[0].name, 'Mission Indradhanush')
  assert.deepEqual(searchSchemes(catalog, 'What are the schemes?', { partial: true }), [])
})

test('a transposed title and a Telugu spelling variant still resolve to the scheme', () => {
  for (const query of ['Psohan Abhiyaan', 'పోషన్']) {
    assert.equal(searchSchemes(catalog, query)[0]?.name, 'Poshan Abhiyaan')
  }
})

test('related IDs supplement local matches without duplication or bypassing the candidate list', () => {
  const schemes = catalog.map((scheme, id) => ({ ...scheme, id }))
  assert.deepEqual(mergeSchemeMatches(schemes, [schemes[0]], [0, 1, 1, 42]), schemes)
})

test('missing translations fall back to existing text, and unsafe link protocols or credentials are blocked', () => {
  assert.equal(sectionText(catalog[0], 'benefits', 'te'), catalog[0].en.benefits)
  for (const url of ['javascript:alert(1)', 'data:text/html,unsafe', '//example.org', 'https://u:p@example.org']) assert.equal(officialUrl(url), '')
  assert.equal(officialUrl('https://example.org/health'), 'https://example.org/health')
})

test('an exact saved alias resolves to the canonical scheme first', () => {
  const first = { name: 'National Health Programme', keywords: ['old plan'] }
  const canonical = { name: 'Canonical Scheme', aliases: ['Old Plan'] }
  assert.equal(searchSchemes([first, canonical], 'old plan')[0], canonical)
})

test('a component title is searchable under its parent scheme', () => {
  const parent = {
    name: 'National Dialysis Programme',
    programme_components: [{
      title: { en: 'Peritoneal dialysis', te: 'పెరిటోనియల్ డయాలసిస్' },
      search_title: 'PM National Dialysis Programme - Peritoneal Dialysis'
    }]
  }
  for (const query of ['Peritoneal dialysis', 'పెరిటోనియల్ డయాలసిస్']) {
    assert.deepEqual(searchSchemes([parent], query), [parent])
  }
})
