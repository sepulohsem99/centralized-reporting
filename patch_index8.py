#!/usr/bin/env python3
"""Patch #8 index.html: Manual User -> flow diagram interaktif.
Rantai nod 0-7 (SETUP sekali / RUN setiap kali) di atas; klik nod
memaparkan detail SATU langkah sahaja — tiada lagi dinding teks."""
import sys
from pathlib import Path

p = Path(sys.argv[1])
t = p.read_text(encoding="utf-8")

if "function pickStep" in t:
    print("SUDAH-DIPATCH")
    sys.exit(0)

# state + pemilih langkah (di sebelah pickTab).
sasar = "function pickTab(t){ sel.tab=t; render(); }"
if sasar not in t:
    sys.exit("TAK JUMPA pickTab")
t = t.replace(sasar, sasar +
              "\nlet mstep=0;\nfunction pickStep(i){ mstep=i; render(); }")

MULA = "function manualHtml(pbt){"
TAMAT = "function fmtDT("
i = t.find(MULA)
j = t.find(TAMAT)
if i < 0 or j < 0 or j <= i:
    sys.exit("TAK JUMPA blok manualHtml")
k = t.rfind("/*", 0, i)
if k >= 0 and "MANUAL USER" in t[k:i]:
    i = k

BARU = r'''/* ------------- MANUAL USER (flow diagram interaktif, BM/EN) ------ */
function manualHtml(pbt){
  const skrip=pbt+'-skrip';
  const adaZip=['MBPG','MBIP'].includes(pbt);
  const runcmd={MBPG:'python tools\\run_penuh.py --borang NPK',
                MBIP:'python tools\\run_penuh_mbip.py --profil mbip-production --terus',
                MBJB:'python tools\\run_and_report.py'}[pbt]||'python tools\\run_and_report.py';
  const btnZip= adaZip
    ? `<a href="/api/skrip/${pbt}" style="display:inline-block;background:var(--panel2);border:1px solid var(--pass);color:var(--pass);border-radius:8px;padding:7px 14px;font-size:.68rem;font-weight:600;text-decoration:none">⬇ ${tr('MUAT TURUN SKRIP','DOWNLOAD SCRIPT')}</a>`
    : `<span style="font-size:.68rem;color:var(--dim)">${tr('Zip '+pbt+' belum tersedia.','The '+pbt+' zip is not available yet.')}</span>`;
  const btnPdf= adaZip
    ? `<a href="/manual/MANUAL-USER-${pbt}.pdf" style="display:inline-flex;align-items:center;gap:7px;background:var(--panel2);border:1px solid #ef4444;color:#ef4444;border-radius:8px;padding:7px 14px;font-size:.68rem;font-weight:600;text-decoration:none"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>PDF</a>`
    : '';

  // 8 langkah: {tajuk BM, tajuk EN, badan()}
  const steps=[
    {b:'Muat turun',e:'Download',h:()=>`${btnZip}<p style="margin-top:8px">${tr('Zip masuk ke folder <b>Downloads</b>.','The zip lands in your <b>Downloads</b> folder.')}</p>`},
    {b:'Susun fail',e:'Organize',h:()=>`${cmd('mkdir C:\\ies-testing')}<p>${tr('Downloads → klik-kanan zip → <b>Extract All</b> → ke <b>C:\\ies-testing</b>. Jangan run dari Downloads/dalam zip.','Downloads → right-click the zip → <b>Extract All</b> → into <b>C:\\ies-testing</b>. Never run from Downloads or inside the zip.')}</p>`},
    {b:'Pasang alat',e:'Install tools',h:()=>`<p>${tr('Python 3.11+ · Node.js LTS · adb dalam PATH. Detail: sidebar → <b>TUTORIALS</b>.','Python 3.11+ · Node.js LTS · adb on PATH. Details: sidebar → <b>TUTORIALS</b>.')}</p>${cmd('npm install -g appium')}${cmd('appium driver install uiautomator2')}`},
    {b:'Dependencies',e:'Dependencies',h:()=>`${cmd('cd C:\\ies-testing\\'+skrip)}${cmd('pip install -r requirements.txt')}`},
    {b:'Peranti',e:'Devices',h:()=>`<p>${tr('Telefon: USB debugging ON, APK '+pbt+' dipasang. Printer Bixolon ON.','Phone: USB debugging ON, '+pbt+' APK installed. Bixolon printer ON.')}</p>${cmd('adb devices')}`},
    {b:'Appium',e:'Appium',h:()=>`<p>${tr('Terminal 1 — biar terbuka.','Terminal 1 — leave it open.')}</p>${cmd('appium')}`},
    {b:'Run',e:'Run',h:()=>`<p>Terminal 2:</p>${cmd('cd C:\\ies-testing\\'+skrip)}${pbt==='MBPG'?cmd('$env:MBPG_IZIN_PRODUCTION = "1"'):''}${cmd(runcmd)}`},
    {b:'Hasil',e:'Results',h:()=>`<p>${tr('Laporan: <b>'+skrip+'\\reports\\</b>. Masuk papan ini: salin run JSON → <b>laporan\\data\\'+pbt+'\\runs\\</b> → refresh.','Reports: <b>'+skrip+'\\reports\\</b>. To show a run here: copy the run JSON → <b>laporan\\data\\'+pbt+'\\runs\\</b> → refresh.')}</p>`},
  ];
  if(mstep<0||mstep>=steps.length) mstep=0;

  const nod=(idx)=>{
    const s=steps[idx], on=idx===mstep;
    return `<div onclick="pickStep(${idx})" style="display:flex;flex-direction:column;align-items:center;gap:5px;cursor:pointer;min-width:74px">
      <div style="width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:.8rem;
        border:2px solid ${on?'var(--cyan)':'var(--line2)'};color:${on?'var(--cyan)':'var(--dim)'};background:${on?'var(--cyan-bg)':'var(--panel2)'}">${idx}</div>
      <div style="font-size:.58rem;letter-spacing:.4px;text-transform:uppercase;color:${on?'var(--ink)':'var(--dimmer)'};text-align:center">${tr(s.b,s.e)}</div></div>`;
  };
  const anak=`<span style="color:var(--dimmer);font-size:.9rem;margin-top:-16px">→</span>`;
  const kump=(tajuk,warna,idxs)=>`
    <div style="display:flex;align-items:center;gap:10px;padding:12px 14px;border:1px dashed ${warna}44;border-radius:12px;position:relative">
      <span style="position:absolute;top:-8px;left:12px;background:var(--panel);padding:0 8px;font-size:.56rem;letter-spacing:1.2px;text-transform:uppercase;color:${warna}">${tajuk}</span>
      ${idxs.map(nod).join(anak)}</div>`;

  const s=steps[mstep];
  return `<div class="panel" style="border-radius:0 9px 9px 9px"><div class="tut">
    <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:14px">
      <h2 style="margin:0">${tr('Manual User','User Manual')} — ${pbt}</h2>
      <span style="flex:1"></span>${btnPdf}
    </div>
    <div style="display:flex;gap:14px;flex-wrap:wrap;margin-bottom:16px">
      ${kump(tr('SETUP — sekali sahaja','SETUP — once only'),'var(--lain)',[0,1,2,3])}
      ${kump(tr('RUN — setiap kali','RUN — every time'),'var(--pass)',[4,5,6,7])}
    </div>
    <div class="step" style="border-left-color:var(--cyan)">
      <h2 style="margin-top:0">${mstep} · ${tr(s.b,s.e)}</h2>
      ${s.h()}
    </div>
    <p style="font-size:.62rem;color:var(--dimmer);margin-top:8px">${tr('Klik nombor di atas untuk langkah lain. Contoh guna C:\\ies-testing — gantikan dengan folder anda (laluan pendek, tiada space).','Click a number above for other steps. Examples use C:\\ies-testing — replace with your own folder (short path, no spaces).')}</p>
  </div></div>`;
}

'''
t = t[:i] + BARU + t[j:]
p.write_text(t, encoding="utf-8")
print("PATCH8-OK", p)
