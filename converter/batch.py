"""Batch conversion planning and execution, independent of the GUI."""

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .constants import TARGET_EXT_MAP


@dataclass(frozen=True)
class ConversionJob:
    source: Path
    destination: Path
    media_type: str
    target_extension: str


@dataclass(frozen=True)
class BatchResult:
    total: int
    succeeded: int
    failures: tuple[str, ...]


def plan_jobs(
    files: tuple[str, ...], output_dir: str, media_type: str, target_format: str
) -> tuple[ConversionJob, ...]:
    """Choose output names without overwriting existing files or earlier jobs."""
    if target_format not in TARGET_EXT_MAP:
        raise ValueError(f"不支援的目標格式：{target_format}")
    if media_type not in ("image", "video"):
        raise ValueError(f"不支援的檔案類型：{media_type}")
    destination_dir = Path(output_dir)
    if not destination_dir.is_dir():
        raise ValueError(f"輸出資料夾不存在：{output_dir}")

    extension = TARGET_EXT_MAP[target_format]
    used: set[Path] = set()
    jobs = []
    for filename in files:
        source = Path(filename)
        base = f"{source.stem}_converted"
        destination = destination_dir / f"{base}{extension}"
        number = 2
        while destination.exists() or destination in used:
            destination = destination_dir / f"{base}_{number}{extension}"
            number += 1
        used.add(destination)
        jobs.append(ConversionJob(source, destination, media_type, extension))
    return tuple(jobs)


def run_jobs(
    jobs: tuple[ConversionJob, ...],
    on_start: Callable[[int, ConversionJob], None] | None = None,
    logger_factory: Callable[[ConversionJob], object] | None = None,
) -> BatchResult:
    """Run all jobs and retain an error for each failed file."""
    failures = []
    for index, job in enumerate(jobs, start=1):
        if on_start:
            on_start(index, job)
        try:
            if job.media_type == "image":
                from .image_converter import convert_image

                convert_image(str(job.source), str(job.destination), job.target_extension)
            else:
                from .video_converter import convert_video

                logger = logger_factory(job) if logger_factory else None
                convert_video(str(job.source), str(job.destination), job.target_extension, logger)
        except Exception as exc:
            failures.append(f"{job.source.name}: {exc}")
    return BatchResult(len(jobs), len(jobs) - len(failures), tuple(failures))
