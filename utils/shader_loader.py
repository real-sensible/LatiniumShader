from __future__ import annotations
from pathlib import Path

from utils.debug import get_logger

log = get_logger(__name__)


def read_shader(path: Path, visited: set[Path] | None = None) -> str:
    """Read a shader file resolving `#include` directives recursively."""
    if visited is None:
        visited = set()
    path = path.resolve()
    log.debug("Reading shader %s", path)
    if path in visited:
        raise ValueError(f"Circular include detected: {path}")
    visited.add(path)
    if not path.exists():
        raise FileNotFoundError(f"Shader file not found: {path}")

    src = path.read_text()
    result: list[str] = []
    for line in src.splitlines():
        stripped = line.strip()
        if stripped.startswith("#include"):
            parts = stripped.split(maxsplit=1)
            if len(parts) != 2:
                raise ValueError(f"Malformed #include: {line}")
            inc = parts[1].strip('"<>')
            inc_path = (path.parent / inc).resolve()
            log.debug("Including shader %s", inc_path)
            result.append(read_shader(inc_path, visited))
        else:
            result.append(line)
    src_final = "\n".join(result)
    log.debug("Shader %s loaded", path)
    return src_final
