# cspell:words levelname

import argparse
import logging
import os
import shutil
import sys
from typing import Optional

from benjaminhamon_standard_extensions.logging import logging_helpers


def configure_logging(arguments: argparse.Namespace):
    message_format = "{asctime} [{levelname}][{name}] {message}"
    date_format = logging_helpers.date_format_iso

    log_stream_verbosity: str = "info"
    log_file_path: Optional[str] = None
    log_file_verbosity: str = "debug"

    if arguments is not None and getattr(arguments, "verbosity", None) is not None:
        log_stream_verbosity = arguments.verbosity
    if arguments is not None and getattr(arguments, "log_file", None) is not None:
        log_file_path = arguments.log_file
    if arguments is not None and getattr(arguments, "log_file_verbosity", None) is not None:
        log_file_verbosity = arguments.log_file_verbosity

    logging.root.setLevel(logging.DEBUG)

    logging.addLevelName(logging.DEBUG, "Debug")
    logging.addLevelName(logging.INFO, "Info")
    logging.addLevelName(logging.WARNING, "Warning")
    logging.addLevelName(logging.ERROR, "Error")
    logging.addLevelName(logging.CRITICAL, "Critical")

    logging_helpers.configure_log_stream(logging.root, sys.stdout, log_stream_verbosity, message_format, date_format)
    if log_file_path is not None:
        logging_helpers.configure_log_file(logging.root, log_file_path, log_file_verbosity, message_format, date_format, mode = "w", encoding = "utf-8")


def create_argument_parser() -> argparse.ArgumentParser:
    argument_parser = argparse.ArgumentParser()

    argument_parser.add_argument("--simulate", action = "store_true",
        help = "perform a test run, without writing changes")
    argument_parser.add_argument("--verbosity", choices = logging_helpers.all_log_levels,
        metavar = "<level>", help = "set the logging level (%s)" % ", ".join(logging_helpers.all_log_levels))
    argument_parser.add_argument("--log-file",
        metavar = "<file_path>", help = "set the log file path")
    argument_parser.add_argument("--log-file-verbosity", choices = logging_helpers.all_log_levels,
        metavar = "<level>", help = "set the logging level for the log file (%s)" % ", ".join(logging_helpers.all_log_levels))

    return argument_parser


def remove_directory(logger: logging.Logger, directory_to_remove: str, *, simulate: bool = False) -> None:
    if os.path.exists(directory_to_remove):
        logger.debug("Removing '%s'", directory_to_remove)
        if not simulate:
            shutil.rmtree(directory_to_remove)


def remove_file(logger: logging.Logger, file_to_remove: str, *, simulate: bool = False) -> None:
    if os.path.exists(file_to_remove):
        logger.debug("Removing '%s'", file_to_remove)
        if not simulate:
            os.remove(file_to_remove)
