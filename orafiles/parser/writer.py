"""Writer to convert AST back to formatted Oracle .ora text."""

from __future__ import annotations
from orafiles.parser.ast_nodes import NVPair, NVList, NVValue, ConfigFile


class Writer:
    """Convert AST nodes back to formatted Oracle .ora text.

    Produces standard Oracle formatting with proper indentation.
    """

    def __init__(self, indent: int = 2):
        self.indent = indent

    def write(self, node: ConfigFile) -> str:
        lines = []
        for i, entry in enumerate(node.entries):
            if i > 0:
                lines.append("")
            lines.append(self._write_entry(entry, 0))
        return "\n".join(lines) + "\n" if lines else ""

    def _write_entry(self, pair: NVPair, depth: int) -> str:
        if isinstance(pair.value, NVValue):
            prefix = " " * (self.indent * depth)
            return f"{prefix}{pair.key} = {pair.value.value}"
        elif isinstance(pair.value, NVList):
            return self._write_pair_with_list(pair, depth)
        return ""

    def _write_pair_with_list(self, pair: NVPair, depth: int) -> str:
        prefix = " " * (self.indent * depth)
        inner_prefix = " " * (self.indent * (depth + 1))
        lines = [f"{prefix}{pair.key} ="]

        nvlist = pair.value
        # Check if this is a simple list of values (no nested pairs)
        all_values = all(isinstance(item, NVValue) for item in nvlist.items)

        if all_values and len(nvlist.items) <= 5:
            # Inline format for short value lists
            vals = ", ".join(item.value for item in nvlist.items)
            lines[0] = f"{prefix}{pair.key} = ({vals})"
            return lines[0]

        lines[0] += "\n" + prefix + "("
        for item in nvlist.items:
            if isinstance(item, NVPair):
                lines.append(self._write_entry(item, depth + 1))
            elif isinstance(item, NVValue):
                lines.append(f"{inner_prefix}{item.value}")
            elif isinstance(item, NVList):
                # Nested anonymous list
                lines.append(self._write_list(item, depth + 1))
        lines.append(prefix + ")")
        return "\n".join(lines)

    def _write_list(self, nvlist: NVList, depth: int) -> str:
        prefix = " " * (self.indent * depth)
        inner_prefix = " " * (self.indent * (depth + 1))
        lines = [prefix + "("]
        for item in nvlist.items:
            if isinstance(item, NVPair):
                lines.append(self._write_entry(item, depth + 1))
            elif isinstance(item, NVValue):
                lines.append(f"{inner_prefix}{item.value}")
            elif isinstance(item, NVList):
                lines.append(self._write_list(item, depth + 1))
        lines.append(prefix + ")")
        return "\n".join(lines)


def write_ora(config: ConfigFile, indent: int = 2) -> str:
    """Convenience function to write a ConfigFile AST to text."""
    return Writer(indent=indent).write(config)
