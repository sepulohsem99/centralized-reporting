#!/usr/bin/env python3
"""PASANG REPO — cipta repo GitHub `centralized-reporting` (private,
akaun sepulohsem99) dan push folder laporan buat kali pertama.

Dijalankan di WINDOWS pemilik (via jambatan) — menggunakan kredential
GitHub yang SEDIA TERSIMPAN dalam Git Credential Manager (yang sama
dipakai untuk push mbip-pipeline-dashboard). Token TIDAK dicetak.
"""
import json
import subprocess
import sys
import urllib.request
import urllib.error
from pathlib import Path

LAPORAN = Path(r"C:\Users\mrsai\Desktop"
               r"\CENTRALIZED REPORTING AI CENTRIC TESTING\laporan")
REPO = "centralized-reporting"
AKAUN = "sepulohsem99"
REMOTE = f"https://github.com/{AKAUN}/{REPO}.git"


def sh(*args, cwd=None, ok_codes=(0,), senyap=False):
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    if r.returncode not in ok_codes:
        print(f"[GAGAL] {' '.join(args[:3])}...: "
              f"{(r.stderr or r.stdout)[:300]}")
        sys.exit(1)
    if not senyap and (r.stdout or "").strip():
        print(r.stdout.strip()[:300])
    return r


def kredential():
    r = subprocess.run(["git", "credential", "fill"],
                       input="protocol=https\nhost=github.com\n\n",
                       capture_output=True, text=True)
    d = dict(ln.split("=", 1) for ln in r.stdout.splitlines()
             if "=" in ln)
    if not d.get("password"):
        print("[GAGAL] tiada kredential github.com tersimpan")
        sys.exit(1)
    return d["username"], d["password"]


def cipta_repo(token):
    req = urllib.request.Request(
        "https://api.github.com/user/repos",
        data=json.dumps({"name": REPO, "private": True,
                         "description": "Centralized Reporting — "
                                        "AI Centric Testing"}
                        ).encode(),
        headers={"Authorization": "token " + token,
                 "Accept": "application/vnd.github+json",
                 "User-Agent": "laporan-berpusat"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            j = json.loads(r.read())
            print(f"[REPO] dicipta: {j.get('full_name')} (private)")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:200]
        if e.code == 422 and "already exists" in body:
            print(f"[REPO] {AKAUN}/{REPO} sudah wujud — teruskan")
        else:
            print(f"[GAGAL] cipta repo: HTTP {e.code}: {body}")
            sys.exit(1)


def main():
    print("== PASANG REPO LAPORAN BERPUSAT ==")
    # 1) jana public/ segar (zip skrip sebenar di Windows).
    sh(sys.executable, str(LAPORAN / "jana_statik.py"), cwd=str(LAPORAN))
    # 2) cipta repo (idempoten).
    user, token = kredential()
    print(f"[KREDENTIAL] github.com sebagai: {user}")
    cipta_repo(token)
    # 3) git init/push.
    if not (LAPORAN / ".git").exists():
        sh("git", "init", cwd=str(LAPORAN), senyap=True)
        print("[GIT] repo diinit")
    sh("git", "-C", str(LAPORAN), "branch", "-M", "main", senyap=True)
    r = subprocess.run(["git", "-C", str(LAPORAN), "remote", "get-url",
                        "origin"], capture_output=True, text=True)
    if r.returncode != 0:
        sh("git", "-C", str(LAPORAN), "remote", "add", "origin", REMOTE,
           senyap=True)
    else:
        sh("git", "-C", str(LAPORAN), "remote", "set-url", "origin",
           REMOTE, senyap=True)
    print(f"[GIT] remote: {REMOTE}")
    sh("git", "-C", str(LAPORAN), "add", "-A", senyap=True)
    subprocess.run(["git", "-C", str(LAPORAN), "commit", "-m",
                    "Laporan berpusat: init"],
                   capture_output=True, text=True)  # ok jika tiada beza
    sh("git", "-C", str(LAPORAN), "push", "-u", "origin", "main")
    print("== SIAP: kod di https://github.com/" + AKAUN + "/" + REPO +
          " — seterusnya sambung Cloudflare Pages ==")
    return 0


if __name__ == "__main__":
    sys.exit(main())
