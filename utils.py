import logging
import pathlib
import sys
import typing
import toml


def read_toml(file_path: typing.Union[str, pathlib.Path]) -> dict:
    """
    Read configuration settings from the TOML file.
    """
    file_path = pathlib.Path(file_path)
    config = toml.load(file_path)
    return config


def format_duration_long(duration_seconds: float) -> str:
    """
    Convert a duration in seconds to a human-readable string with
    years, months, days, hours, minutes, seconds, and milliseconds.
    Example: 1y2mo3d4h5m6s321ms
    """
    # Convert everything to milliseconds for easier integer math
    total_ms = int(duration_seconds * 1000)

    # Define conversions
    ms_per_second = 1000
    ms_per_minute = 60 * ms_per_second
    ms_per_hour = 60 * ms_per_minute
    ms_per_day = 24 * ms_per_hour
    ms_per_month = 30 * ms_per_day   # approximate month as 30 days
    ms_per_year = 365 * ms_per_day   # approximate year as 365 days

    years, rem_ms = divmod(total_ms, ms_per_year)
    months, rem_ms = divmod(rem_ms, ms_per_month)
    days, rem_ms = divmod(rem_ms, ms_per_day)
    hours, rem_ms = divmod(rem_ms, ms_per_hour)
    minutes, rem_ms = divmod(rem_ms, ms_per_minute)
    seconds, milliseconds = divmod(rem_ms, ms_per_second)

    parts = []
    if years:
        parts.append(f"{years}y")
    if months:
        parts.append(f"{months}mo")
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if seconds:
        parts.append(f"{seconds}s")
    if milliseconds or not parts:
        parts.append(f"{milliseconds}ms")  # always show ms if nothing else

    return "".join(parts)


def setup_logging(
        logger: logging.Logger,
        log_file_path: typing.Union[str, pathlib.Path],
        number_of_logs_to_keep: typing.Union[int, None] = None,
        console_logging_level: int = logging.DEBUG,
        file_logging_level: int = logging.DEBUG,
        log_message_format: str = "%(asctime)s.%(msecs)03d %(levelname)s [%(funcName)s] [%(name)s]: %(message)s",
        date_format: str = "%Y-%m-%d %H:%M:%S") -> None:
    log_file_path = pathlib.Path(log_file_path)
    log_dir = log_file_path.parent
    log_dir.mkdir(parents=True, exist_ok=True)

    # Limit # of logs in logs folder
    if number_of_logs_to_keep is not None:
        log_files = sorted([f for f in log_dir.glob("*.log")], key=lambda f: f.stat().st_mtime)
        if len(log_files) > number_of_logs_to_keep:
            for file in log_files[:-number_of_logs_to_keep]:
                file.unlink()

    # Clear old handlers to avoid duplication
    logger.handlers.clear()
    logger.setLevel(file_logging_level)

    formatter = logging.Formatter(log_message_format, datefmt=date_format)

    # File Handler
    file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
    file_handler.setLevel(file_logging_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_logging_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
