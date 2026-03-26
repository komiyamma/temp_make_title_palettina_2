from __future__ import annotations

import re
import shutil
from pathlib import Path


LEADING_NUMBER_PATTERN = re.compile(r"^(\d+)")
TITLE_DIRECTORY = "title"
RESOURCE_DIRECTORIES = ("tags", "tags_back", "critique", "critique_back", "picture", "picture_back")
BACK_TARGET_DIRECTORIES = ("tags_back", "critique_back", "picture_back")
MOVE_DIRECTORY_PAIRS = (
    ("tags_back", "tags"),
    ("critique_back", "critique"),
    ("picture_back", "picture"),
)
OUTPUT_FILE_NAME = "list.txt"
MAX_RESULTS = 15


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


def collect_files_by_leading_number(directory: Path) -> dict[int, list[Path]]:
    if not directory.is_dir():
        return {}

    files_by_number: dict[int, list[Path]] = {}
    for path in directory.iterdir():
        if not path.is_file():
            continue

        match = LEADING_NUMBER_PATTERN.match(path.name)
        if not match:
            continue

        number = int(match.group(1))
        files_by_number.setdefault(number, []).append(path)

    return files_by_number


def collect_completed_title_base_names(directory: Path) -> set[str]:
    if not directory.is_dir():
        return set()

    languages_by_base_name: dict[str, set[str]] = {}
    for path in directory.iterdir():
        if not path.is_file():
            continue

        parts = path.name.split(".")
        if len(parts) < 3 or parts[-1] != "txt":
            continue

        language = parts[-2]
        if language not in {"en", "ja"}:
            continue

        base_name = parts[0]
        languages_by_base_name.setdefault(base_name, set()).add(language)

    return {
        base_name
        for base_name, languages in languages_by_base_name.items()
        if {"en", "ja"}.issubset(languages)
    }


def delete_matching_files(base_names: set[str], target_directories: tuple[Path, ...]) -> int:
    if not base_names:
        return 0

    deleted_count = 0
    for directory in target_directories:
        if not directory.is_dir():
            continue

        for path in directory.iterdir():
            if not path.is_file():
                continue

            if extract_base_name(path) not in base_names:
                continue

            path.unlink()
            deleted_count += 1

    return deleted_count


def copy_matching_files(root: Path, numbers_to_copy: list[int]) -> int:
    if not numbers_to_copy:
        return 0

    copy_count = 0
    for source_directory_name, destination_directory_name in MOVE_DIRECTORY_PAIRS:
        source_directory = root / source_directory_name
        if not source_directory.is_dir():
            continue

        destination_directory = root / destination_directory_name
        destination_directory.mkdir(parents=True, exist_ok=True)

        files_by_number = collect_files_by_leading_number(source_directory)
        for number in numbers_to_copy:
            for source_path in files_by_number.get(number, []):
                destination_path = destination_directory / source_path.name
                shutil.copy2(source_path, destination_path)
                copy_count += 1

    return copy_count


def move_old_title_files(root: Path) -> int:
    title_dir = root / TITLE_DIRECTORY
    move_title_config = root / "move_title.txt"

    if not title_dir.is_dir() or not move_title_config.is_file():
        return 0

    destination_path_str = move_title_config.read_text(encoding="utf-8").strip()
    if not destination_path_str:
        return 0

    destination_dir = Path(destination_path_str)
    destination_dir.mkdir(parents=True, exist_ok=True)

    files = [p for p in title_dir.iterdir() if p.is_file()]
    if len(files) < 50:
        return 0

    # Sort files by modification time descending (newest first)
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    files_to_move = files[30:]
    move_count = 0
    for file_path in files_to_move:
        dest_file_path = destination_dir / file_path.name
        try:
            shutil.move(str(file_path), str(dest_file_path))
            move_count += 1
        except Exception as e:
            print(f"Failed to move {file_path}: {e}")

    if move_count > 0:
        print(f"Moved {move_count} old title files to {destination_dir}")

    return move_count


def main() -> None:
    root = Path(__file__).resolve().parent
    completed_title_base_names = collect_completed_title_base_names(root / TITLE_DIRECTORY)
    deleted_count = delete_matching_files(
        completed_title_base_names,
        tuple(root / directory for directory in RESOURCE_DIRECTORIES),
    )

    number_sets = [extract_leading_numbers(root / directory) for directory in BACK_TARGET_DIRECTORIES]

    common_numbers = sorted(set.intersection(*number_sets))[:MAX_RESULTS] if number_sets else []
    output_path = root / OUTPUT_FILE_NAME
    output_text = "\n".join(str(number) for number in common_numbers)
    if output_text:
        output_text += "\n"

    output_path.write_text(output_text, encoding="utf-8")
    copied_count = copy_matching_files(root, common_numbers)

    print(f"Deleted {deleted_count} resource files for completed titles")
    print(f"Copied {copied_count} files from *_back directories")
    print(f"Wrote {len(common_numbers)} entries to {output_path}")

    # Process old title files
    move_old_title_files(root)


if __name__ == "__main__":
    main()
