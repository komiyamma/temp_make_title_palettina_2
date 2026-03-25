import os
import sys

ids = [
    "1767780598762", "1767781001238", "1767781358993", "1767782397742",
    "1767782401655", "1767782405344", "1767784480700", "1767784485527",
    "1767784490115", "1767784503702", "1767784505663", "1767784510123",
    "1767784514525", "1767785186669", "1767800760296"
]

titles = {
    "1767780598762": {"ja": "提灯の灯りに誘われて", "en": "Lured by the Lantern's Glow"},
    "1767781001238": {"ja": "宵の祝祭、高鳴る鼓動", "en": "Evening Festivities, Pounding Hearts"},
    "1767781358993": {"ja": "夕暮れの調べ", "en": "Melody of the Dusk"},
    "1767782397742": {"ja": "煌めきの記憶", "en": "Memories of Sparkle"},
    "1767782401655": {"ja": "幽玄なる峰と飛翔", "en": "Mystic Peaks and Flight"},
    "1767782405344": {"ja": "水面のきらめき、翡翠の舞", "en": "Glimmering Water, Emerald Dance"},
    "1767784480700": {"ja": "朝霧に包まれて", "en": "Embraced by Morning Mist"},
    "1767784485527": {"ja": "黄金の空へ", "en": "To the Golden Sky"},
    "1767784490115": {"ja": "静寂の深淵", "en": "Abyss of Silence"},
    "1767784503702": {"ja": "蓮池に舞い降りる妖精", "en": "Fairy Descending on the Lotus Pond"},
    "1767784505663": {"ja": "命の輝き、夏の調べ", "en": "Radiance of Life, Melody of Summer"},
    "1767784510123": {"ja": "ノスタルジアの光", "en": "Light of Nostalgia"},
    "1767784514525": {"ja": "秋風の便り", "en": "Tidings of the Autumn Wind"},
    "1767785186669": {"ja": "郷愁の里", "en": "Village of Nostalgia"},
    "1767800760296": {"ja": "木漏れ日の囁き", "en": "Whispers of Sunlight Through the Trees"}
}

os.makedirs("title", exist_ok=True)

for iid in ids:
    with open(f"title/{iid}.ja.txt", "w", encoding="utf-8") as f:
        f.write(titles[iid]["ja"])
    with open(f"title/{iid}.en.txt", "w", encoding="utf-8") as f:
        f.write(titles[iid]["en"])

print("Titles generated.")
