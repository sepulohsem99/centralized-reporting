#!/usr/bin/env python3
"""Patch #9 index.html: Manual User kembali ke layout senarai ringkas
(versi patch #6/#7 yang CEO suka) + ikon SVG setiap langkah + satu
ilustrasi hardware: laptop -USB- telefon -Bluetooth- printer Bixolon."""
import sys
from pathlib import Path

p = Path(sys.argv[1])
t = p.read_text(encoding="utf-8")

if "function ikonManual" in t:
    print("SUDAH-DIPATCH")
    sys.exit(0)

MULA = "function manualHtml(pbt){"
TAMAT = "function fmtDT("
i = t.find(MULA)
j = t.find(TAMAT)
if i < 0 or j < 0 or j <= i:
    sys.exit("TAK JUMPA blok manualHtml")
k = t.rfind("/*", 0, i)
if k >= 0 and "MANUAL USER" in t[k:i]:
    i = k

BARU = r'''/* ---- MANUAL USER (senarai ringkas + ikon + ilustrasi hardware) ---- */
function ikonManual(n){
  const s='width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-3px;margin-right:7px"';
  const d={
    muat:`<svg ${s}><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>`,
    folder:`<svg ${s}><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>`,
    alat:`<svg ${s}><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>`,
    pakej:`<svg ${s}><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>`,
    fon:`<svg ${s}><rect x="5" y="2" width="14" height="20" rx="2" ry="2"/><line x1="12" y1="18" x2="12.01" y2="18"/></svg>`,
    terminal:`<svg ${s}><polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/></svg>`,
    main:`<svg ${s}><polygon points="5 3 19 12 5 21 5 3"/></svg>`,
    hasil:`<svg ${s}><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>`,
  };
  return d[n]||'';
}
function ilustrasiHardware(){
  const lbl='font-size="8.5" fill="var(--dim)" text-anchor="middle" font-family="Segoe UI,Arial"';
  const wire='stroke="var(--dimmer)" stroke-width="1.5"';
  return `<div style="margin:8px 0 12px;overflow-x:auto">
  <svg width="430" height="96" viewBox="0 0 430 96" fill="none" xmlns="http://www.w3.org/2000/svg">
    <!-- laptop -->
    <g stroke="var(--cyan)" stroke-width="2" stroke-linejoin="round">
      <rect x="22" y="18" width="64" height="38" rx="3"/>
      <path d="M14 62 L94 62 L86 56 L22 56 Z" fill="var(--panel2)"/>
      <polyline points="34 30 40 36 34 42" stroke-width="1.6"/>
      <line x1="44" y1="42" x2="56" y2="42" stroke-width="1.6"/>
    </g>
    <text x="54" y="80" ${lbl}>Laptop · Appium</text>
    <!-- USB -->
    <line x1="100" y1="40" x2="168" y2="40" ${wire}/>
    <text x="134" y="32" ${lbl}>USB</text>
    <!-- telefon -->
    <g stroke="var(--pass)" stroke-width="2" stroke-linejoin="round">
      <rect x="174" y="12" width="34" height="58" rx="5"/>
      <line x1="187" y1="62" x2="195" y2="62"/>
    </g>
    <text x="191" y="86" ${lbl}>Phone · IES APK</text>
    <!-- Bluetooth -->
    <line x1="214" y1="40" x2="288" y2="40" ${wire} stroke-dasharray="5 4"/>
    <text x="251" y="32" ${lbl}>Bluetooth</text>
    <!-- printer bixolon -->
    <g stroke="var(--lain)" stroke-width="2" stroke-linejoin="round">
      <rect x="294" y="26" width="66" height="32" rx="4"/>
      <rect x="306" y="14" width="42" height="12" rx="2"/>
      <path d="M310 58 L310 74 L344 74 L344 58" stroke-width="1.6"/>
      <line x1="316" y1="64" x2="338" y2="64" stroke-width="1.2"/>
      <line x1="316" y1="69" x2="332" y2="69" stroke-width="1.2"/>
      <circle cx="350" cy="42" r="2.5" fill="var(--lain)" stroke="none"/>
    </g>
    <text x="327" y="90" ${lbl}>Printer Bixolon SPP</text>
  </svg></div>`;
}
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
    ? `<p style="margin:4px 0 6px"><a href="/manual/MANUAL-USER-${pbt}.pdf" style="display:inline-flex;align-items:center;gap:8px;background:var(--panel2);border:1px solid #ef4444;color:#ef4444;border-radius:8px;padding:8px 16px;font-size:.72rem;font-weight:600;text-decoration:none"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>${tr('MANUAL USER PDF','USER MANUAL PDF')}</a></p>`
    : '';
  return `<div class="panel" style="border-radius:0 9px 9px 9px"><div class="tut">
    <h2>${tr('Manual User','User Manual')} — ${pbt}</h2>
    ${btnPdf}
    ${ilustrasiHardware()}
    <p style="font-size:.72rem;color:var(--dim)">${tr('Contoh guna <b>C:\\ies-testing</b> — gantikan dengan folder anda (laluan pendek, tiada space).','Examples use <b>C:\\ies-testing</b> — replace with your own folder (short path, no spaces).')}</p>
    <h2>${ikonManual('muat')}0 · ${tr('Muat turun','Download')}</h2>
    <div class="step">${btnZip}<p>${tr('Zip masuk ke folder <b>Downloads</b>.','The zip lands in your <b>Downloads</b> folder.')}</p></div>
    <h2>${ikonManual('folder')}1 · ${tr('Susun fail','Organize files')}</h2>
    <div class="step">${cmd('mkdir C:\\ies-testing')}
      <p>${tr('Downloads → klik-kanan zip → <b>Extract All</b> → ke <b>C:\\ies-testing</b>. Jangan run dari Downloads/dalam zip.','Downloads → right-click the zip → <b>Extract All</b> → into <b>C:\\ies-testing</b>. Never run from Downloads or inside the zip.')}</p></div>
    <h2>${ikonManual('alat')}2 · ${tr('Pasang alat (sekali per komputer)','Install tools (once per computer)')}</h2>
    <div class="step"><p>${tr('Python 3.11+ · Node.js LTS · adb dalam PATH. Detail: sidebar → <b>TUTORIALS</b>.','Python 3.11+ · Node.js LTS · adb on PATH. Details: sidebar → <b>TUTORIALS</b>.')}</p>
      ${cmd('npm install -g appium')}${cmd('appium driver install uiautomator2')}</div>
    <h2>${ikonManual('pakej')}3 · ${tr('Dependencies (sekali per folder)','Dependencies (once per folder)')}</h2>
    <div class="step">${cmd('cd C:\\ies-testing\\'+skrip)}${cmd('pip install -r requirements.txt')}</div>
    <h2>${ikonManual('fon')}4 · ${tr('Peranti','Devices')}</h2>
    <div class="step"><p>${tr('Telefon: USB debugging ON, APK '+pbt+' dipasang. Printer Bixolon ON.','Phone: USB debugging ON, '+pbt+' APK installed. Bixolon printer ON.')}</p>${cmd('adb devices')}</div>
    <h2>${ikonManual('terminal')}5 · Terminal 1</h2>
    <div class="step">${cmd('appium')}</div>
    <h2>${ikonManual('main')}6 · Terminal 2</h2>
    <div class="step">${cmd('cd C:\\ies-testing\\'+skrip)}${ekstra}${cmd(runcmd)}</div>
    <h2>${ikonManual('hasil')}7 · ${tr('Hasil','Results')}</h2>
    <div class="step"><p>${tr('Laporan: <b>'+skrip+'\\reports\\</b>. Masuk papan ini: salin run JSON → <b>laporan\\data\\'+pbt+'\\runs\\</b> → refresh.','Reports: <b>'+skrip+'\\reports\\</b>. To show a run here: copy the run JSON → <b>laporan\\data\\'+pbt+'\\runs\\</b> → refresh.')}</p></div>
  </div></div>`;
}

'''
t = t[:i] + BARU + t[j:]
p.write_text(t, encoding="utf-8")
print("PATCH9-OK", p)
