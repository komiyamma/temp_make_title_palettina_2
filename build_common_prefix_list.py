from __future__ import annotations

import re
from pathlib import Path


LEADING_NUMBER_PATTERN = re.compile(r"^(\d+)")
TITLE_DIRECTORIES = ("title", "title_back")
DELETE_TARGET_DIRECTORIES = ("tags", "critique")
TARGET_DIRECTORIES = ("tags", "critique", "picture")
OUTPUT_FILE_NAME = "list.txt"
MAX_RESULTS = 10


def extract_base_name(path: Path) -> str:
    return path.name.split(".", 1)[0]


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


def collect_base_names(directory: Path) -> set[str]:
    if not directory.is_dir():
        return set()

    return {extract_base_name(path) for path in directory.iterdir() if path.is_file()}


def delete_matching_files(source_directories: tuple[Path, ...], target_directories: tuple[Path, ...]) -> int:
    source_base_names: set[str] = set()
    for directory in source_directories:
        source_base_names.update(collect_base_names(directory))

    if not source_base_names:
        return 0

    deleted_count = 0
    for directory in target_directories:
        if not directory.is_dir():
            continue

        for path in directory.iterdir():
            if not path.is_file():
                continue

            if extract_base_name(path) not in source_base_names:
                continue

            path.unlink()
            deleted_count += 1

    return deleted_count


def main() -> None:
    root = Path(__file__).resolve().parent
    deleted_count = delete_matching_files(
        tuple(root / directory for directory in TITLE_DIRECTORIES),
        tuple(root / directory for directory in DELETE_TARGET_DIRECTORIES),
    )

    number_sets = [extract_leading_numbers(root / directory) for directory in TARGET_DIRECTORIES]

    common_numbers = sorted(set.intersection(*number_sets))[:MAX_RESULTS] if number_sets else []
    output_path = root / OUTPUT_FILE_NAME
    output_text = "\n".join(str(number) for number in common_numbers)
    if output_text:
        output_text += "\n"

    output_path.write_text(output_text, encoding="utf-8")

    print(f"Deleted {deleted_count} files from tags/critique")
    print(f"Wrote {len(common_numbers)} entries to {output_path}")


if __name__ == "__main__":
    main()
