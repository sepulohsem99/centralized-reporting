#!/usr/bin/env python3
"""Patch #5 index.html: pautan Manual User PDF (ikon PDF) di bahagian
atas tab Manual User — MBPG & MBIP."""
import sys
from pathlib import Path

p = Path(sys.argv[1])
t = p.read_text(encoding="utf-8")

if "MANUAL-USER-${pbt}.pdf" in t:
    print("SUDAH-DIPATCH — tiada perubahan")
    sys.exit(0)

sasar = ("    <h2>Manual User — ${pbt}</h2>\n")
ganti = (
    "    <h2>Manual User — ${pbt}</h2>\n"
    "    ${adaZip?`<p style=\"margin:4px 0 10px\"><a "
    "href=\"/manual/MANUAL-USER-${pbt}.pdf\" "
    "style=\"display:inline-flex;align-items:center;gap:8px;"
    "background:var(--panel2);border:1px solid #ef4444;color:#ef4444;"
    "border-radius:8px;padding:8px 16px;font-size:.72rem;font-weight:600;"
    "text-decoration:none\" title=\"Muat turun manual ini sebagai PDF\">"
    "<svg width=\"15\" height=\"15\" viewBox=\"0 0 24 24\" "
    "fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" "
    "stroke-linecap=\"round\" stroke-linejoin=\"round\">"
    "<path d=\"M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 "
    "2-2V8z\"/><polyline points=\"14 2 14 8 20 8\"/></svg>"
    "MANUAL USER PDF (${pbt})</a></p>`:''}\n")

if sasar not in t:
    sys.exit("TAK JUMPA tajuk Manual User")
t = t.replace(sasar, ganti)
p.write_text(t, encoding="utf-8")
print("PATCH5-OK", p)
