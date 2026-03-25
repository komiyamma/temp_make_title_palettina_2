import os

titles = {
    "1768015025038": {
        "en": "Whispers of the Canvas",
        "ja": "アトリエの息遣い"
    },
    "1768015029835": {
        "en": "Kaleidoscope of the Forgotten Realm",
        "ja": "忘れられた領域の万華鏡"
    },
    "1768015034603": {
        "en": "Tears of the Prismatic Night",
        "ja": "虹色の夜が流す涙"
    },
    "1768015041294": {
        "en": "Echoes of a Jeweled Festivity",
        "ja": "宝石の祝祭が残した木霊"
    },
    "1768015053813": {
        "en": "Embrace of the Sapphire Horizon",
        "ja": "蒼き水平線の抱擁"
    },
    "1768015060509": {
        "en": "Dance of the Distorted Spheres",
        "ja": "歪んだ次元の舞踏"
    },
    "1768015066122": {
        "en": "Soul of the Silent Mannequin",
        "ja": "静かなる人形の魂"
    },
    "1768015070621": {
        "en": "Symphony of the Gilded Glass",
        "ja": "黄金のガラスが奏でる交響曲"
    },
    "1768015081091": {
        "en": "Sanctuary of the Sunlit Arches",
        "ja": "陽光とアーチの聖域"
    },
    "1768015083753": {
        "en": "Reverie of the Mosaic Bloom",
        "ja": "モザイクの花が視る夢"
    },
    "1768015142952": {
        "en": "Secrets of the Azure Grotto",
        "ja": "蒼海が隠す洞窟の秘密"
    },
    "1768015151865": {
        "en": "Slumber of the Alpine Giants",
        "ja": "高き峰々の微睡み"
    },
    "1768015157963": {
        "en": "Awakening of the Pink Snows",
        "ja": "薄紅の雪の目覚め"
    },
    "1768015165076": {
        "en": "Golden Sighs of the Autumn Lake",
        "ja": "秋の湖面がこぼす黄金の溜息"
    },
    "1768015170416": {
        "en": "Farewell of the Golden Hour",
        "ja": "黄金の刻の別れ"
    }
}

def main():
    # Only process IDs strictly present in list.txt
    with open('list.txt', 'r', encoding='utf-8') as f:
        valid_ids = [line.strip() for line in f if line.strip()]

    os.makedirs('title', exist_ok=True)

    for vid in valid_ids:
        if vid in titles:
            en_path = f"title/{vid}.en.txt"
            ja_path = f"title/{vid}.ja.txt"

            with open(en_path, 'w', encoding='utf-8') as f_en:
                f_en.write(titles[vid]["en"])

            with open(ja_path, 'w', encoding='utf-8') as f_ja:
                f_ja.write(titles[vid]["ja"])
        else:
            print(f"Warning: No title data generated for {vid}")

if __name__ == '__main__':
    main()
