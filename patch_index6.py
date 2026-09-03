#!/usr/bin/env python3
"""Patch #6 index.html: Manual User dikemaskan — ringkas, satu baris
setiap poin, buang ayat panjang (maklum balas CEO: too wordy)."""
import sys
from pathlib import Path

p = Path(sys.argv[1])
t = p.read_text(encoding="utf-8")

MULA = "function manualHtml(pbt){"
TAMAT = "function fmtDT("
i = t.find(MULA)
j = t.find(TAMAT)
if i < 0 or j < 0 or j <= i:
    sys.exit("TAK JUMPA blok manualHtml")
# kekalkan komen blok sebelum fungsi — cari titik mula komen
k = t.rfind("/*", 0, i)
if k >= 0 and "MANUAL USER" in t[k:i]:
    i = k

BARU = r'''/* ---------------- MANUAL USER (ringkas, generik) ---------------- */
function manualHtml(pbt){
  const skrip=pbt+'-skrip';
  const adaZip=['MBPG','MBIP'].includes(pbt);
  const runcmd={MBPG:'python tools\\run_penuh.py --borang NPK',
                MBIP:'python tools\\run_penuh_mbip.py --profil mbip-production --terus',
                MBJB:'python tools\\run_and_report.py'}[pbt]||'python tools\\run_and_report.py';
  const ekstra= pbt==='MBPG' ? cmd('$env:MBPG_IZIN_PRODUCTION = "1"') : '';
  const btnZip= adaZip
    ? `<p style="margin:6px 0"><a href="/api/skrip/${pbt}" style="display:inline-block;background:var(--panel2);border:1px solid var(--pass);color:var(--pass);border-radius:8px;padding:8px 16px;font-size:.72rem;font-weight:600;text-decoration:none">⬇ MUAT TURUN SKRIP</a></p>`
    : `<p style="font-size:.72rem;color:var(--dim)">Zip ${pbt} belum tersedia — dapatkan folder suite dari pemilik.</p>`;
  const btnPdf= adaZip
    ? `<p style="margin:4px 0 10px"><a href="/manual/MANUAL-USER-${pbt}.pdf" style="display:inline-flex;align-items:center;gap:8px;background:var(--panel2);border:1px solid #ef4444;color:#ef4444;border-radius:8px;padding:8px 16px;font-size:.72rem;font-weight:600;text-decoration:none"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>MANUAL USER PDF</a></p>`
    : '';
  return `<div class="panel" style="border-radius:0 9px 9px 9px"><div class="tut">
    <h2>Manual User — ${pbt}</h2>
    ${btnPdf}
    <p style="font-size:.72rem;color:var(--dim)">Contoh guna <b>C:\\ies-testing</b> — gantikan dengan folder anda (laluan pendek, tiada space).</p>
    <h2>0 · Muat turun</h2>
    <div class="step">${btnZip}<p>Zip masuk ke folder <b>Downloads</b>.</p></div>
    <h2>1 · Susun fail</h2>
    <div class="step">${cmd('mkdir C:\\ies-testing')}
      <p>Downloads → klik-kanan zip → <b>Extract All</b> → ke <b>C:\\ies-testing</b>. Jangan run dari Downloads/dalam zip.</p></div>
    <h2>2 · Pasang alat (sekali per komputer)</h2>
    <div class="step"><p>Python 3.11+ · Node.js LTS · adb dalam PATH. Detail: sidebar → <b>TUTORIALS</b>.</p>
      ${cmd('npm install -g appium')}${cmd('appium driver install uiautomator2')}</div>
    <h2>3 · Dependencies (sekali per folder)</h2>
    <div class="step">${cmd('cd C:\\ies-testing\\'+skrip)}${cmd('pip install -r requirements.txt')}</div>
    <h2>4 · Peranti</h2>
    <div class="step"><p>Telefon: USB debugging ON, APK ${pbt} dipasang. Printer Bixolon ON.</p>${cmd('adb devices')}</div>
    <h2>5 · Terminal 1</h2>
    <div class="step">${cmd('appium')}</div>
    <h2>6 · Terminal 2</h2>
    <div class="step">${cmd('cd C:\\ies-testing\\'+skrip)}${ekstra}${cmd(runcmd)}</div>
    <h2>7 · Hasil</h2>
    <div class="step"><p>Laporan: <b>${skrip}\\reports\\</b>. Masuk papan ini: salin run JSON → <b>laporan\\data\\${pbt}\\runs\\</b> → refresh.</p></div>
  </div></div>`;
}

'''

t = t[:i] + BARU + t[j:]
p.write_text(t, encoding="utf-8")
print("PATCH6-OK", p)
