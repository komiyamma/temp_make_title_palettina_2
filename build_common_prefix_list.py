from __future__ import annotations

import re
from pathlib import Path


LEADING_NUMBER_PATTERN = re.compile(r"^(\d+)")
TARGET_DIRECTORIES = ("tags", "critique", "picture")
OUTPUT_FILE_NAME = "list.txt"
MAX_RESULTS = 10


def extract_leading_numbers(directory: Path) -> set[int]:
    if not directory.is_dir():
        return set()

    numbers: set[int] = set()
    for path in directory.iterdir():
        if not path.is_file():
            continue

        match = LEADING_NUMBER_PATTERN.match(path.name)
        if match:
            numbers.add(int(match.group(1)))

    return numbers


def main() -> None:
    root = Path(__file__).resolve().parent
    number_sets = [extract_leading_numbers(root / directory) for directory in TARGET_DIRECTORIES]

    common_numbers = sorted(set.intersection(*number_sets))[:MAX_RESULTS] if number_sets else []
    output_path = root / OUTPUT_FILE_NAME
    output_text = "\n".join(str(number) for number in common_numbers)
    if output_text:
        output_text += "\n"

    output_path.write_text(output_text, encoding="utf-8")

    print(f"Wrote {len(common_numbers)} entries to {output_path}")


if __name__ == "__main__":
    main()