from __future__ import annotations

import argparse
import math
import os
import subprocess
import shutil
import tempfile
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageOps


DEFAULT_SOURCE_DIR = Path(r"G:\repogitory\data_painting_art_pictures")
DEFAULT_TITLE_DIRS = (
    DEFAULT_SOURCE_DIR / "title",
    Path(__file__).resolve().parent / "title",
)
DEFAULT_DEST_DIR = Path(__file__).resolve().parent / "picture_back"
DEFAULT_TAG_SOURCE_DIR = DEFAULT_SOURCE_DIR / "tags"
DEFAULT_REPO_TAG_DIRS = (
    Path(__file__).resolve().parent / "tags",
    Path(__file__).resolve().parent / "tags_back",
)
DEFAULT_TAG_DEST_DIR = Path(__file__).resolve().parent / "tags_back"
DEFAULT_CRITIQUE_SOURCE_DIR = DEFAULT_SOURCE_DIR / "critique"
DEFAULT_REPO_CRITIQUE_DIRS = (
    Path(__file__).resolve().parent / "critique",
    Path(__file__).resolve().parent / "critique_back",
)
DEFAULT_CRITIQUE_DEST_DIR = Path(__file__).resolve().parent / "critique_back"
DEFAULT_TARGET_PIXELS = 160_000
DEFAULT_MAX_WORKERS = 10
TEXT_FILE_PATTERNS = ("*.ja.txt", "*.en.txt")


@dataclass(frozen=True)
class CopyTask:
    source_path: Path
    dest_path: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Copy PNG files into the repository picture directory after filtering out "
            "images that already have title text files. Large images are resized "
            "to roughly the target pixel count while preserving aspect ratio."
        )
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=DEFAULT_SOURCE_DIR,
        help=f"Directory containing source PNG files (default: {DEFAULT_SOURCE_DIR})",
    )
    parser.add_argument(
        "--title-dir",
        type=Path,
        action="append",
        default=None,
        help=(
            "Directory containing title text files. "
            "May be specified multiple times. "
            f"Default: {', '.join(str(path) for path in DEFAULT_TITLE_DIRS)}"
        ),
    )
    parser.add_argument(
        "--dest-dir",
        type=Path,
        default=DEFAULT_DEST_DIR,
        help=f"Directory to write copied PNG files (default: {DEFAULT_DEST_DIR})",
    )
    parser.add_argument(
        "--target-pixels",
        type=int,
        default=DEFAULT_TARGET_PIXELS,
        help=f"Approximate pixel count for resized images (default: {DEFAULT_TARGET_PIXELS})",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=DEFAULT_MAX_WORKERS,
        help=f"Maximum number of worker processes to use (default: {DEFAULT_MAX_WORKERS})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be copied without writing files.",
    )
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    if args.target_pixels <= 0:
        raise ValueError("--target-pixels must be a positive integer.")
    if args.max_workers <= 0:
        raise ValueError("--max-workers must be a positive integer.")
    if not args.source_dir.exists():
        raise FileNotFoundError(f"Source directory does not exist: {args.source_dir}")
    title_dirs = args.title_dir or list(DEFAULT_TITLE_DIRS)
    for title_dir in title_dirs:
        if not title_dir.exists():
            raise FileNotFoundError(f"Title directory does not exist: {title_dir}")
        if not title_dir.is_dir():
            raise NotADirectoryError(f"Title directory is not a directory: {title_dir}")
    if not args.source_dir.is_dir():
        raise NotADirectoryError(f"Source directory is not a directory: {args.source_dir}")
    if not DEFAULT_TAG_SOURCE_DIR.exists():
        raise FileNotFoundError(f"Tag source directory does not exist: {DEFAULT_TAG_SOURCE_DIR}")
    if not DEFAULT_TAG_SOURCE_DIR.is_dir():
        raise NotADirectoryError(f"Tag source directory is not a directory: {DEFAULT_TAG_SOURCE_DIR}")
    for repo_tag_dir in DEFAULT_REPO_TAG_DIRS:
        if repo_tag_dir.exists() and not repo_tag_dir.is_dir():
            raise NotADirectoryError(f"Repository tag directory is not a directory: {repo_tag_dir}")
    if not DEFAULT_CRITIQUE_SOURCE_DIR.exists():
        raise FileNotFoundError(f"Critique source directory does not exist: {DEFAULT_CRITIQUE_SOURCE_DIR}")
    if not DEFAULT_CRITIQUE_SOURCE_DIR.is_dir():
        raise NotADirectoryError(f"Critique source directory is not a directory: {DEFAULT_CRITIQUE_SOURCE_DIR}")
    for repo_critique_dir in DEFAULT_REPO_CRITIQUE_DIRS:
        if repo_critique_dir.exists() and not repo_critique_dir.is_dir():
            raise NotADirectoryError(f"Repository critique directory is not a directory: {repo_critique_dir}")


def text_file_basename(path: Path) -> str | None:
    suffixes = tuple(path.suffixes[-2:])
    if suffixes not in ((".ja", ".txt"), (".en", ".txt")):
        return None
    return path.name.removesuffix("".join(suffixes))


def collect_text_basenames(text_dirs: list[Path], *, missing_ok: bool = False) -> set[str]:
    basenames: set[str] = set()
    for text_dir in text_dirs:
        if not text_dir.exists():
            if missing_ok:
                continue
            raise FileNotFoundError(f"Text directory does not exist: {text_dir}")
        if not text_dir.is_dir():
            raise NotADirectoryError(f"Text directory is not a directory: {text_dir}")
        for pattern in TEXT_FILE_PATTERNS:
            for text_file in text_dir.glob(pattern):
                basename = text_file_basename(text_file)
                if basename is not None:
                    basenames.add(basename)
    return basenames


def collect_tasks(
    source_dir: Path,
    dest_dir: Path,
    excluded_basenames: set[str],
) -> tuple[list[CopyTask], int, int]:
    tasks: list[CopyTask] = []
    source_count = 0
    skipped_existing = 0
    for source_path in sorted(source_dir.glob("*.png")):
        basename = source_path.stem
        if not basename.isdigit():
            continue
        source_count += 1
        if basename in excluded_basenames:
            continue

        dest_path = dest_dir / source_path.name
        if dest_path.exists():
            skipped_existing += 1
            continue

        tasks.append(CopyTask(source_path=source_path, dest_path=dest_path))
    return tasks, source_count, skipped_existing


def collect_text_copy_tasks(
    source_dir: Path,
    dest_dir: Path,
    excluded_basenames: set[str],
    existing_basenames: set[str],
) -> tuple[list[CopyTask], int, int, int]:
    tasks: list[CopyTask] = []
    source_count = 0
    skipped_title_existing = 0
    skipped_repo_existing = 0

    for pattern in TEXT_FILE_PATTERNS:
        for source_path in sorted(source_dir.glob(pattern)):
            basename = text_file_basename(source_path)
            if basename is None or not basename.isdigit():
                continue

            source_count += 1
            if basename in excluded_basenames:
                skipped_title_existing += 1
                continue
            if basename in existing_basenames:
                skipped_repo_existing += 1
                continue

            dest_path = dest_dir / source_path.name
            if dest_path.exists():
                skipped_repo_existing += 1
                continue

            tasks.append(CopyTask(source_path=source_path, dest_path=dest_path))

    return tasks, source_count, skipped_title_existing, skipped_repo_existing


def resized_dimensions(width: int, height: int, target_pixels: int) -> tuple[int, int]:
    pixel_count = width * height
    if pixel_count <= target_pixels:
        return width, height

    scale = math.sqrt(target_pixels / pixel_count)
    new_width = max(1, round(width * scale))
    new_height = max(1, round(height * scale))
    return new_width, new_height


def process_one(task: CopyTask, target_pixels: int) -> tuple[str, str]:
    task.dest_path.parent.mkdir(parents=True, exist_ok=True)

    if task.dest_path.exists():
        return ("skipped_existing", task.dest_path.name)

    with Image.open(task.source_path) as image:
        image = ImageOps.exif_transpose(image)
        width, height = image.size
        new_width, new_height = resized_dimensions(width, height, target_pixels)

        if (new_width, new_height) == (width, height):
            shutil.copy2(task.source_path, task.dest_path)
            return ("copied_original", task.dest_path.name)

        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        with tempfile.NamedTemporaryFile(
            dir=task.dest_path.parent,
            prefix=f".{task.dest_path.stem}.",
            suffix=".png",
            delete=False,
        ) as temp_file:
            temp_path = Path(temp_file.name)

        try:
            image.save(temp_path, format="PNG", optimize=True)
            os.replace(temp_path, task.dest_path)
        finally:
            if temp_path.exists():
                temp_path.unlink()

        return ("resized", task.dest_path.name)


def run_tasks(
    tasks: list[CopyTask],
    target_pixels: int,
    max_workers: int,
) -> dict[str, int]:
    counts = {
        "resized": 0,
        "copied_original": 0,
        "skipped_existing": 0,
        "failed": 0,
    }

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_one, task, target_pixels): task
            for task in tasks
        }
        for future in as_completed(futures):
            task = futures[future]
            try:
                status, _ = future.result()
                counts[status] += 1
            except Exception as exc:
                counts["failed"] += 1
                print(f"FAILED {task.source_path.name}: {exc}")

    return counts


def optimize_copied_pngs(dest_dir: Path) -> None:
    png_files = sorted(dest_dir.glob("*.png"))
    if not png_files:
        return

    batch_size = 200
    for start in range(0, len(png_files), batch_size):
        batch = png_files[start : start + batch_size]
        subprocess.run(
            ["oxipng", "-o", "6", "--strip", "safe", "--alpha", *[path.name for path in batch]],
            cwd=dest_dir,
            check=True,
        )


def copy_text_tasks(tasks: list[CopyTask]) -> dict[str, int]:
    counts = {
        "copied": 0,
        "skipped_existing": 0,
        "failed": 0,
    }

    for task in tasks:
        try:
            task.dest_path.parent.mkdir(parents=True, exist_ok=True)
            if task.dest_path.exists():
                counts["skipped_existing"] += 1
                continue
            shutil.copy2(task.source_path, task.dest_path)
            counts["copied"] += 1
        except Exception as exc:
            counts["failed"] += 1
            print(f"FAILED {task.source_path.name}: {exc}")

    return counts


def main() -> int:
    args = parse_args()
    title_dirs = args.title_dir or list(DEFAULT_TITLE_DIRS)
    validate_args(args)

    excluded_basenames = collect_text_basenames(title_dirs)
    tasks, source_count, skipped_existing_count = collect_tasks(
        source_dir=args.source_dir,
        dest_dir=args.dest_dir,
        excluded_basenames=excluded_basenames,
    )
    existing_tag_basenames = collect_text_basenames(list(DEFAULT_REPO_TAG_DIRS), missing_ok=True)
    tag_tasks, tag_source_count, tag_skipped_title_count, tag_skipped_existing_count = collect_text_copy_tasks(
        source_dir=DEFAULT_TAG_SOURCE_DIR,
        dest_dir=DEFAULT_TAG_DEST_DIR,
        excluded_basenames=excluded_basenames,
        existing_basenames=existing_tag_basenames,
    )
    existing_critique_basenames = collect_text_basenames(list(DEFAULT_REPO_CRITIQUE_DIRS), missing_ok=True)
    critique_tasks, critique_source_count, critique_skipped_title_count, critique_skipped_existing_count = (
        collect_text_copy_tasks(
            source_dir=DEFAULT_CRITIQUE_SOURCE_DIR,
            dest_dir=DEFAULT_CRITIQUE_DEST_DIR,
            excluded_basenames=excluded_basenames,
            existing_basenames=existing_critique_basenames,
        )
    )

    excluded_count = sum(
        1 for path in args.source_dir.glob("*.png") if path.stem.isdigit() and path.stem in excluded_basenames
    )

    print(f"Source PNG files with numeric basenames: {source_count}")
    print(f"Excluded because title text exists: {excluded_count}")
    print(f"Skipped because destination already exists: {skipped_existing_count}")
    print(f"Pending files after filtering: {len(tasks)}")
    print(f"Source tag text files with numeric basenames: {tag_source_count}")
    print(f"Tag files skipped because title text exists: {tag_skipped_title_count}")
    print(f"Tag files skipped because repository tags already exist: {tag_skipped_existing_count}")
    print(f"Pending tag files after filtering: {len(tag_tasks)}")
    print(f"Source critique text files with numeric basenames: {critique_source_count}")
    print(f"Critique files skipped because title text exists: {critique_skipped_title_count}")
    print(f"Critique files skipped because repository critique already exist: {critique_skipped_existing_count}")
    print(f"Pending critique files after filtering: {len(critique_tasks)}")

    if args.dry_run:
        print("Dry run enabled. No files were written.")
        return 0

    if not tasks and not tag_tasks and not critique_tasks:
        print("No files to process.")
        return 0

    picture_counts = {
        "resized": 0,
        "copied_original": 0,
        "skipped_existing": 0,
        "failed": 0,
    }
    worker_count = 0
    if tasks:
        worker_count = min(args.max_workers, os.cpu_count() or 1, len(tasks))
        picture_counts = run_tasks(
            tasks=tasks,
            target_pixels=args.target_pixels,
            max_workers=worker_count,
        )
        if picture_counts["resized"] or picture_counts["copied_original"]:
            optimize_copied_pngs(args.dest_dir)

    tag_counts = {
        "copied": 0,
        "skipped_existing": 0,
        "failed": 0,
    }
    if tag_tasks:
        tag_counts = copy_text_tasks(tag_tasks)

    critique_counts = {
        "copied": 0,
        "skipped_existing": 0,
        "failed": 0,
    }
    if critique_tasks:
        critique_counts = copy_text_tasks(critique_tasks)

    print(f"Worker processes used: {worker_count}")
    print(f"Resized and copied: {picture_counts['resized']}")
    print(f"Copied without resizing: {picture_counts['copied_original']}")
    print(f"Skipped because destination already exists: {picture_counts['skipped_existing'] + skipped_existing_count}")
    print(f"Tag files copied to tags_back: {tag_counts['copied']}")
    print(f"Tag files skipped because destination already exists: {tag_counts['skipped_existing'] + tag_skipped_existing_count}")
    print(f"Critique files copied to critique_back: {critique_counts['copied']}")
    print(
        "Critique files skipped because destination already exists: "
        f"{critique_counts['skipped_existing'] + critique_skipped_existing_count}"
    )
    print(f"Failed: {picture_counts['failed'] + tag_counts['failed'] + critique_counts['failed']}")

    return 1 if picture_counts["failed"] or tag_counts["failed"] or critique_counts["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
