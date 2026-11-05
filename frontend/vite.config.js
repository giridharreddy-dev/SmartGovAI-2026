import { defineConfig } from 'vite'
import { createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'

export default defineConfig({
  base: '/studio/',
  esbuild: { jsx: 'automatic' },
  plugins: [{
    name: 'smartgov-offline',
    apply: 'build',
    generateBundle(_, bundle) {
      const worker = readFileSync(new URL('./src/worker.js', import.meta.url), 'utf8')
      const hash = createHash('sha256').update(worker)
      for (const name of ['index.html', 'public/mark.svg', 'public/manifest.webmanifest'])
        hash.update(readFileSync(new URL(name, import.meta.url)))
      const assets = Object.keys(bundle).filter(name => name.startsWith('assets/')).sort()
      assets.forEach(name => hash.update(name))
      this.emitFile({
        type: 'asset', fileName: 'sw.js',
        source: worker.replace('__BUILD_ID__', hash.digest('hex').slice(0, 12))
          .replace('/*__ASSETS__*/', assets.map(name => JSON.stringify('/studio/' + name)).join(',')),
      })
      const licenses = ['fraunces', 'manrope', 'noto-sans-telugu'].map(name =>
        readFileSync(new URL(`node_modules/@fontsource-variable/${name}/LICENSE`, import.meta.url), 'utf8').trim())
      this.emitFile({ type: 'asset', fileName: 'font-licenses.txt', source: licenses.join('\n\n-----\n\n') + '\n' })
    },
  }],
})
