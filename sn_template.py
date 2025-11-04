import logging
import pathlib
import socket
import sys
import time
import traceback
from datetime import datetime
from utils import setup_logging, format_duration_long, read_toml

logger = logging.getLogger(__name__)

"""
SN-Specific Python Script Template

Template includes:
- Configurable logging via utils
- Execution timing with human-readable duration
- Error handling and cleanup
- DUT serial number support with SN-specific log folders
"""

__version__ = "1.0.0"  # Major.Minor.Patch
__date__ = "2000-01-01"  # yyyy-mm-dd

config_path = pathlib.Path("config.toml")
config = read_toml(config_path)


def main(dut_sn: str | None) -> None:
    logger.debug(f"Testing DUT SN '{dut_sn}'")
    pass  # Code goes here


if __name__ == "__main__":
    dut_sn = input("SN: ")
    if dut_sn == "":
        dut_sn = None

    script_name = pathlib.Path(__file__).stem
    pc_name = socket.gethostname()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Create SN-specific log directory
    log_dir = pathlib.Path(f"{script_name} Logs")
    if dut_sn:
        log_dir /= str(dut_sn)
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file_name = f"{timestamp}_{str(dut_sn)}_{pc_name}.log"
    log_file_path = log_dir / log_file_name

    # Set up logging
    setup_logging(
        logger,
        log_file_path,
        console_logging_level=logging.DEBUG,
        file_logging_level=logging.DEBUG,
        number_of_logs_to_keep=10,
        log_message_format="%(asctime)s.%(msecs)03d %(levelname)s [%(funcName)s]: %(message)s"
    )

    error = 0
    try:
        start_time = time.perf_counter_ns()
        logger.info(f"Script: {script_name} | Version: {__version__} | DUT SN: {dut_sn} | Date: {datetime.now().strftime('%Y-%m-%d')}")
        main(dut_sn)
        end_time = time.perf_counter_ns()
        duration = end_time - start_time
        duration = format_duration_long(duration / 1e9)
        logger.info(f"Execution completed in {duration}.")
    except KeyboardInterrupt:
        logger.warning("Operation interrupted by user.")
        error = 130
    except Exception as e:
        logger.warning(f"A fatal error has occurred: {repr(e)}\n{traceback.format_exc()}")
        error = 1
    finally:
        # Clean up logging handlers
        for handler in logger.handlers:
            handler.close()
        logger.handlers.clear()
        sys.exit(error)
