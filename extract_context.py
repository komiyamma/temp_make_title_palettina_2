import os
import glob
from collections import defaultdict

def extract_data():
    with open('list.txt', 'r', encoding='utf-8') as f:
        target_ids = [line.strip() for line in f if line.strip()]

    for id_ in target_ids:
        # We need to collect tags and critique for both en and ja
        print(f"--- ID: {id_} ---")

        for lang in ['en', 'ja']:
            tags_file = f"tags/{id_}.{lang}.txt"
            critique_file = f"critique/{id_}.{lang}.txt"

            tags_content = ""
            critique_content = ""
            if os.path.exists(tags_file):
                with open(tags_file, 'r', encoding='utf-8') as f:
                    tags_content = f.read().replace('\n', ' ')
            if os.path.exists(critique_file):
                with open(critique_file, 'r', encoding='utf-8') as f:
                    # just get the first bit of critique for context
                    critique_content = f.read()[:500].replace('\n', ' ')

            print(f"[{lang.upper()}] Tags: {tags_content[:100]}...")
            print(f"[{lang.upper()}] Critique: {critique_content[:150]}...")

if __name__ == '__main__':
    extract_data()