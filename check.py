import os
with open('list.txt', 'r') as f:
    ids = [line.strip() for line in f if line.strip()]

all_ok = True
for id_val in ids:
    en_path = f"title/{id_val}.en.txt"
    ja_path = f"title/{id_val}.ja.txt"
    if not os.path.exists(en_path):
        print(f"Missing {en_path}")
        all_ok = False
    if not os.path.exists(ja_path):
        print(f"Missing {ja_path}")
        all_ok = False

if all_ok:
    print("All title files exist.")
