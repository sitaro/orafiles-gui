"""AST nodes for Oracle NV-pair configuration files."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Union


@dataclass
class NVValue:
    """A simple string value in a name-value pair."""
    value: str

    def __repr__(self):
        return f"NVValue({self.value!r})"


@dataclass
class NVList:
    """A parenthesized list of NV pairs or values."""
    items: list[Union[NVPair, NVValue]] = field(default_factory=list)

    def __repr__(self):
        return f"NVList({self.items!r})"

    def find(self, key: str) -> NVPair | None:
        """Find first child NVPair with given key (case-insensitive)."""
        key_upper = key.upper()
        for item in self.items:
            if isinstance(item, NVPair) and item.key.upper() == key_upper:
                return item
        return None

    def find_all(self, key: str) -> list[NVPair]:
        """Find all child NVPairs with given key (case-insensitive)."""
        key_upper = key.upper()
        return [
            item for item in self.items
            if isinstance(item, NVPair) and item.key.upper() == key_upper
        ]

    def get_value(self, key: str) -> str | None:
        """Get string value of first child NVPair with given key."""
        pair = self.find(key)
        if pair and isinstance(pair.value, NVValue):
            return pair.value.value
        return None


@dataclass
class NVPair:
    """A name-value pair: KEY = VALUE or KEY = (list)."""
    key: str
    value: Union[NVValue, NVList]

    def __repr__(self):
        return f"NVPair({self.key!r}, {self.value!r})"

    def get_value(self) -> str | None:
        """Get string value if this pair has a simple value."""
        if isinstance(self.value, NVValue):
            return self.value.value
        return None

    def get_list(self) -> NVList | None:
        """Get list value if this pair has a list."""
        if isinstance(self.value, NVList):
            return self.value
        return None


@dataclass
class ConfigFile:
    """Root node: a collection of top-level NV pairs."""
    entries: list[NVPair] = field(default_factory=list)

    def find(self, key: str) -> NVPair | None:
        """Find first top-level entry with given key."""
        key_upper = key.upper()
        for entry in self.entries:
            if entry.key.upper() == key_upper:
                return entry
        return None

    def find_all(self, key: str) -> list[NVPair]:
        """Find all top-level entries with given key."""
        key_upper = key.upper()
        return [e for e in self.entries if e.key.upper() == key_upper]

    def get_value(self, key: str) -> str | None:
        """Get string value of first top-level entry with given key."""
        pair = self.find(key)
        if pair:
            return pair.get_value()
        return None
