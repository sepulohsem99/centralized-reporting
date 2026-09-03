#!/usr/bin/env python3
"""Patch index.html Laporan Berpusat: Ganti Nilai MBPG-sahaja -> MBPG+MBIP."""
import sys
from pathlib import Path

p = Path(sys.argv[1])
t = p.read_text(encoding="utf-8")

subs = [
    ("/* ---------------- GANTI NILAI (Fasa 5, MBPG sahaja buat masa ini)"
     " ------ */",
     "/* ---------------- GANTI NILAI (Fasa 5 — MBPG + MBIP, unifikasi"
     " 2026-09-02) ------ */"),

    ("if(sel.pbt!=='MBPG'){",
     "if(!['MBPG','MBIP'].includes(sel.pbt)){"),

    ("belum disambung — enjin skrip ${sel.pbt} akan diunifikasi "
     "(Fasa 4). MBPG tersedia.",
     "belum disambung — enjin skrip ${sel.pbt} akan diunifikasi. "
     "MBPG & MBIP tersedia."),

    ("try{ const r=await fetch('/api/terminal/data',{cache:'no-store'});",
     "if(window._gantiPbt!==sel.pbt){ tedit={}; window._gantiPbt=sel.pbt; }\n"
     "  try{ const r=await fetch('/api/terminal/data?pbt='+sel.pbt,"
     "{cache:'no-store'});"),

    ("override ditulis ke oracle MBPG (asal auto-backup)",
     "override ditulis ke testdata ${sel.pbt} (asal auto-backup)"),

    ("body:JSON.stringify({perubahan:tedit})});",
     "body:JSON.stringify({pbt:sel.pbt,perubahan:tedit})});"),
]
for a, b in subs:
    if a not in t:
        sys.exit("TAK JUMPA: " + a[:70])
    t = t.replace(a, b)
p.write_text(t, encoding="utf-8")
print("PATCH-OK", p)
