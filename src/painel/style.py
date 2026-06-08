# -*- coding: utf-8 -*-
"""
style.py — estilo compartilhado da saída de terminal do north (cores ANSI +
helpers de cabeçalho/dica/estado-vazio), para um output consistente entre todos
os comandos. Degrada para texto puro se a paleta não estiver disponível.
"""

ANSI = {
    "reset": "\033[0m", "dim": "\033[2m", "bold": "\033[1m",
    "north": "\033[38;5;208m",      # laranja north
    "ok": "\033[38;5;114m", "warn": "\033[38;5;221m", "risk": "\033[38;5;203m",
    "accent": "\033[38;5;208m", "squad": "\033[38;5;111m",
}


def header(title, sub=""):
    a = ANSI
    line = "{}\U0001f9ed north{} · {}".format(a["north"], a["reset"], title)
    if sub:
        line += "  {}{}{}".format(a["dim"], sub, a["reset"])
    return line


def tip(msg):
    return "  {}→ {}{}".format(ANSI["dim"], msg, ANSI["reset"])


def empty(msg, hint=""):
    out = "  {}(vazio) {}{}".format(ANSI["dim"], msg, ANSI["reset"])
    if hint:
        out += "\n" + tip(hint)
    return out
