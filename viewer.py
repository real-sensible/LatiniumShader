#!/usr/bin/env python3
"""Minimal shader viewer for LatiniumShader.

Opens a GLFW window and displays the output of a fragment shader on a fullscreen
quad. The default shaders are ``shaders/gbuffers_textured.vsh`` and
``shaders/gbuffers_textured.fsh`` but alternative paths can be passed on the
command line. The viewer requires the vertex shader to expose ``in_pos`` and
``in_uv`` attributes. If they are missing or the shader fails to compile, a
built-in fallback vertex shader is used instead.
"""

from __future__ import annotations
import sys
from pathlib import Path
from typing import Iterable

import glfw  # type: ignore
import moderngl  # type: ignore
from array import array

DEFAULT_VSH = Path("shaders/gbuffers_textured.vsh")
DEFAULT_FSH = Path("shaders/gbuffers_textured.fsh")

# Vertex shader used when the provided shader fails to compile or does not
# expose the expected attributes. ``in_pos`` and ``in_uv`` are required for
# the fullscreen quad setup.
FALLBACK_VERTEX_SHADER = """
    #version 330 core
    in vec2 in_pos;
    in vec2 in_uv;
    out vec2 texcoord;
    void main() {
        texcoord = in_uv;
        gl_Position = vec4(in_pos, 0.0, 1.0);
    }
"""


def _read_shader(path: Path) -> str:
    """Read a shader file and resolve simple ``#include"`` directives."""
    src = path.read_text()
    result: list[str] = []
    for line in src.splitlines():
        line_strip = line.strip()
        if line_strip.startswith("#include"):
            # Expect format: #include "path"
            inc = line_strip.split()[1].strip('"<>')
            inc_path = (path.parent / inc).resolve()
            if not inc_path.exists():
                inc_path = Path(inc)
            result.append(_read_shader(inc_path))
        else:
            result.append(line)
    return "\n".join(result)


class Viewer:
    def __init__(self, vertex_path: Path, fragment_path: Path) -> None:
        if not glfw.init():
            raise RuntimeError("Failed to initialize GLFW")

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

        self.window = glfw.create_window(800, 600, "Latinium Shader Viewer", None, None)
        if not self.window:
            glfw.terminate()
            raise RuntimeError("Failed to create GLFW window")

        glfw.make_context_current(self.window)
        self.ctx = moderngl.create_context()

        vs_src = _read_shader(vertex_path)
        fs_src = _read_shader(fragment_path)
        try:
            prog = self.ctx.program(vertex_shader=vs_src, fragment_shader=fs_src)
        except moderngl.Error:
            # Fallback vertex shader for GLSL compatibility issues
            prog = self.ctx.program(vertex_shader=FALLBACK_VERTEX_SHADER, fragment_shader=fs_src)
        else:
            # Ensure required attributes are present
            if "in_pos" not in prog.attributes or "in_uv" not in prog.attributes:
                # The provided vertex shader compiled but does not expose the
                # attributes needed for the quad.
                prog = self.ctx.program(vertex_shader=FALLBACK_VERTEX_SHADER, fragment_shader=fs_src)

        self.prog = prog

        vertices = array(
            "f",
            [
                -1.0,
                -1.0,
                0.0,
                0.0,
                1.0,
                -1.0,
                1.0,
                0.0,
                -1.0,
                1.0,
                0.0,
                1.0,
                1.0,
                1.0,
                1.0,
                1.0,
            ],
        )
        self.vbo = self.ctx.buffer(vertices.tobytes())
        self.vao = self.ctx.vertex_array(
            self.prog, [(self.vbo, "2f 2f", "in_pos", "in_uv")]
        )

    def run(self) -> None:
        while not glfw.window_should_close(self.window):
            glfw.poll_events()
            self.ctx.clear(0.0, 0.0, 0.0, 1.0)
            self.vao.render(mode=moderngl.TRIANGLE_STRIP)
            glfw.swap_buffers(self.window)
        glfw.terminate()


def main(argv: Iterable[str] | None = None) -> None:
    args = list(argv) if argv is not None else sys.argv[1:]
    vsh = Path(args[0]) if args else DEFAULT_VSH
    fsh = Path(args[1]) if len(args) > 1 else DEFAULT_FSH
    viewer = Viewer(vsh, fsh)
    viewer.run()


if __name__ == "__main__":
    main()
