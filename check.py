import os
import sys

with open("list.txt", "r") as f:
    ids = [line.strip() for line in f if line.strip()]

missing = []
for iid in ids:
    ja_path = f"title/{iid}.ja.txt"
    en_path = f"title/{iid}.en.txt"
    if not os.path.exists(ja_path):
        missing.append(ja_path)
    if not os.path.exists(en_path):
        missing.append(en_path)

if missing:
    print("Missing files:")
    for m in missing:
        print(m)
else:
    print("All files present.")
