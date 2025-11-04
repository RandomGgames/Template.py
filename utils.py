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
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    config = toml.load(file_path)
    return config


def format_duration_long(duration_seconds: float) -> str:
    """
    Convert a duration in seconds to a human-readable string with
    years, months, days, hours, minutes, seconds, milliseconds,
    microseconds, and nanoseconds.
    Example: 1y2mo3d4h5m6s321ms123us456ns
    """
    # Convert everything to nanoseconds for precision
    total_ns = int(duration_seconds * 1_000_000_000)

    # Define conversions
    ns_per_microsecond = 1_000
    ns_per_millisecond = 1_000_000
    ns_per_second = 1_000_000_000
    ns_per_minute = 60 * ns_per_second
    ns_per_hour = 60 * ns_per_minute
    ns_per_day = 24 * ns_per_hour
    ns_per_month = 30 * ns_per_day   # approximate month as 30 days
    ns_per_year = 365 * ns_per_day   # approximate year as 365 days

    years, rem_ns = divmod(total_ns, ns_per_year)
    months, rem_ns = divmod(rem_ns, ns_per_month)
    days, rem_ns = divmod(rem_ns, ns_per_day)
    hours, rem_ns = divmod(rem_ns, ns_per_hour)
    minutes, rem_ns = divmod(rem_ns, ns_per_minute)
    seconds, rem_ns = divmod(rem_ns, ns_per_second)
    milliseconds, rem_ns = divmod(rem_ns, ns_per_millisecond)
    microseconds, nanoseconds = divmod(rem_ns, ns_per_microsecond)

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
    if milliseconds:
        parts.append(f"{milliseconds}ms")
    if microseconds:
        parts.append(f"{microseconds}us")
    if nanoseconds or not parts:
        parts.append(f"{nanoseconds}ns")  # always show ns if nothing else

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
