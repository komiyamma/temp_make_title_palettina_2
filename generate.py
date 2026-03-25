import os

titles = {
    "1767879764712": {"en": "Echoes of a Gilded Aviary", "ja": "黄金の鳥籠が奏でる光の交響曲"},
    "1767879768309": {"en": "Whispers of the Sunlit Oasis", "ja": "陽光のオアシスに響く水音"},
    "1767879772213": {"en": "Architects of the Cosmos", "ja": "宇宙を編む賢者たち"},
    "1767879775899": {"en": "Serenade of the Golden Blossom", "ja": "黄金の花咲く静寂の調べ"},
    "1767879787698": {"en": "The Clockwork Heavens", "ja": "星霜を刻む天球の記憶"},
    "1767879791323": {"en": "Symphony of Iron and Steam", "ja": "鉄と蒸気が織りなす交響詩"},
    "1767879798998": {"en": "Sparks of the Forge's Heart", "ja": "赫怒の鉄、散りゆく火花"},
    "1767879803180": {"en": "Tears of Molten Gold", "ja": "溶鉄の涙、迸る黄金の脈動"},
    "1767879806365": {"en": "Chronicles of the Starry Sphere", "ja": "星月夜に語られる叡智の年代記"},
    "1767879814506": {"en": "Vessel of the Golden Twilight", "ja": "黄昏に染まる出航の夢"},
    "1767879823358": {"en": "Cascade of Celestial Geometry", "ja": "降り注ぐ天界の幾何学"},
    "1767879828170": {"en": "Embrace Under the Starlit Cafe", "ja": "星屑のカフェで交わす抱擁"},
    "1767879831833": {"en": "Harbor of Turquoise Dreams", "ja": "蒼緑の港に揺蕩う夢"},
    "1767879836575": {"en": "Golden Glow of the Grand Canal", "ja": "大運河を染める黄金の宵"},
    "1767879841328": {"en": "Toast to the Twilight Splendor", "ja": "黄昏の祝杯、煌めく街角"}
}

os.makedirs('title', exist_ok=True)

with open('list.txt') as f:
    ids = [line.strip() for line in f if line.strip()]

for id in ids:
    with open(f"title/{id}.en.txt", "w") as f:
        f.write(titles[id]["en"])
    with open(f"title/{id}.ja.txt", "w") as f:
        f.write(titles[id]["ja"])

print("Successfully generated all title files.")
