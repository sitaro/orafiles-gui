"""Base model with validation support."""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class ValidationError:
    field: str
    message: str


@dataclass
class BaseModel:
    """Base class for all configuration models."""

    def validate(self) -> list[ValidationError]:
        """Validate the model and return a list of errors."""
        return []

    def is_valid(self) -> bool:
        return len(self.validate()) == 0

    @staticmethod
    def _validate_port(value: str, field_name: str) -> list[ValidationError]:
        errors = []
        if value:
            try:
                port = int(value)
                if not (1 <= port <= 65535):
                    errors.append(ValidationError(field_name, "Port must be between 1 and 65535"))
            except ValueError:
                errors.append(ValidationError(field_name, "Port must be a number"))
        return errors

    @staticmethod
    def _validate_positive_int(value: str, field_name: str) -> list[ValidationError]:
        errors = []
        if value:
            try:
                n = int(value)
                if n < 0:
                    errors.append(ValidationError(field_name, "Value must be non-negative"))
            except ValueError:
                errors.append(ValidationError(field_name, "Value must be a number"))
        return errors
