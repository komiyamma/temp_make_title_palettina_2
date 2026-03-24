import os
import google.generativeai as genai

# NOTE: API key should be set in environment variable GEMINI_API_KEY
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def generate_title(image_path, tags_path, critique_path, lang):
    with open(tags_path, "r", encoding="utf-8") as f:
        tags = f.read()
    with open(critique_path, "r", encoding="utf-8") as f:
        critique = f.read()

    # Read image
    image = genai.upload_file(image_path)

    model = genai.GenerativeModel('gemini-1.5-pro')

    if lang == "en":
        prompt = f"""
Based on the provided image, tags, and critique, create the most heart-touching title for this painting in English.
Do NOT create an objective title like "Landscape of XX" as a third party would.
Create a subjective, heart-touching title that the artist themselves might give, one that maximizes the charm of the painting.
The title should be of a reasonable length for a painting title.
Output ONLY the title string.

Tags:
{tags}

Critique:
{critique}
"""
    elif lang == "ja":
        prompt = f"""
提供された画像、タグ、批評文を基に、この絵画の魅力を最大限に引き出す、人々の心を打つような日本語のタイトルを1つ作成してください。
第三者が付けたような「◯◯の風景」といった客観的なタイトルではなく、作者自身が付けそうな主観的で心に響くタイトルにしてください。
絵画のタイトルとして常識的な長さの範囲内にしてください。
出力はタイトルの文字列のみにしてください。

Tags:
{tags}

Critique:
{critique}
"""

    response = model.generate_content([prompt, image])
    return response.text.strip()

def process_list(list_file):
    with open(list_file, "r") as f:
        ids = [line.strip() for line in f if line.strip()]

    for id in ids:
        print(f"Processing {id}...")

        # English
        en_tags = f"tags/{id}.en.txt"
        en_critique = f"critique/{id}.en.txt"
        image_path = f"picture/{id}.png"
        en_title_out = f"title/{id}.en.txt"

        if os.path.exists(en_tags) and os.path.exists(en_critique) and os.path.exists(image_path):
            title = generate_title(image_path, en_tags, en_critique, "en")
            with open(en_title_out, "w", encoding="utf-8") as f:
                f.write(title)
            print(f"  Saved {en_title_out}")
        else:
            print(f"  Missing files for English title of {id}")

        # Japanese
        ja_tags = f"tags/{id}.ja.txt"
        ja_critique = f"critique/{id}.ja.txt"
        ja_title_out = f"title/{id}.ja.txt"

        if os.path.exists(ja_tags) and os.path.exists(ja_critique) and os.path.exists(image_path):
            title = generate_title(image_path, ja_tags, ja_critique, "ja")
            with open(ja_title_out, "w", encoding="utf-8") as f:
                f.write(title)
            print(f"  Saved {ja_title_out}")
        else:
            print(f"  Missing files for Japanese title of {id}")

if __name__ == "__main__":
    process_list("list.txt")
