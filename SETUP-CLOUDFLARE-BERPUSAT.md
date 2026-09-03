# SETUP CLOUDFLARE PAGES — LAPORAN BERPUSAT (sekali sahaja)

Corak sama seperti dashboard v3 (`mbip-pipeline-dashboard`). Selepas
setup, setiap kemaskini hanya perlu `publish.bat`.

> **PENTING — KREDENTIAL:** `public/skrip/*.zip` mengandungi
> kredential ujian PBT (pilihan pemilik 2026-09-03). **Cloudflare
> Access WAJIB dipasang (Langkah 4) SEBELUM kongsi URL.** Fail
> `_headers` sudah menghalang pengindeksan enjin carian.

## 1 · Buat repo GitHub kosong

Login GitHub → New repository → nama: `centralized-reporting`
(Private disyorkan) → Create. JANGAN tambah README.

Akaun: yang terbukti di mesin ini ialah `sepulohsem99` (dipakai untuk
mbip-pipeline-dashboard). Kalau mahu guna akaun lain (cth. neurodata),
cuma tukar nama akaun dalam URL remote di bawah.

## 2 · Jadikan folder laporan repo git & push pertama

Dalam terminal:

```
cd "C:\Users\mrsai\Desktop\CENTRALIZED REPORTING AI CENTRIC TESTING\laporan"
python jana_statik.py
git init
git add -A
git commit -m "Laporan berpusat: init"
git branch -M main
git remote add origin https://github.com/sepulohsem99/centralized-reporting.git
git push -u origin main
```

(Ganti `sepulohsem99` dengan `neurodata` jika guna akaun itu.)

## 3 · Sambung ke Cloudflare Pages

1. dash.cloudflare.com → **Workers & Pages** → **Create** → **Pages**
   → **Connect to Git**.
2. Pilih repo `centralized-reporting`.
3. Tetapan build:
   - Framework preset: **None**
   - Build command: *(kosongkan)*
   - Build output directory: **public**
4. **Save and Deploy**. URL live: `https://<projek>.pages.dev`.

## 4 · Cloudflare Access (WAJIB — kredential dalam zip)

1. dash.cloudflare.com → **Zero Trust** → **Access** → **Applications**
   → **Add an application** → **Self-hosted**.
2. Application domain: `<projek>.pages.dev` (semua laluan `/*`).
3. Policy: Allow → Include → **Emails** → senaraikan email team.
4. Save. Sesiapa buka URL kena login OTP email dahulu — sama seperti
   dashboard v3.

## Selepas setup — kemaskini harian

```
cd "C:\Users\mrsai\Desktop\CENTRALIZED REPORTING AI CENTRIC TESTING\laporan"
publish.bat
```

## Apa yang berbeza pada versi awam (statik)

- Data run dibakar dalam HTML — untuk data terbaru, jalankan
  `publish.bat` semula selepas run baharu.
- Chip atas kanan tulis **STATIC** (bukan LIVE).
- Tab **Ganti Nilai** dimatikan — ia perlukan server localhost
  (`python serve.py`).
- Butang zip skrip & PDF manual berfungsi (fail statik pra-jana).
