#!/usr/bin/env node
/*
 * north — instalador/lançador cross-plataforma multi-runtime (Win/macOS/Linux).
 *
 *   npx north-cli            -> instalador interativo (escolhe runtimes, escopo, pasta)
 *   north install [flags]    -> instala (não-interativo se receber flags)
 *   north <cmd> [args]       -> roda o motor (~/.north/run.py) — focus, note, status, ...
 *
 * O north é um app Python; este shim acha o Python e delega. Nunca o usuário
 * precisa digitar "python install.py".
 */
'use strict';

const { spawnSync, spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');
const readline = require('readline');

const PKG_ROOT = path.join(__dirname, '..');
const BUNDLED_INSTALL = path.join(PKG_ROOT, 'install.py');
const HOME = process.env.USERPROFILE || process.env.HOME || os.homedir();

const RUNTIMES = [
  { key: 'claude', label: 'Claude Code', home: '~/.claude' },
  { key: 'codex', label: 'Codex', home: '~/.codex' },
  { key: 'gemini', label: 'Gemini CLI', home: '~/.gemini' },
];

function findPython() {
  const cands = process.platform === 'win32'
    ? ['py', 'python', 'python3'] : ['python3', 'python'];
  for (const c of cands) {
    try {
      const r = spawnSync(c, ['-c', 'import sys; sys.exit(0 if sys.version_info[0]>=3 else 1)'],
        { stdio: 'ignore' });
      if (!r.error && r.status === 0) return c;
    } catch (e) { /* próximo */ }
  }
  return null;
}

function fail(msg) { process.stderr.write('north: ' + msg + '\n'); process.exit(1); }

function engineRun() {
  // Resolve o run.py do motor instalado (ordem: ~/.north, ./.north, legado ~/.claude/painel)
  const cands = [
    path.join(HOME, '.north', 'run.py'),
    path.join(process.cwd(), '.north', 'run.py'),
    path.join(HOME, '.claude', 'painel', 'run.py'),
  ];
  return cands.find(p => fs.existsSync(p)) || null;
}

const BANNER = [
  '',
  '  \x1b[38;5;208m███╗   ██╗ ██████╗ ██████╗ ████████╗██╗  ██╗\x1b[0m',
  '  \x1b[38;5;208m████╗  ██║██╔═══██╗██╔══██╗╚══██╔══╝██║  ██║\x1b[0m',
  '  \x1b[38;5;208m██╔██╗ ██║██║   ██║██████╔╝   ██║   ███████║\x1b[0m',
  '  \x1b[38;5;214m██║╚██╗██║██║   ██║██╔══██╗   ██║   ██╔══██║\x1b[0m',
  '  \x1b[38;5;214m██║ ╚████║╚██████╔╝██║  ██║   ██║   ██║  ██║\x1b[0m',
  '  \x1b[38;5;214m╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝\x1b[0m',
  '',
  '  \x1b[1mnorth\x1b[0m \x1b[2m— copiloto de produtividade multi-projeto para IAs\x1b[0m',
  '  \x1b[2mfoco do dia · sinais vitais · painel · lê plan-build e GSD · 100% local\x1b[0m',
  '',
].join('\n');

function ask(rl, q, def_) {
  return new Promise(res => rl.question(q, a => res((a || '').trim() || def_)));
}

async function interactiveInstall(py) {
  process.stdout.write(BANNER + '\n');
  if (!process.stdin.isTTY) {
    // sem terminal (CI/headless): instala Claude Code, global, pasta atual
    return runInstall(py, ['--runtimes', 'claude', '--scope', 'global', '--all']);
  }
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  try {
    process.stdout.write('  Para quais runtimes instalar?\n');
    RUNTIMES.forEach((r, i) => process.stdout.write(
      '    ' + (i + 1) + ') ' + r.label.padEnd(12) + ' \x1b[2m(' + r.home + ')\x1b[0m\n'));
    process.stdout.write('    ' + (RUNTIMES.length + 1) + ') Todos\n');
    const sel = await ask(rl, '  Escolha (ex.: 1,3 ou 1 3) [1]: ', '1');
    let keys;
    const nums = sel.split(/[,\s]+/).map(s => parseInt(s, 10)).filter(n => !isNaN(n));
    if (nums.includes(RUNTIMES.length + 1) || /todos|all/i.test(sel)) {
      keys = RUNTIMES.map(r => r.key);
    } else {
      keys = nums.filter(n => n >= 1 && n <= RUNTIMES.length).map(n => RUNTIMES[n - 1].key);
    }
    if (!keys.length) keys = ['claude'];

    process.stdout.write('\n  Escopo da instalação?\n');
    process.stdout.write('    1) Global (~/.north, ~/.claude, ...) — todos os projetos\n');
    process.stdout.write('    2) Local  (./.north, ./.claude, ...) — só este diretório\n');
    const sc = await ask(rl, '  Escolha [1]: ', '1');
    const scope = (sc === '2') ? 'local' : 'global';

    process.stdout.write('\n  Onde ficam seus projetos? O north varre essa pasta (e subpastas)\n');
    process.stdout.write('  atrás de projetos com plan-build/ ou .planning/.\n');
    process.stdout.write('  \x1b[2mDica: aponte para a pasta-raiz que contém todos os seus repos.\x1b[0m\n');
    process.stdout.write('  \x1b[2mExemplos: ~/code · ~/projetos · ' + process.cwd() + '\x1b[0m\n');
    let root = await ask(rl, '  Pasta dos projetos [' + process.cwd() + ']: ', process.cwd());
    if (root[0] === '~') root = path.join(os.homedir(), root.slice(1));
    if (!fs.existsSync(root)) {
      const yn = await ask(rl, "  '" + root + "' não existe. Criar agora? [S/n]: ", 's');
      if (/^(s|sim|y|yes)$/i.test(yn.trim())) {
        try { fs.mkdirSync(root, { recursive: true }); process.stdout.write('  (criada)\n'); }
        catch (e) { process.stdout.write('  (não consegui criar: ' + e.message + ')\n'); }
      }
    }

    rl.close();
    process.stdout.write('\n');
    return runInstall(py, ['--runtimes', keys.join(','), '--scope', scope,
      '--scan-root', root]);
  } finally {
    try { rl.close(); } catch (e) {}
  }
}

function runInstall(py, flags) {
  const r = spawnSync(py, [BUNDLED_INSTALL].concat(flags), { stdio: 'inherit' });
  return r.status == null ? 1 : r.status;
}

const py = findPython();
if (!py) {
  fail('Python 3.8+ não encontrado no PATH.\n' +
       '  macOS: brew install python | Linux: apt install python3 | Windows: https://python.org');
}

const args = process.argv.slice(2);
const cmd = args[0] || '';

if (cmd === '' || cmd === 'install') {
  const flags = (cmd === 'install') ? args.slice(1) : [];
  if (flags.length) {
    process.exit(runInstall(py, flags));            // install com flags = não-interativo
  } else {
    interactiveInstall(py).then(code => process.exit(code))
      .catch(e => fail(String(e && e.message || e)));
  }
} else if (cmd === 'uninstall' || cmd === 'remove') {
  process.exit(runInstall(py, args));               // 'uninstall' + flags -> install.py
} else {
  const run = engineRun();
  if (!run) fail('motor não instalado. Rode primeiro:  npx north-cli   (ou: north install)');
  const r = spawnSync(py, [run].concat(args), { stdio: 'inherit' });
  if (r.error) fail(String(r.error.message || r.error));
  process.exit(r.status == null ? 1 : r.status);
}
