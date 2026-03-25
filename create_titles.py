import os

titles = {
    "1767930826381": {
        "en": "Whispers of the Forest Stream",
        "ja": "森のせせらぎが囁くとき"
    },
    "1767930836728": {
        "en": "Golden Reverie by the Sea",
        "ja": "海鳴りと黄金色の追憶"
    },
    "1767930844473": {
        "en": "Echoes of a Sunlit Afternoon",
        "ja": "陽光に溶けゆく午後の語らい"
    },
    "1767957137454": {
        "en": "Night's Golden Bloom",
        "ja": "夜空に咲く黄金の華"
    },
    "1767966154072": {
        "en": "Crimson Silence and the Glowing Mirror",
        "ja": "深紅の静寂、鏡に映る想い"
    },
    "1767966157778": {
        "en": "Sails of the Setting Sun",
        "ja": "落日が染める湖面の帆"
    },
    "1768014973573": {
        "en": "Campfire Embers at the Edge of the World",
        "ja": "世界の果てで燃える焚き火"
    },
    "1768014977941": {
        "en": "Roar of the Untamed Sea",
        "ja": "荒ぶる海の咆哮"
    },
    "1768014981249": {
        "en": "Drifting in the Golden Haze",
        "ja": "黄金色のまどろみに揺られて"
    },
    "1768014985080": {
        "en": "Farewell to the Golden Port",
        "ja": "黄金の港に別れを告げて"
    },
    "1768014990773": {
        "en": "Pearls and the Distant Tide",
        "ja": "真珠の輝きと遠い潮騒"
    },
    "1768014996614": {
        "en": "Neon Rhythms of Yesteryear",
        "ja": "ネオンが刻む過ぎ去りし日のリズム"
    },
    "1768015002398": {
        "en": "Terrace Memories in the Fading Light",
        "ja": "夕闇に溶けるテラスの記憶"
    },
    "1768015009868": {
        "en": "Iron Giants in the Twilight",
        "ja": "黄昏にそびえる鉄の巨人たち"
    },
    "1768015014804": {
        "en": "Slumber of the Clockwork Soul",
        "ja": "からくり仕掛けの魂が眠る場所"
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
