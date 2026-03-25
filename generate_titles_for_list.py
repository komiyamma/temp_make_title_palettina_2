import os

titles = {
    "1768015176000": {
        "en": "Whispers of the Windswept Shore",
        "ja": "風濤がさざめく汀の記憶"
    },
    "1768015183227": {
        "en": "Golden Embrace of the Evening Tide",
        "ja": "黄昏の波が抱く黄金色のノスタルジア"
    },
    "1768015188314": {
        "en": "Ember's Solace in the Twilight Wild",
        "ja": "黄昏の荒野に灯る温もりの記憶"
    },
    "1768015193705": {
        "en": "Breath of the Ancient Canopy",
        "ja": "木漏れ日が導く古き森の息吹"
    },
    "1768015199612": {
        "en": "Solitary Steps on the Azure Edge",
        "ja": "蒼の果てを歩む孤独な足跡"
    },
    "1768015205141": {
        "en": "Reverie on the Sunlit Balcony",
        "ja": "陽だまりのテラスが視る夢"
    },
    "1768015210848": {
        "en": "Tears of the Ancient Citadel",
        "ja": "古代の城塞がこぼす黄金の涙"
    },
    "1768015216309": {
        "en": "Sighs of the Hidden Gorge",
        "ja": "秘められし峡谷の静かな溜息"
    },
    "1768015220776": {
        "en": "Symphony of the Crystal Prism",
        "ja": "光のプリズムが奏でる幻影"
    },
    "1768015225801": {
        "en": "Echoes in the Shallow Sapphire",
        "ja": "浅き瑠璃色に響く命の詩"
    },
    "1768015231224": {
        "en": "Sanctuary of the Blooming Path",
        "ja": "花ひらく小径の聖域"
    },
    "1768015237211": {
        "en": "Awakening of the Celestial Lotus",
        "ja": "天上の蓮華が目覚めるとき"
    },
    "1768015243299": {
        "en": "Pulse of the Painted Harbor",
        "ja": "彩られた港の脈動"
    },
    "1768015252195": {
        "en": "Slumber of the Sapphire Grotto",
        "ja": "蒼玉の洞穴がまどろむ淵"
    },
    "1768015264821": {
        "en": "Whispers of the Crescent Frost",
        "ja": "凍てつく三日月の囁き"
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
