import os

with open('list.txt', 'r') as f:
    ids = [line.strip() for line in f if line.strip()]

for id_val in ids:
    en_crit_path = f"critique/{id_val}.en.txt"
    if os.path.exists(en_crit_path):
        with open(en_crit_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # extract first paragraph or lines under "2. Description"
            desc = ""
            for i, line in enumerate(lines):
                if "2. Description" in line or "Description" in line:
                    desc = lines[i+1].strip()
                    if not desc and i+2 < len(lines):
                        desc = lines[i+2].strip()
                    break
            if not desc and lines:
                desc = lines[0].strip()
            print(f"ID: {id_val} | Desc: {desc[:150]}")
