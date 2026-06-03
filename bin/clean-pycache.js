#!/usr/bin/env node
/*
 * prepack: remove __pycache__/*.pyc do pacote antes do npm empacotar.
 * O campo "files" do package.json (whitelist) faz o .npmignore NAO podar dentro
 * das pastas incluidas — entao limpamos o working tree aqui. Portavel (Node fs).
 */
'use strict';
const fs = require('fs');
const path = require('path');

let removed = 0;
function walk(dir) {
  let entries;
  try { entries = fs.readdirSync(dir, { withFileTypes: true }); }
  catch (e) { return; }
  for (const e of entries) {
    if (!e.isDirectory()) continue;
    if (e.name === 'node_modules') continue;
    const full = path.join(dir, e.name);
    if (e.name === '__pycache__') {
      fs.rmSync(full, { recursive: true, force: true });
      removed++;
    } else {
      walk(full);
    }
  }
}

walk(path.join(__dirname, '..'));
process.stdout.write('prepack: ' + removed + ' __pycache__ removido(s)\n');
