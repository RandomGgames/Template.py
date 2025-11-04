import logging
import pathlib
import socket
import sys
import time
import traceback
from utils import setup_logging, format_duration_long, read_toml

logger = logging.getLogger(__name__)

"""
Python Script Template

Template includes:
- Configurable logging via TOML
- Execution timing with human-readable duration
- Error handling and cleanup
"""
__version__ = "1.0.0"
__date__ = "2023-01-01"


def main() -> None:
    pass  # Code goes here
    time.sleep(10)


if __name__ == "__main__":
    config_path = pathlib.Path("config.toml")
    if not config_path.exists():
        raise FileNotFoundError(f"Missing {config_path}")

    config = read_toml(config_path)

    console_logging_level = getattr(logging, config.get("logging", {}).get("console_logging_level", "INFO").upper(), logging.INFO)
    file_logging_level = getattr(logging, config.get("logging", {}).get("file_logging_level", "INFO").upper(), logging.INFO)
    use_logs_folder = config.get("logging", {}).get("use_logs_folder", True)
    number_of_logs_to_keep = config.get("logging", {}).get("number_of_logs_to_keep", 10)
    log_message_format = config.get("logging", {}).get(
        "log_message_format",
        "%(asctime)s.%(msecs)03d %(levelname)s [%(funcName)s]: %(message)s"
    )

    script_name = pathlib.Path(__file__).stem
    if use_logs_folder:
        pc_name = socket.gethostname()
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        log_dir = pathlib.Path(f"{script_name} Logs")
        log_dir.mkdir(exist_ok=True)
        log_file_name = f"{timestamp}_{pc_name}.log"
        log_file_path = log_dir / log_file_name
    else:
        log_file_path = pathlib.Path(f"{script_name}.log")

    setup_logging(
        logger,
        log_file_path,
        console_logging_level=console_logging_level,
        file_logging_level=file_logging_level,
        number_of_logs_to_keep=number_of_logs_to_keep,
        log_message_format=log_message_format
    )

    error = 0
    try:
        start_time = time.perf_counter()
        logger.info(f"Script: {script_name} | Version: {__version__} | Date: {__date__}")
        main()
        end_time = time.perf_counter()
        duration = end_time - start_time
        duration = format_duration_long(duration)
        logger.info(f"Execution completed in {duration}.")
    except KeyboardInterrupt:
        logger.warning("Operation interrupted by user.")
        error = 130
    except Exception as e:
        logger.warning(f"A fatal error has occurred: {repr(e)}\n{traceback.format_exc()}")
        error = 1
    finally:
        for handler in logger.handlers:
            handler.close()
        logger.handlers.clear()
        sys.exit(error)
