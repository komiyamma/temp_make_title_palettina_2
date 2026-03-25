import os
import sys

ids = [
    "1767780598762", "1767781001238", "1767781358993", "1767782397742",
    "1767782401655", "1767782405344", "1767784480700", "1767784485527",
    "1767784490115", "1767784503702", "1767784505663", "1767784510123",
    "1767784514525", "1767785186669", "1767800760296"
]

for iid in ids:
    print(f"=== ID: {iid} ===")

    # JA
    ja_tags = ""
    ja_tags_path = f"tags/{iid}.ja.txt"
    if os.path.exists(ja_tags_path):
        with open(ja_tags_path, 'r', encoding='utf-8') as f:
            ja_tags = ",".join([line.strip() for line in f if line.strip()])

    ja_crit = ""
    ja_crit_path = f"critique/{iid}.ja.txt"
    if os.path.exists(ja_crit_path):
        with open(ja_crit_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
            ja_crit = " ".join(lines[:3]) # 冒頭のみ

    print(f"JA Tags: {ja_tags}")

    # EN
    en_tags = ""
    en_tags_path = f"tags/{iid}.en.txt"
    if os.path.exists(en_tags_path):
        with open(en_tags_path, 'r', encoding='utf-8') as f:
            en_tags = ",".join([line.strip() for line in f if line.strip()])

    print(f"EN Tags: {en_tags}")
    print()
