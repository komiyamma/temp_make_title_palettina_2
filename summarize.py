import sys, os

with open('list.txt') as f:
    ids = [line.strip() for line in f if line.strip()]

for id in ids:
    with open(f"tags/{id}.en.txt") as f:
        tags_en = ", ".join([l.strip() for l in f][:5])
    with open(f"tags/{id}.ja.txt") as f:
        tags_ja = ", ".join([l.strip() for l in f][:5])

    with open(f"critique/{id}.en.txt") as f:
        critique_en = f.read()
        desc_en = critique_en.split("2. Description")[1].split("3. Analysis")[0].strip()[:200]
    with open(f"critique/{id}.ja.txt") as f:
        critique_ja = f.read()
        desc_ja = critique_ja.split("2. 記述")[1].split("3. 分析")[0].strip()[:200]

    print(f"ID: {id}")
    print(f"  EN Tags: {tags_en}")
    print(f"  EN Desc: {desc_en}...")
    print(f"  JA Tags: {tags_ja}")
    print(f"  JA Desc: {desc_ja}...")
    print("-" * 40)
