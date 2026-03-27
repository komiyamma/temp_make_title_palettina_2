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
DEFAULT_TARGET_PIXELS = 160_000
DEFAULT_MAX_WORKERS = 10


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


def collect_excluded_basenames(title_dirs: list[Path]) -> set[str]:
    excluded: set[str] = set()
    for title_dir in title_dirs:
        for pattern in ("*.ja.txt", "*.en.txt"):
            for title_file in title_dir.glob(pattern):
                excluded.add(title_file.name.removesuffix("".join(title_file.suffixes[-2:])))
    return excluded


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

    subprocess.run(
        ["oxipng", "-o", "6", "--strip", "safe", "--alpha", *[path.name for path in png_files]],
        cwd=dest_dir,
        check=True,
    )


def main() -> int:
    args = parse_args()
    title_dirs = args.title_dir or list(DEFAULT_TITLE_DIRS)
    validate_args(args)

    excluded_basenames = collect_excluded_basenames(title_dirs)
    tasks, source_count, skipped_existing_count = collect_tasks(
        source_dir=args.source_dir,
        dest_dir=args.dest_dir,
        excluded_basenames=excluded_basenames,
    )

    excluded_count = sum(
        1 for path in args.source_dir.glob("*.png") if path.stem.isdigit() and path.stem in excluded_basenames
    )

    print(f"Source PNG files with numeric basenames: {source_count}")
    print(f"Excluded because title text exists: {excluded_count}")
    print(f"Skipped because destination already exists: {skipped_existing_count}")
    print(f"Pending files after filtering: {len(tasks)}")

    if args.dry_run:
        print("Dry run enabled. No files were written.")
        return 0

    if not tasks:
        print("No files to process.")
        return 0

    worker_count = min(args.max_workers, os.cpu_count() or 1, len(tasks))
    counts = run_tasks(
        tasks=tasks,
        target_pixels=args.target_pixels,
        max_workers=worker_count,
    )

    optimize_copied_pngs(args.dest_dir)

    print(f"Worker processes used: {worker_count}")
    print(f"Resized and copied: {counts['resized']}")
    print(f"Copied without resizing: {counts['copied_original']}")
    print(f"Skipped because destination already exists: {counts['skipped_existing'] + skipped_existing_count}")
    print(f"Failed: {counts['failed']}")

    return 1 if counts["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
