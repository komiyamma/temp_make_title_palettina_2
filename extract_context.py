import os

ids = []
with open('list.txt', 'r') as f:
    for line in f:
        line = line.strip()
        if line:
            ids.append(line)

with open('context_dump.txt', 'w', encoding='utf-8') as out:
    for id_val in ids:
        out.write(f"=== ID: {id_val} ===\n")

        en_tags_path = f"tags/{id_val}.en.txt"
        if os.path.exists(en_tags_path):
            with open(en_tags_path, 'r', encoding='utf-8') as f:
                out.write(f"[EN Tags]\n{f.read()}\n")

        en_critique_path = f"critique/{id_val}.en.txt"
        if os.path.exists(en_critique_path):
            with open(en_critique_path, 'r', encoding='utf-8') as f:
                out.write(f"[EN Critique]\n{f.read()}\n")

        ja_tags_path = f"tags/{id_val}.ja.txt"
        if os.path.exists(ja_tags_path):
            with open(ja_tags_path, 'r', encoding='utf-8') as f:
                out.write(f"[JA Tags]\n{f.read()}\n")

        ja_critique_path = f"critique/{id_val}.ja.txt"
        if os.path.exists(ja_critique_path):
            with open(ja_critique_path, 'r', encoding='utf-8') as f:
                out.write(f"[JA Critique]\n{f.read()}\n")

        out.write("\n")
