"""
Supabase DATABASE_URL setup helper.

Naya database password maangta hai (hidden input), sahi pooler host
khud detect karta hai, .env update karta hai, aur connection verify karta hai.

Run:  ./venv/bin/python setup_db_url.py
"""
import getpass
import pathlib
import re
import sys
from urllib.parse import quote

import psycopg2

PROJECT_REF = "axxclwrwuqmhaubzsphe"
REGION = "ap-northeast-1"
ENV_PATH = pathlib.Path(__file__).parent / ".env"

CANDIDATE_HOSTS = [
    f"aws-0-{REGION}.pooler.supabase.com",
    f"aws-1-{REGION}.pooler.supabase.com",
]


def build_url(host, password):
    user = quote(f"postgres.{PROJECT_REF}")
    return f"postgresql://{user}:{quote(password, safe='')}@{host}:5432/postgres"


def try_connect(url):
    conn = psycopg2.connect(url, connect_timeout=15)
    cur = conn.cursor()
    cur.execute("select count(*) from colleges;")
    total = cur.fetchone()[0]
    cur.execute("select count(*) from colleges where embedding is not null;")
    embedded = cur.fetchone()[0]
    cur.close()
    conn.close()
    return total, embedded


def update_env(url):
    if not ENV_PATH.exists():
        print(f"!! {ENV_PATH} nahi mila")
        return
    text = ENV_PATH.read_text()
    if re.search(r"^DATABASE_URL=.*$", text, flags=re.M):
        text = re.sub(r"^DATABASE_URL=.*$", f"DATABASE_URL={url}", text, flags=re.M)
    else:
        text = text.rstrip() + f"\nDATABASE_URL={url}\n"
    ENV_PATH.write_text(text)
    print(f"✅ .env updated ({ENV_PATH})")


def main():
    print("Supabase ka NAYA database password paste kar (screen pe nahi dikhega):")
    password = getpass.getpass("Password: ").strip()
    if not password:
        print("Khaali password. Abort.")
        sys.exit(1)

    for host in CANDIDATE_HOSTS:
        print(f"\nTrying {host} ...")
        url = build_url(host, password)
        try:
            total, embedded = try_connect(url)
        except psycopg2.OperationalError as e:
            msg = str(e).strip().splitlines()[0]
            print(f"  ❌ {msg}")
            continue

        print(f"  ✅ Connected!")
        print(f"     colleges        : {total:,}")
        print(f"     with embeddings : {embedded:,}")
        update_env(url)
        print("\nAgla step: yahi URL Streamlit Cloud secrets aur GitHub secret me bhi daal.")
        print("Print karne ke liye:  grep '^DATABASE_URL=' .env")
        return

    print("\n❌ Dono pooler hosts fail ho gaye.")
    print("   Password galat ho sakta hai, ya Connect modal se exact URI copy karke")
    print("   seedha .env me paste kar de.")
    sys.exit(1)


if __name__ == "__main__":
    main()
