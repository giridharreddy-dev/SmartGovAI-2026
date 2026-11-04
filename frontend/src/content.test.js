import assert from 'node:assert/strict'
import test from 'node:test'
import { officialUrl, searchSchemes, sectionText } from './content.js'

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

test('missing translations fall back to existing text, and unsafe link protocols or credentials are blocked', () => {
  assert.equal(sectionText(catalog[0], 'benefits', 'te'), catalog[0].en.benefits)
  for (const url of ['javascript:alert(1)', 'data:text/html,unsafe', '//example.org', 'https://u:p@example.org']) assert.equal(officialUrl(url), '')
  assert.equal(officialUrl('https://example.org/health'), 'https://example.org/health')
})
