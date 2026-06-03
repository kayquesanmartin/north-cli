#!/usr/bin/env node
/*
 * north — lancador cross-plataforma (Windows / macOS / Linux).
 *
 * north e um app Python; este shim Node existe so para a distribuicao via npm/npx.
 * Ele detecta o interpretador Python e roteia:
 *   north            -> install.py (bootstrap)          [tambem: npx north-cli]
 *   north install    -> install.py [args]
 *   north <cmd> ...   -> ~/.claude/painel/run.py <cmd>   (engine instalado)
 *
 * Nunca reimplementa nada do north — so acha o Python e delega.
 */
'use strict';

const { spawnSync } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');

const PKG_ROOT = path.join(__dirname, '..');
const HOME = process.env.USERPROFILE || process.env.HOME || os.homedir();
const ENGINE_RUN = path.join(HOME, '.claude', 'painel', 'run.py');
const BUNDLED_INSTALL = path.join(PKG_ROOT, 'install.py');

function findPython() {
  // Windows: 'py' (launcher) costuma ser o mais confiavel; depois python/python3.
  // Unix: python3 primeiro.
  const candidates = process.platform === 'win32'
    ? ['py', 'python', 'python3']
    : ['python3', 'python'];
  for (const c of candidates) {
    try {
      const r = spawnSync(c, ['-c', 'import sys; sys.exit(0 if sys.version_info[0]>=3 else 1)'],
        { stdio: 'ignore' });
      if (!r.error && r.status === 0) return c;
    } catch (e) { /* tenta o proximo */ }
  }
  return null;
}

function fail(msg) { process.stderr.write('north: ' + msg + '\n'); process.exit(1); }

const py = findPython();
if (!py) {
  fail('Python 3.8+ nao encontrado no PATH. Instale o Python e tente de novo.\n' +
       '  macOS:  brew install python   |  Linux: apt install python3   |  Windows: https://python.org');
}

const args = process.argv.slice(2);
const cmd = args[0] || '';

let script, scriptArgs;
if (cmd === '' || cmd === 'install') {
  // bootstrap / (re)instalacao — roda o install.py embutido no pacote
  script = BUNDLED_INSTALL;
  scriptArgs = (cmd === 'install') ? args.slice(1) : args;
} else {
  // comando normal -> engine instalado em ~/.claude/painel
  if (!fs.existsSync(ENGINE_RUN)) {
    fail('engine nao instalado ainda. Rode primeiro:  north install   (ou: npx north-cli)');
  }
  script = ENGINE_RUN;
  scriptArgs = args;
}

const res = spawnSync(py, [script].concat(scriptArgs), { stdio: 'inherit' });
if (res.error) fail(String(res.error.message || res.error));
process.exit(res.status == null ? 1 : res.status);
