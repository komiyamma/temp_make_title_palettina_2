import os

titles = {
    "1768039490087": {
        "en": "Echoes of the Sunlit Greenhouse",
        "ja": "陽光の温室が奏でる残響"
    },
    "1768039494151": {
        "en": "Geometry of the Soul's Prism",
        "ja": "魂のプリズムが描く幾何学"
    },
    "1768039503550": {
        "en": "Whispers from the Glass Utopia",
        "ja": "硝子の理想郷からの囁き"
    },
    "1768045430790": {
        "en": "The Cosmic Instrument's Overture",
        "ja": "宇宙の楽器が奏でる序曲"
    },
    "1768045441137": {
        "en": "Twilight Reverie on the Balcony",
        "ja": "バルコニーで微睡む黄昏の夢"
    },
    "1768045447311": {
        "en": "Curiosity Written in the Stars",
        "ja": "星々に刻まれた好奇の眼差し"
    },
    "1768045453194": {
        "en": "Rhythm of the Morning Catch",
        "ja": "朝の豊漁が刻む鼓動"
    },
    "1768045458566": {
        "en": "Tears of the Stone Fountain",
        "ja": "石の泉が零す涙"
    },
    "1768045464090": {
        "en": "Crimson Prelude to the Gala",
        "ja": "夜会へ向かう真紅の調べ"
    },
    "1768045470460": {
        "en": "Symphony of the Scattered Studio",
        "ja": "散らかったアトリエの交響曲"
    },
    "1768045476393": {
        "en": "Solitude Amidst the Seaside Festival",
        "ja": "海辺の祝祭に溶け込む孤独"
    },
    "1768045483593": {
        "en": "Treasures of a Forgotten Era",
        "ja": "忘れ去られた時代の宝物"
    },
    "1768045488780": {
        "en": "Mosaic Dreams of Spheres",
        "ja": "球体が夢見るモザイク"
    },
    "1768045495434": {
        "en": "Spiral Ascend to the Tower's Core",
        "ja": "塔の中心へと続く螺旋の昇天"
    },
    "1768045512695": {
        "en": "Radiance of the Colored Void",
        "ja": "彩られた虚空の輝き"
    }
}

os.makedirs('title', exist_ok=True)

with open('list.txt', 'r') as f:
    ids = [line.strip() for line in f if line.strip()]

for id_val in ids:
    if id_val in titles:
        en_path = f"title/{id_val}.en.txt"
        ja_path = f"title/{id_val}.ja.txt"
        with open(en_path, 'w', encoding='utf-8') as f:
            f.write(titles[id_val]["en"])
        with open(ja_path, 'w', encoding='utf-8') as f:
            f.write(titles[id_val]["ja"])
        print(f"Generated titles for {id_val}")
    else:
        print(f"Missing title generation for {id_val}")
