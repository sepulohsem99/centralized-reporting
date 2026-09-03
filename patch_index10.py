#!/usr/bin/env python3
"""Patch #10 index.html: ganti lukisan garis dengan ilustrasi gaya
CLIP-ART flat design BERANIMASI (bentuk berisi, bayang, warna; kertas
resit keluar, Bluetooth berdenyut, kursor berkelip, device terapung)."""
import sys
from pathlib import Path

p = Path(sys.argv[1])
t = p.read_text(encoding="utf-8")

if "@keyframes apung" in t:
    print("SUDAH-DIPATCH")
    sys.exit(0)

# 1) CSS animasi — masuk sebelum </style>.
css = """
/* --- animasi ilustrasi manual --- */
@keyframes apung{0%,100%{transform:translateY(0)}50%{transform:translateY(-5px)}}
@keyframes apung2{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}
@keyframes kelip{0%,49%{opacity:1}50%,100%{opacity:0}}
@keyframes denyut{0%,100%{opacity:.15}50%{opacity:.9}}
@keyframes cetak{0%{transform:translateY(-26px)}70%{transform:translateY(0)}100%{transform:translateY(0)}}
@keyframes led{0%,100%{opacity:.3}50%{opacity:1}}
.il-a1{animation:apung 4s ease-in-out infinite}
.il-a2{animation:apung2 4.6s ease-in-out .6s infinite}
.il-a3{animation:apung 5s ease-in-out 1.1s infinite}
.il-kelip{animation:kelip 1.1s steps(1) infinite}
.il-bt1{animation:denyut 2s ease-in-out infinite}
.il-bt2{animation:denyut 2s ease-in-out .4s infinite}
.il-cetak{animation:cetak 3.2s ease-in-out infinite}
.il-led{animation:led 1.6s ease-in-out infinite}
"""
if "</style>" not in t:
    sys.exit("TAK JUMPA </style>")
t = t.replace("</style>", css + "</style>", 1)

# 2) Ganti fungsi ilustrasiHardware sepenuhnya.
MULA = "function ilustrasiHardware(){"
TAMAT = "function manualHtml(pbt){"
i = t.find(MULA)
j = t.find(TAMAT)
if i < 0 or j < 0 or j <= i:
    sys.exit("TAK JUMPA blok ilustrasiHardware")

BARU = r'''function ilustrasiHardware(){
  const lbl='font-size="9" fill="var(--dim)" text-anchor="middle" font-family="Segoe UI,Arial" font-weight="600"';
  return `<div style="margin:8px 0 12px;overflow-x:auto">
  <svg width="470" height="122" viewBox="0 0 470 122" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="gSkrin" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#1e293b"/><stop offset="1" stop-color="#0b1120"/>
      </linearGradient>
      <linearGradient id="gFon" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#34d399"/><stop offset="1" stop-color="#059669"/>
      </linearGradient>
      <linearGradient id="gPrn" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#475569"/><stop offset="1" stop-color="#1e293b"/>
      </linearGradient>
    </defs>
    <!-- bayang lantai -->
    <ellipse cx="62" cy="106" rx="46" ry="6" fill="#000" opacity=".28"/>
    <ellipse cx="200" cy="106" rx="26" ry="5" fill="#000" opacity=".28"/>
    <ellipse cx="345" cy="106" rx="44" ry="6" fill="#000" opacity=".28"/>
    <!-- LAPTOP (clip-art flat) -->
    <g class="il-a1">
      <rect x="26" y="22" width="72" height="48" rx="5" fill="#334155"/>
      <rect x="30" y="26" width="64" height="40" rx="3" fill="url(#gSkrin)"/>
      <text x="36" y="40" font-family="Consolas,monospace" font-size="8" fill="#4ade80">&gt; appium</text>
      <text x="36" y="52" font-family="Consolas,monospace" font-size="8" fill="#4ade80">&gt; run</text>
      <rect class="il-kelip" x="58" y="46" width="5" height="7" fill="#4ade80"/>
      <path d="M18 78 L106 78 L96 70 L28 70 Z" fill="#64748b"/>
      <path d="M18 78 L106 78 L106 81 L18 81 Z" fill="#475569"/>
      <rect x="54" y="72" width="16" height="4" rx="2" fill="#94a3b8"/>
    </g>
    <text x="62" y="119" ${lbl}>Laptop · Appium</text>
    <!-- kabel USB -->
    <path d="M106 74 C 140 74, 150 60, 178 56" stroke="#64748b" stroke-width="3" fill="none" stroke-linecap="round"/>
    <rect x="102" y="70" width="10" height="8" rx="2" fill="#94a3b8"/>
    <text x="142" y="52" ${lbl}>USB</text>
    <!-- TELEFON (clip-art flat) -->
    <g class="il-a2">
      <rect x="180" y="24" width="40" height="74" rx="8" fill="#0f172a" stroke="#334155" stroke-width="2"/>
      <rect x="185" y="32" width="30" height="54" rx="3" fill="url(#gFon)"/>
      <rect x="189" y="37" width="22" height="7" rx="2" fill="#ffffff" opacity=".9"/>
      <rect x="189" y="48" width="22" height="4" rx="2" fill="#065f46"/>
      <rect x="189" y="55" width="22" height="4" rx="2" fill="#065f46"/>
      <rect x="189" y="62" width="14" height="4" rx="2" fill="#065f46"/>
      <rect x="189" y="72" width="22" height="9" rx="2" fill="#f59e0b"/>
      <rect x="194" y="27" width="12" height="3" rx="1.5" fill="#334155"/>
      <circle cx="200" cy="92" r="3" fill="#334155"/>
    </g>
    <text x="200" y="119" ${lbl}>Phone · IES</text>
    <!-- gelombang Bluetooth -->
    <g stroke="#38bdf8" stroke-width="2.5" fill="none" stroke-linecap="round">
      <path class="il-bt1" d="M240 52 a14 14 0 0 1 0 24"/>
      <path class="il-bt2" d="M250 44 a26 26 0 0 1 0 40"/>
    </g>
    <text x="256" y="30" ${lbl}>Bluetooth</text>
    <!-- PRINTER BIXOLON (clip-art flat) -->
    <g class="il-a3">
      <!-- kertas resit beranimasi (di belakang badan) -->
      <g clip-path="url(#klipKertas)">
        <g class="il-cetak">
          <rect x="318" y="30" width="46" height="34" rx="2" fill="#f8fafc"/>
          <rect x="323" y="36" width="36" height="3" rx="1.5" fill="#cbd5e1"/>
          <rect x="323" y="42" width="28" height="3" rx="1.5" fill="#cbd5e1"/>
          <rect x="323" y="48" width="36" height="3" rx="1.5" fill="#cbd5e1"/>
          <rect x="323" y="54" width="20" height="3" rx="1.5" fill="#cbd5e1"/>
        </g>
      </g>
      <clipPath id="klipKertas"><rect x="316" y="28" width="50" height="40"/></clipPath>
      <!-- badan printer -->
      <rect x="304" y="58" width="82" height="40" rx="8" fill="url(#gPrn)"/>
      <rect x="304" y="58" width="82" height="12" rx="6" fill="#334155"/>
      <rect x="314" y="62" width="54" height="5" rx="2.5" fill="#0f172a"/>
      <circle class="il-led" cx="376" cy="64" r="3.5" fill="#4ade80"/>
      <rect x="312" y="78" width="30" height="12" rx="3" fill="#0f172a"/>
      <text x="327" y="87" font-size="7" fill="#94a3b8" text-anchor="middle" font-family="Segoe UI,Arial" font-weight="700">SPP-R410</text>
    </g>
    <text x="345" y="119" ${lbl}>Printer Bixolon</text>
  </svg></div>`;
}
'''
t = t[:i] + BARU + t[j:]
p.write_text(t, encoding="utf-8")
print("PATCH10-OK", p)
