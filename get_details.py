import sys
ids = sys.argv[1:]
for id_val in ids:
    print(f"--- {id_val} ---")
    en_crit_path = f"critique/{id_val}.en.txt"
    if True: # os.path.exists
        with open(en_crit_path, 'r', encoding='utf-8') as f:
            for line in f:
                if "2. Description" in line or "3. Analysis" in line or "4. Interpretation" in line:
                    continue
                if line.strip() and not line.startswith(str(1)) and not line.startswith(str(2)) and not line.startswith(str(3)) and not line.startswith(str(4)) and not line.startswith(str(5)):
                    print(line.strip()[:100])
