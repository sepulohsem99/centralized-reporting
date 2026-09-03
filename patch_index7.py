#!/usr/bin/env python3
"""Patch #7 index.html: toggle bahasa BM/EN (header) + terjemahan UI
utama (tab, laporan, ganti nilai, manual user). Data run (sebab) kekal
bahasa asalnya — hanya chrome UI yang bertukar."""
import sys
from pathlib import Path

p = Path(sys.argv[1])
t = p.read_text(encoding="utf-8")

if "function toggleLang" in t:
    print("SUDAH-DIPATCH")
    sys.exit(0)


def mesti(a, b):
    global t
    if a not in t:
        sys.exit("TAK JUMPA (wajib): " + a[:70])
    t = t.replace(a, b)


def cuba(a, b):
    global t
    if a in t:
        t = t.replace(a, b)


# 1) Enjin i18n + toggle.
mesti("const ST = {",
      "let LANG=(()=>{try{return localStorage.getItem('lang')||'BM'}"
      "catch(e){return 'BM'}})();\n"
      "function tr(bm,en){return LANG==='EN'?en:bm;}\n"
      "function toggleLang(){LANG=LANG==='BM'?'EN':'BM';"
      "try{localStorage.setItem('lang',LANG)}catch(e){};render();}\n"
      "const ST = {")

# 2) Suis dalam header.
mesti('<div class="right"><span class="chip live" id="feed">LIVE</span>'
      '</div>',
      '<div class="right" style="display:flex;gap:8px;align-items:center">'
      '<span class="chip" id="langsw" onclick="toggleLang()" '
      'style="cursor:pointer;user-select:none" '
      'title="Bahasa / Language">BM | EN</span>'
      '<span class="chip live" id="feed">LIVE</span></div>')

# 3) Kemaskini teks suis pada setiap render.
mesti("function render(){\n  renderSide();",
      "function render(){\n"
      "  const lsw=document.getElementById('langsw');\n"
      "  if(lsw) lsw.innerHTML= LANG==='BM'"
      "?'<b style=\"color:var(--ink)\">BM</b> · EN'"
      ":'BM · <b style=\"color:var(--ink)\">EN</b>';\n"
      "  renderSide();")

# 4) Label tab.
mesti("onclick=\"pickTab('laporan')\">Laporan</div>",
      "onclick=\"pickTab('laporan')\">${tr('Laporan','Report')}</div>")
mesti("onclick=\"pickTab('sejarah')\">Sejarah Run (${runs.length})</div>",
      "onclick=\"pickTab('sejarah')\">${tr('Sejarah Run','Run History')}"
      " (${runs.length})</div>")
mesti("onclick=\"pickTab('ganti')\">Ganti Nilai</div>",
      "onclick=\"pickTab('ganti')\">${tr('Ganti Nilai','Replace "
      "Values')}</div>")

# 5) Laporan.
mesti('`<div class="panel"><div class="empty">Tiada larian untuk PBT '
      'ini lagi</div></div>`',
      '`<div class="panel"><div class="empty">${tr(\'Tiada larian untuk '
      "PBT ini lagi','No runs for this PBT yet')}</div></div>`")
mesti('<div class="l">jumlah tc</div>',
      "<div class=\"l\">${tr('jumlah tc','total tc')}</div>")
mesti('<div class="l">lain</div>',
      "<div class=\"l\">${tr('lain','other')}</div>")
mesti(">${f}<span class=\"k\">",
      ">${f==='SEMUA'?tr('SEMUA','ALL'):f==='LAIN'?tr('LAIN','OTHER'):f}"
      "<span class=\"k\">")
mesti('placeholder="cari TC / sebab..."',
      "placeholder=\"${tr('cari TC / sebab...','search TC / "
      "reason...')}\"")
mesti('`<div class="empty">Tiada TC padan dengan penapis</div>`',
      '`<div class="empty">${tr(\'Tiada TC padan dengan penapis\','
      "'No TC matches the filter')}</div>`")
mesti('<th style="width:210px">Nama</th>',
      "<th style=\"width:210px\">${tr('Nama','Name')}</th>")
mesti("<th>Sebab / bukti</th>",
      "<th>${tr('Sebab / bukti','Reason / evidence')}</th>")

# 6) Ganti Nilai.
mesti("belum disambung — enjin skrip ${sel.pbt} akan diunifikasi. "
      "MBPG & MBIP tersedia.",
      "${tr('belum disambung — enjin skrip '+sel.pbt+' akan "
      "diunifikasi. MBPG & MBIP tersedia.','not connected yet — the "
      "'+sel.pbt+' script engine will be unified. MBPG & MBIP are "
      "available.')}")
cuba("Ganti Nilai untuk ${sel.pbt} ",
     "${tr('Ganti Nilai untuk','Replace Values for')} ${sel.pbt} ")
mesti("w.innerHTML='<div class=\"empty\">Server terminal tidak "
      "tersedia</div>'",
      "w.innerHTML='<div class=\"empty\">'+tr('Server terminal tidak "
      "tersedia','Terminal server unavailable')+'</div>'")
mesti("Ubah nilai → JANA SKRIP: override ditulis ke testdata "
      "${sel.pbt} (asal auto-backup). Kombo kompaun→akta→kesalahan "
      "divalidasi lawan pokok production — kombo tak wujud DITOLAK.",
      "${tr('Ubah nilai → JANA SKRIP: override ditulis ke testdata "
      "'+sel.pbt+' (asal auto-backup). Kombo kompaun→akta→kesalahan "
      "divalidasi lawan pokok production — kombo tak wujud DITOLAK.',"
      "'Edit values → GENERATE: overrides are written into '+sel.pbt+' "
      "testdata (originals auto-backed up). The kompaun→akta→kesalahan "
      "combo is validated against the production tree — unknown combos "
      "are REJECTED.')}")
mesti("${nUbah?nUbah+' medan diubah — belum dijana':'Tiada perubahan'}",
      "${nUbah?nUbah+tr(' medan diubah — belum dijana',' field(s) "
      "changed — not generated yet'):tr('Tiada perubahan','No "
      "changes')}")
mesti(">JANA SKRIP</button>",
      ">${tr('JANA SKRIP','GENERATE')}</button>")
mesti("s.textContent='menjana...';",
      "s.textContent=tr('menjana...','generating...');")
mesti("s2.textContent='✔ Skrip dijana — backup: '+d.backup;",
      "s2.textContent=tr('✔ Skrip dijana — backup: ','✔ Generated — "
      "backup: ')+d.backup;")
mesti("s.textContent='DITOLAK: '+JSON.stringify(d.ralat);",
      "s.textContent=tr('DITOLAK: ','REJECTED: ')"
      "+JSON.stringify(d.ralat);")
cuba('id="gantiWrap"><div class="empty">memuat...</div>',
     'id="gantiWrap"><div class="empty">${tr(\'memuat...\','
     "'loading...')}</div>")

# 7) Manual User — versi dwibahasa (ganti fungsi sepenuhnya).
MULA = "function manualHtml(pbt){"
TAMAT = "function fmtDT("
i = t.find(MULA)
j = t.find(TAMAT)
if i < 0 or j < 0 or j <= i:
    sys.exit("TAK JUMPA blok manualHtml")
k = t.rfind("/*", 0, i)
if k >= 0 and "MANUAL USER" in t[k:i]:
    i = k

BARU = r'''/* ---------------- MANUAL USER (ringkas, generik, BM/EN) --------- */
function manualHtml(pbt){
  const skrip=pbt+'-skrip';
  const adaZip=['MBPG','MBIP'].includes(pbt);
  const runcmd={MBPG:'python tools\\run_penuh.py --borang NPK',
                MBIP:'python tools\\run_penuh_mbip.py --profil mbip-production --terus',
                MBJB:'python tools\\run_and_report.py'}[pbt]||'python tools\\run_and_report.py';
  const ekstra= pbt==='MBPG' ? cmd('$env:MBPG_IZIN_PRODUCTION = "1"') : '';
  const btnZip= adaZip
    ? `<p style="margin:6px 0"><a href="/api/skrip/${pbt}" style="display:inline-block;background:var(--panel2);border:1px solid var(--pass);color:var(--pass);border-radius:8px;padding:8px 16px;font-size:.72rem;font-weight:600;text-decoration:none">⬇ ${tr('MUAT TURUN SKRIP','DOWNLOAD SCRIPT')}</a></p>`
    : `<p style="font-size:.72rem;color:var(--dim)">${tr('Zip '+pbt+' belum tersedia — dapatkan folder suite dari pemilik.','The '+pbt+' zip is not available yet — get the suite folder from the owner.')}</p>`;
  const btnPdf= adaZip
    ? `<p style="margin:4px 0 10px"><a href="/manual/MANUAL-USER-${pbt}.pdf" style="display:inline-flex;align-items:center;gap:8px;background:var(--panel2);border:1px solid #ef4444;color:#ef4444;border-radius:8px;padding:8px 16px;font-size:.72rem;font-weight:600;text-decoration:none"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>${tr('MANUAL USER PDF','USER MANUAL PDF')}</a></p>`
    : '';
  return `<div class="panel" style="border-radius:0 9px 9px 9px"><div class="tut">
    <h2>${tr('Manual User','User Manual')} — ${pbt}</h2>
    ${btnPdf}
    <p style="font-size:.72rem;color:var(--dim)">${tr('Contoh guna <b>C:\\ies-testing</b> — gantikan dengan folder anda (laluan pendek, tiada space).','Examples use <b>C:\\ies-testing</b> — replace with your own folder (short path, no spaces).')}</p>
    <h2>0 · ${tr('Muat turun','Download')}</h2>
    <div class="step">${btnZip}<p>${tr('Zip masuk ke folder <b>Downloads</b>.','The zip lands in your <b>Downloads</b> folder.')}</p></div>
    <h2>1 · ${tr('Susun fail','Organize files')}</h2>
    <div class="step">${cmd('mkdir C:\\ies-testing')}
      <p>${tr('Downloads → klik-kanan zip → <b>Extract All</b> → ke <b>C:\\ies-testing</b>. Jangan run dari Downloads/dalam zip.','Downloads → right-click the zip → <b>Extract All</b> → into <b>C:\\ies-testing</b>. Never run from Downloads or inside the zip.')}</p></div>
    <h2>2 · ${tr('Pasang alat (sekali per komputer)','Install tools (once per computer)')}</h2>
    <div class="step"><p>${tr('Python 3.11+ · Node.js LTS · adb dalam PATH. Detail: sidebar → <b>TUTORIALS</b>.','Python 3.11+ · Node.js LTS · adb on PATH. Details: sidebar → <b>TUTORIALS</b>.')}</p>
      ${cmd('npm install -g appium')}${cmd('appium driver install uiautomator2')}</div>
    <h2>3 · ${tr('Dependencies (sekali per folder)','Dependencies (once per folder)')}</h2>
    <div class="step">${cmd('cd C:\\ies-testing\\'+skrip)}${cmd('pip install -r requirements.txt')}</div>
    <h2>4 · ${tr('Peranti','Devices')}</h2>
    <div class="step"><p>${tr('Telefon: USB debugging ON, APK '+pbt+' dipasang. Printer Bixolon ON.','Phone: USB debugging ON, '+pbt+' APK installed. Bixolon printer ON.')}</p>${cmd('adb devices')}</div>
    <h2>5 · Terminal 1</h2>
    <div class="step">${cmd('appium')}</div>
    <h2>6 · Terminal 2</h2>
    <div class="step">${cmd('cd C:\\ies-testing\\'+skrip)}${ekstra}${cmd(runcmd)}</div>
    <h2>7 · ${tr('Hasil','Results')}</h2>
    <div class="step"><p>${tr('Laporan: <b>'+skrip+'\\reports\\</b>. Masuk papan ini: salin run JSON → <b>laporan\\data\\'+pbt+'\\runs\\</b> → refresh.','Reports: <b>'+skrip+'\\reports\\</b>. To show a run on this board: copy the run JSON → <b>laporan\\data\\'+pbt+'\\runs\\</b> → refresh.')}</p></div>
  </div></div>`;
}

'''
t = t[:i] + BARU + t[j:]

p.write_text(t, encoding="utf-8")
print("PATCH7-OK", p)
