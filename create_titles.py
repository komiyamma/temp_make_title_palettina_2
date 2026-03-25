import os

ids = [
    "1767843142153", "1767843146922", "1767843150816", "1767843156401",
    "1767843160189", "1767843163860", "1767843167798", "1767851299538",
    "1767851304860", "1767851309946", "1767851314701", "1767851319136",
    "1767851323867", "1767851329529", "1767851335052"
]

titles = {
    "1767843142153": {
        "en": "Whispers of the Golden Prism",
        "ja": "黄金の雫に宿る永遠の瞬き"
    },
    "1767843146922": {
        "en": "Illusions Woven by Twilight Lanterns",
        "ja": "宵闇に揺れる灯火の幻影"
    },
    "1767843150816": {
        "en": "Solitary Pine in the Whispering Mist",
        "ja": "霧消の峰に立つ孤高の松"
    },
    "1767843156401": {
        "en": "A Timeless Melody of the Cascading Falls",
        "ja": "悠久の岩肌を撫でる飛瀑の調べ"
    },
    "1767843160189": {
        "en": "Spring Illusion Blooming in the Mystic Peaks",
        "ja": "幽玄なる峰に咲き誇る春の幻影"
    },
    "1767843163860": {
        "en": "Echoes of the Past in a Warm Embrace",
        "ja": "追憶の書斎に灯る過ぎ去りし日の温もり"
    },
    "1767843167798": {
        "en": "Illusory Forest Melting into the Golden Glow",
        "ja": "黄金の光芒に溶けゆく幻想の森"
    },
    "1767851299538": {
        "en": "A Hymn of Life in the Cradle of Sunlight",
        "ja": "光の揺り籠に咲き誇る生命の讃歌"
    },
    "1767851304860": {
        "en": "An Evening Banquet Woven by Lantern Light",
        "ja": "灯火が紡ぐ宵の宴、交交たる想い"
    },
    "1767851309946": {
        "en": "Eternal Conversations Beneath the Dancing Spring Petals",
        "ja": "春陽に舞う花びらと、永遠なる友の語らい"
    },
    "1767851314701": {
        "en": "Roar of the Untamed Earth and the Piercing Spray",
        "ja": "岩を穿つ飛沫、荒ぶる大地の咆哮"
    },
    "1767851319136": {
        "en": "Eternal Silence Drifting on the Misty Water",
        "ja": "霞む水鏡に揺蕩う悠久の静寂"
    },
    "1767851323867": {
        "en": "A Soul's Voyage Thirsting for Knowledge Beyond the Stars",
        "ja": "星屑の彼方へ、知を渇望する魂の航海"
    },
    "1767851329529": {
        "en": "Indomitable Pulse Carved into the Raging Sea",
        "ja": "荒れ狂う海原に刻む不屈の鼓動"
    },
    "1767851335052": {
        "en": "Beauty of Daily Life Breathing on the Sunlit Cobblestone",
        "ja": "木漏れ日の石畳に息づく、名もなき営みの美"
    }
}

os.makedirs("title", exist_ok=True)

for iid in ids:
    with open(f"title/{iid}.ja.txt", "w", encoding="utf-8") as f:
        f.write(titles[iid]["ja"])
    with open(f"title/{iid}.en.txt", "w", encoding="utf-8") as f:
        f.write(titles[iid]["en"])

print("Successfully generated all title files.")
