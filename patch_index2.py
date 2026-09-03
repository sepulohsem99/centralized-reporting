#!/usr/bin/env python3
"""Patch #2 index.html: butang Muat Turun Skrip (MBPG + MBIP)."""
import sys
from pathlib import Path

p = Path(sys.argv[1])
t = p.read_text(encoding="utf-8")

sasar = ("    <div class=\"tab ${sel.tab==='manual'?'on':''}\" "
         "onclick=\"pickTab('manual')\">Manual User</div>\n  </div>`;")
ganti = ("    <div class=\"tab ${sel.tab==='manual'?'on':''}\" "
         "onclick=\"pickTab('manual')\">Manual User</div>\n"
         "    ${['MBPG','MBIP'].includes(sel.pbt)?`<a class=\"tab\" "
         "style=\"text-decoration:none;color:var(--pass)\" "
         "href=\"/api/skrip/${sel.pbt}\" "
         "title=\"Zip suite skrip penuh (tanpa cache/dump/apk)\">"
         "⬇ Muat Turun Skrip</a>`:''}\n  </div>`;")

if "Muat Turun Skrip" in t:
    print("SUDAH-DIPATCH — tiada perubahan")
    sys.exit(0)
if sasar not in t:
    sys.exit("TAK JUMPA sasaran tab Manual User")
t = t.replace(sasar, ganti)
p.write_text(t, encoding="utf-8")
print("PATCH2-OK", p)
