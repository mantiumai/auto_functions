import functools
import logging
from typing import Any, Mapping

import structlog
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from structlog.stdlib import ProcessorFormatter
from structlog.types import FilteringBoundLogger
from structlog.typing import EventDict, Processor, WrappedLogger


class LoggingConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="logging_")

    for_stdlib: bool = False
    min_level: str = "INFO"

    @field_validator("min_level")
    @classmethod
    def validate_min_level(cls, min_level: str) -> str:
        """Validate that the level is a valid log level string"""
        if min_level not in logging.getLevelNamesMapping():
            raise ValueError("must be a valid log level name")
        return min_level


def render_extras(_: WrappedLogger, __: str, event_dict: EventDict) -> EventDict:
    """
    Lift an ``extra`` field that is a dictionary into the event dictionary.

    This makes the logger behave more like the standard library logger without the rigamarole of setting up
    Standard Library Logging in structlog i.e. https://www.structlog.org/en/stable/standard-library.html#stdlib-config
    """

    extra: Mapping[str, Any] | None = event_dict.pop("extra", None)

    if extra and isinstance(extra, dict):
        for key, value in extra.items():
            if key not in event_dict:
                event_dict[key] = value

    return event_dict


@functools.cache
def get_logger() -> FilteringBoundLogger:
    """Initialize and return a logger

    :return: A configured logger
    """
    config = LoggingConfig()
    min_level = logging.getLevelNamesMapping()[config.min_level]

    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.dev.set_exc_info,
        render_extras,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.ExceptionRenderer(),
        structlog.processors.StackInfoRenderer(),
    ]

    if config.for_stdlib:
        processors.append(ProcessorFormatter.remove_processors_meta)

    processors.append(structlog.processors.JSONRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(min_level),
        logger_factory=structlog.PrintLoggerFactory(),
    )

    return structlog.get_logger("main")


__all__ = ["get_logger"]
