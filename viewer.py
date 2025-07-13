#!/usr/bin/env python3
"""ModernGL-based viewer implementing the mini-Iris laboratory roadmap."""
from __future__ import annotations

import sys
from pathlib import Path

import glfw  # type: ignore
import moderngl  # type: ignore
import numpy as np
import pyrr

from utils.shader_loader import read_shader
from utils.mesh_loader import load_mesh
from utils.camera import build_matrices
from overlay import Overlay
import watcher

SCRIPT_DIR = Path(__file__).parent
MODEL_PATH = SCRIPT_DIR / "models" / "box.gltf"

IRIS_TEXTURE_UNITS = {
    "texture": 0,
    "lightmap": 1,
    "shadowtex0": 2,
    "shadowtex1": 3,
    "shadowcolor0": 4,
    "latiniumGIEnvMap": 5,
}


def recompile(ctx: moderngl.Context, vertex_path: Path, fragment_path: Path):
    vs_src = read_shader(vertex_path)
    fs_src = read_shader(fragment_path)
    return ctx.program(vertex_shader=vs_src, fragment_shader=fs_src)


def main(argv: list[str] | None = None) -> None:
    args = argv if argv is not None else sys.argv[1:]
    vsh = Path(args[0]) if args else SCRIPT_DIR / "shaders" / "gbuffers_textured.vsh"
    fsh = Path(args[1]) if len(args) > 1 else SCRIPT_DIR / "shaders" / "gbuffers_textured.fsh"

    if not glfw.init():
        raise RuntimeError("Failed to init GLFW")

    window = glfw.create_window(800, 600, "Latinium Viewer", None, None)
    if not window:
        glfw.terminate()
        raise RuntimeError("Failed to create window")

    glfw.make_context_current(window)
    ctx = moderngl.create_context()

    prog = recompile(ctx, vsh, fsh)

    data, indices = load_mesh(MODEL_PATH)
    vbo = ctx.buffer(data.tobytes())
    ibo = ctx.buffer(indices.tobytes())
    vao_content = [
        (vbo, "3f 3f 2f", "in_pos", "in_normal", "in_uv"),
    ]
    vao = ctx.vertex_array(prog, vao_content, ibo)

    white_tex = ctx.texture((1, 1), 4, b"\xff\xff\xff\xff")

    overlay = Overlay()

    def reload_shaders():
        nonlocal prog, vao
        prog = recompile(ctx, vsh, fsh)
        vao = ctx.vertex_array(prog, vao_content, ibo)
        print("[INFO] Shaders reloaded")

    watch = watcher.watch([vsh.parent, fsh.parent], reload_shaders)

    cam_pos = np.array([3.0, 3.0, 3.0])
    cam_target = np.array([0.0, 0.0, 0.0])

    while not glfw.window_should_close(window):
        glfw.poll_events()
        width, height = glfw.get_window_size(window)
        aspect = width / height
        mv, mvinv, proj = build_matrices(cam_pos, cam_target, 70.0, aspect)
        if "gbufferModelView" in prog:
            prog["gbufferModelView"].write(mv.astype("f4").tobytes())
        if "gbufferModelViewInverse" in prog:
            prog["gbufferModelViewInverse"].write(mvinv.astype("f4").tobytes())
        if "gl_ProjectionMatrix" in prog:
            prog["gl_ProjectionMatrix"].write(proj.astype("f4").tobytes())
        if "iTime" in prog:
            prog["iTime"].value = glfw.get_time()
        if "iResolution" in prog:
            prog["iResolution"].value = (float(width), float(height))

        for name, unit in IRIS_TEXTURE_UNITS.items():
            if name in prog:
                white_tex.use(location=unit)
                prog[name].value = unit

        ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)
        ctx.clear(0.1, 0.1, 0.1, 1.0)
        vao.render()
        overlay.draw({})
        glfw.swap_buffers(window)

    watch.stop()
    glfw.terminate()


if __name__ == "__main__":
    main()
