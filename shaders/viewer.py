#!/usr/bin/env python3
"""Minimal shader viewer for LatiniumShader, optimized for Minecraft shader development.

Opens a GLFW window and displays the output of a fragment shader on a fullscreen
quad. The default shaders are `gbuffers_textured.vsh` and `gbuffers_textured.fsh`
in the same directory as the script, but alternative paths can be passed on the
command line. Supports common shader uniforms like iTime and iResolution.
"""

from __future__ import annotations
import sys
from pathlib import Path
from typing import Iterable
import glfw  # type: ignore
import moderngl  # type: ignore
from array import array

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_VSH = SCRIPT_DIR / "gbuffers_textured.vsh"
DEFAULT_FSH = SCRIPT_DIR / "gbuffers_textured.fsh"


def _read_shader(path: Path, visited: set[Path] | None = None) -> str:
    """Read a shader file and resolve #include directives recursively."""
    if visited is None:
        visited = set()

    path = path.resolve()

    if path in visited:
        raise ValueError(f"Circular include detected: {path}")
    visited.add(path)

    if not path.exists():
        raise FileNotFoundError(
            f"Shader file not found: {path}\n"
            f"Ensure the file exists in {path.parent}\n"
            f"Script directory: {SCRIPT_DIR}"
        )

    src = path.read_text()
    result = []

    for line in src.splitlines():
        line_strip = line.strip()
        if line_strip.startswith("#include"):
            try:
                inc = line_strip.split()[1].strip('"<>')
            except IndexError:
                raise ValueError(f"Malformed #include directive in {path}: {line}")

            # Always treat includes as relative!
            inc = inc.lstrip("/\\")  # Remove leading slash or backslash if present
            inc_path = (path.parent / inc).resolve()
            print(f"[DEBUG] Including file: {inc_path}")

            if not inc_path.exists():
                raise FileNotFoundError(
                    f"Included file not found: {inc_path}\n"
                    f"Included from: {path}\n"
                    f"Line: {line}"
                )

            result.append(_read_shader(inc_path, visited))
        else:
            result.append(line)

    return "\n".join(result)


class Viewer:
    def __init__(self, vertex_path: Path, fragment_path: Path) -> None:
        # Validate shader paths
        for path in (vertex_path, fragment_path):
            if not path.exists():
                raise FileNotFoundError(
                    f"Shader file not found: {path}\n"
                    f"Ensure the file exists in {path.parent}\n"
                    f"Script directory: {SCRIPT_DIR}"
                )

        if not glfw.init():
            raise RuntimeError("Failed to initialize GLFW")

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.SAMPLES, 4)  # Enable multisampling

        self.window = glfw.create_window(800, 600, "Minecraft Shader Viewer", None, None)
        if not self.window:
            glfw.terminate()
            raise RuntimeError("Failed to create GLFW window")

        glfw.make_context_current(self.window)
        glfw.swap_interval(1)  # Enable vsync
        self.ctx = moderngl.create_context()

        vs_src = _read_shader(vertex_path)
        fs_src = _read_shader(fragment_path)
        try:
            self.prog = self.ctx.program(vertex_shader=vs_src, fragment_shader=fs_src)
        except moderngl.Error as e:
            print(f"Shader compilation failed: {e}")
            # Fallback vertex shader
            fallback_vs = """
                #version 330 core
                in vec2 in_pos;
                in vec2 in_uv;
                out vec2 texcoord;
                void main() {
                    texcoord = in_uv;
                    gl_Position = vec4(in_pos, 0.0, 1.0);
                }
            """
            self.prog = self.ctx.program(vertex_shader=fallback_vs, fragment_shader=fs_src)

        vertices = array(
            "f",
            [
                -1.0, -1.0, 0.0, 0.0,  # Bottom-left
                 1.0, -1.0, 1.0, 0.0,  # Bottom-right
                -1.0,  1.0, 0.0, 1.0,  # Top-left
                 1.0,  1.0, 1.0, 1.0,  # Top-right
            ],
        )
        self.vbo = self.ctx.buffer(vertices.tobytes())
        self.vao = self.ctx.vertex_array(
            self.prog, [(self.vbo, "2f 2f", "in_pos", "in_uv")]
        )

    def run(self) -> None:
        while not glfw.window_should_close(self.window):
            glfw.poll_events()

            # Update shader uniforms for Minecraft-like effects
            if "iTime" in self.prog:
                self.prog["iTime"].value = glfw.get_time()
            if "iResolution" in self.prog:
                width, height = glfw.get_window_size(self.window)
                self.prog["iResolution"].value = (float(width), float(height))

            self.ctx.clear(0.0, 0.0, 0.0, 1.0)
            self.vao.render(mode=moderngl.TRIANGLE_STRIP)
            glfw.swap_buffers(self.window)

        glfw.terminate()


def main(argv: Iterable[str] | None = None) -> None:
    args = list(argv) if argv is not None else sys.argv[1:]
    try:
        vsh = Path(args[0]) if args else DEFAULT_VSH
        fsh = Path(args[1]) if len(args) > 1 else DEFAULT_FSH
    except IndexError:
        print("Error: Invalid command-line arguments. Usage: python viewer.py [vertex_shader] [fragment_shader]")
        sys.exit(1)

    viewer = Viewer(vsh, fsh)
    viewer.run()


if __name__ == "__main__":
    main()