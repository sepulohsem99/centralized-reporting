#!/usr/bin/env python3
"""Patch #4 index.html: alih butang Muat Turun Skrip — keluar dari baris
tab (CEO tak setuju gaya tab), masuk ke dalam Manual User langkah 0."""
import sys
from pathlib import Path

p = Path(sys.argv[1])
t = p.read_text(encoding="utf-8")

# 1) Buang butang dari baris tab (dipasang patch #2).
tab_btn = ("    ${['MBPG','MBIP'].includes(sel.pbt)?`<a class=\"tab\" "
           "style=\"text-decoration:none;color:var(--pass)\" "
           "href=\"/api/skrip/${sel.pbt}\" "
           "title=\"Zip suite skrip penuh (tanpa cache/dump/apk)\">"
           "⬇ Muat Turun Skrip</a>`:''}\n")
if tab_btn in t:
    t = t.replace(tab_btn, "")
elif "⬇ Muat Turun Skrip</a>`:''}" in t:
    sys.exit("Butang tab wujud tetapi teks tak padan — semak manual")

# 2) Ganti langkah 0 Manual User: rujukan "butang di baris tab" ->
#    butang sebenar dalam langkah itu sendiri.
lama = ("        <li>Klik butang <b>⬇ Muat Turun Skrip</b> di baris "
        "tab atas.</li>\n"
        "        <li>Fail zip (<b>${skrip}-&lt;tarikh&gt;.zip</b>) akan "
        "masuk ke folder <b>Downloads</b> anda.</li></ul></div>")
baru = ("        <li>Klik butang di bawah — fail zip "
        "(<b>${skrip}-&lt;tarikh&gt;.zip</b>) akan masuk ke folder "
        "<b>Downloads</b> anda.</li></ul>\n"
        "      <p style=\"margin:10px 0 4px\"><a href=\"/api/skrip/"
        "${pbt}\" style=\"display:inline-block;background:var(--panel2);"
        "border:1px solid var(--pass);color:var(--pass);"
        "border-radius:8px;padding:8px 16px;font-size:.72rem;"
        "font-weight:600;text-decoration:none\" title=\"Zip suite "
        "skrip penuh (tanpa cache/dump/apk)\">⬇ MUAT TURUN SKRIP "
        "${pbt}</a></p></div>")
if lama not in t:
    sys.exit("TAK JUMPA langkah 0 Manual User")
t = t.replace(lama, baru)

p.write_text(t, encoding="utf-8")
print("PATCH4-OK", p)
