#!/usr/bin/env python3
"""Patch #3 index.html: Manual User generik — mula dari muat turun zip,
susun fail (struktur folder setiap orang berbeza), baru pasang & run."""
import sys
from pathlib import Path

p = Path(sys.argv[1])
t = p.read_text(encoding="utf-8")

MULA = "/* ---------------- MANUAL USER (per PBT) ---------------- */"
TAMAT = "function fmtDT("
i = t.find(MULA)
j = t.find(TAMAT)
if i < 0 or j < 0 or j <= i:
    sys.exit("TAK JUMPA penanda blok Manual User")

BARU = r'''/* ---------------- MANUAL USER (per PBT, generik) ----------------
   2026-09-02: ditulis semula — struktur folder setiap orang BERBEZA,
   jadi manual bermula dari butang Muat Turun Skrip dan mengajar cara
   menyusun fail dahulu; tiada laluan mesin sesiapa di-hardcode. */
function manualHtml(pbt){
  const skrip=pbt+'-skrip';
  const adaZip=['MBPG','MBIP'].includes(pbt);
  const runcmd={MBPG:'python tools\\run_penuh.py --borang NPK',
                MBIP:'python tools\\run_penuh_mbip.py --profil mbip-production --terus',
                MBJB:'python tools\\run_and_report.py'}[pbt]||'python tools\\run_and_report.py';
  const ekstra= pbt==='MBPG'
    ? `<p>Khusus MBPG — sebelum runner, benarkan production dan jawab soalan skrip (IP/lesen: Enter untuk terima profil, kemudian taip YA). Printer Bixolon WAJIB hidup (atau tambah <b>--tanpa-printer</b>).</p>
       ${cmd('$env:MBPG_IZIN_PRODUCTION = "1"')}`
    : '';
  const langkah0= adaZip
    ? `<div class="step"><ul>
        <li>Klik butang <b>⬇ Muat Turun Skrip</b> di baris tab atas.</li>
        <li>Fail zip (<b>${skrip}-&lt;tarikh&gt;.zip</b>) akan masuk ke folder <b>Downloads</b> anda.</li></ul></div>`
    : `<div class="step"><p>Zip skrip ${pbt} belum tersedia dari papan ini — dapatkan folder suite daripada pemilik, kemudian ikut langkah 1 seterusnya (susun fail sama sahaja).</p></div>`;
  return `<div class="panel" style="border-radius:0 9px 9px 9px"><div class="tut">
    <h2>Manual User — ${pbt}</h2>
    <p>Manual ini GENERIK — struktur folder setiap komputer berbeza, jadi kita mula dari muat turun dan susun fail dahulu. Contoh di bawah guna <b>C:\\ies-testing</b>; gantikan dengan folder pilihan anda (yang penting: <b>laluan pendek, TIADA space</b>).</p>
    <h2>0 · Muat turun skrip</h2>
    ${langkah0}
    <h2>1 · Susun fail (WAJIB — jangan run dari Downloads)</h2>
    <div class="step"><ul>
      <li>Buat satu folder kerja tetap, contoh: <b>C:\\ies-testing</b> (laluan pendek, tiada space — path panjang/berspace kerap memecahkan alat command line).</li>
      <li>Pergi ke <b>Downloads</b> → klik-kanan zip → <b>Extract All...</b> → sasarkan folder kerja tadi.</li>
      <li>Hasil: <b>C:\\ies-testing\\${skrip}\\</b> berisi config.py, pages\\, tests\\, testdata\\, tools\\.</li>
      <li>Jangan run terus dari dalam zip atau dari Downloads — extract dahulu.</li></ul>
      ${cmd('mkdir C:\\ies-testing')}</div>
    <h2>2 · Pasang alat (sekali sahaja setiap komputer)</h2>
    <div class="step"><ul>
      <li><b>Python 3.11+</b> (tick "Add to PATH" semasa pasang) dan <b>Node.js LTS</b>.</li>
      <li>Appium + driver Android: lihat command di bawah.</li>
      <li><b>adb</b> (Android platform-tools) dalam PATH.</li>
      <li>Langkah pemasangan penuh bergambar: sidebar → <b>TUTORIALS</b>.</li></ul>
      ${cmd('npm install -g appium')}${cmd('appium driver install uiautomator2')}</div>
    <h2>3 · Pasang dependencies skrip (sekali setiap folder)</h2>
    <div class="step">${cmd('cd C:\\ies-testing\\'+skrip)}${cmd('pip install -r requirements.txt')}</div>
    <h2>4 · Sedia peranti</h2>
    <div class="step"><ul>
      <li>Telefon: USB debugging ON, APK ${pbt} dipasang, auto-lock OFF, kekal bersambung USB.</li>
      <li>Printer Bixolon berpasangan Bluetooth &amp; hidup (untuk TC cetak).</li>
      <li>Sahkan telefon dikesan:</li></ul>
      ${cmd('adb devices')}</div>
    <h2>5 · Appium — Terminal 1 (biar terbuka)</h2>
    <div class="step">${cmd('appium')}</div>
    <h2>6 · Run — Terminal 2</h2>
    <div class="step">${cmd('cd C:\\ies-testing\\'+skrip)}${ekstra}${cmd(runcmd)}</div>
    <h2>7 · Baca hasil</h2>
    <div class="step"><p>Laporan dalam <b>${skrip}\\reports\\</b>. Untuk memasukkan run ke papan ini: salin fail run JSON ke <b>laporan\\data\\${pbt}\\runs\\</b> kemudian refresh browser.</p></div>
  </div></div>`;
}

'''

t = t[:i] + BARU + t[j:]
p.write_text(t, encoding="utf-8")
print("PATCH3-OK", p)
