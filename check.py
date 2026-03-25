with open('list.txt') as f:
    ids = [line.strip() for line in f if line.strip()]

import os
missing = []
for id in ids:
    if not os.path.exists(f"title/{id}.en.txt"): missing.append(f"title/{id}.en.txt")
    if not os.path.exists(f"title/{id}.ja.txt"): missing.append(f"title/{id}.ja.txt")

if missing:
    print(f"Missing files: {missing}")
else:
    print(f"Success: All {len(ids)*2} files exist.")
