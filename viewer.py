#!/usr/bin/env python3
"""ModernGL-based viewer implementing the mini-Iris laboratory roadmap."""
from __future__ import annotations

import time

import sys
import traceback
from pathlib import Path

from utils.debug import get_logger

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
MODEL_PATH = SCRIPT_DIR / "models" / "Box.glb"

IRIS_TEXTURE_UNITS = {
    "diffuseTexture": 0,
    "lightmap": 1,
    "shadowtex0": 2,
    "shadowtex1": 3,
    "shadowcolor0": 4,
    "latiniumGIEnvMap": 5,
}

log = get_logger(__name__)

def recompile(ctx: moderngl.Context, vertex_path: Path, fragment_path: Path):
    log.debug(f"Recompiling shaders: {vertex_path}, {fragment_path}")
    try:
        vs_src = read_shader(vertex_path)
        fs_src = read_shader(fragment_path)
        prog = ctx.program(vertex_shader=vs_src, fragment_shader=fs_src)
        log.debug("Shader compilation successful.")
        return prog
    except Exception as e:
        log.error("Shader compilation failed: %s", e)
        traceback.print_exc()
        raise

import imgui
def main(argv: list[str] | None = None) -> None:
    imgui.create_context()
    log.debug("Entered main()")
    args = argv if argv is not None else sys.argv[1:]
    vsh = Path(args[0]) if args else SCRIPT_DIR / "shaders" / "gbuffers_textured.vsh"
    fsh = Path(args[1]) if len(args) > 1 else SCRIPT_DIR / "shaders" / "gbuffers_textured.fsh"
    log.debug(f"Vertex shader: {vsh}, Fragment shader: {fsh}")

    log.info("Initializing GLFW...")
    if not glfw.init():
        log.error("Failed to init GLFW")
        raise RuntimeError("Failed to init GLFW")

    log.info("Creating window...")
    window = glfw.create_window(800, 600, "Latinium Viewer", None, None)
    if not window:
        log.error("Failed to create window")
        glfw.terminate()
        raise RuntimeError("Failed to create window")

    glfw.make_context_current(window)
    log.info("Creating ModernGL context...")
    try:
        ctx = moderngl.create_context()
        log.debug("ModernGL context created: %s", ctx)
    except Exception as e:
        log.error("ModernGL context creation failed: %s", e)
        traceback.print_exc()
        glfw.terminate()
        raise

    try:
        prog = recompile(ctx, vsh, fsh)
    except Exception as e:
        log.error("Initial shader compilation failed: %s", e)
        glfw.terminate()
        raise

    log.info("Shader _members:")
    for name, member in prog._members.items():
        log.info(f"{name}: {type(member).__name__}")

    log.info("Program attributes:")
    for attr in prog._members:
        if isinstance(prog._members[attr], moderngl.Attribute):
            log.info(f"  {attr}")

    log.debug(f"Loading mesh from: {MODEL_PATH}")
    try:
        data, indices = load_mesh(MODEL_PATH)
        log.debug("Mesh loaded successfully.")
        log.debug("First 5 vertices:")
        log.debug(str(data[:5]))
    except Exception as e:
        log.error("Mesh loading failed: %s", e)
        traceback.print_exc()
        glfw.terminate()
        raise

    log.info("Data shape: %s", data.shape)
    log.info("Indices shape: %s", indices.shape)
    log.info("Indices dtype: %s", indices.dtype)
    log.info("Max index: %s", indices.max())

    log.info("Creating VBO/IBO...")
    try:
        vbo = ctx.buffer(data.tobytes())
        if indices.dtype != np.uint32:
            log.debug("Indices dtype not uint32, converting...")
            indices = indices.astype(np.uint32)
        ibo = ctx.buffer(indices.tobytes())
    except Exception as e:
        log.error("Buffer creation failed: %s", e)
        traceback.print_exc()
        glfw.terminate()
        raise

    vao_content = [
        (vbo, "3f", "in_pos"),
        (vbo, "3f", "in_normal"),
        (vbo, "2f", "in_uv"),
    ]

    log.info("Creating VAO...")
    try:
        vao = ctx.vertex_array(prog, vao_content, ibo)
        log.debug("VAO created: %s", vao)
    except Exception as e:
        log.error("VAO creation failed: %s", e)
        traceback.print_exc()
        glfw.terminate()
        raise

    log.info("Creating default white texture...")
    try:
        white_tex = ctx.texture((1, 1), 4, b"\xff\xff\xff\xff")
        log.debug("White texture created.")
    except Exception as e:
        log.error("Texture creation failed: %s", e)
        traceback.print_exc()
        glfw.terminate()
        raise

    log.info("Creating overlay...")
    overlay = None
    try:
        overlay = Overlay(window)
        log.debug("Overlay created.")
    except Exception as e:
        log.error("Overlay creation failed: %s", e)
        traceback.print_exc()

    def reload_shaders():
        nonlocal prog, vao
        log.info("Reloading shaders...")
        try:
            prog = recompile(ctx, vsh, fsh)
            vao = ctx.vertex_array(prog, vao_content, ibo)
            log.info("Shaders reloaded successfully.")
        except Exception as e:
            log.error("Shader reload failed: %s", e)
            traceback.print_exc()

    log.info("Starting watcher...")
    try:
        watch = watcher.watch([vsh.parent, fsh.parent], reload_shaders)
        log.debug("Watcher started.")
    except Exception as e:
        log.error("Watcher failed: %s", e)
        traceback.print_exc()

    cam_pos = np.array([3.0, 3.0, 3.0])
    cam_target = np.array([0.0, 0.0, 0.0])
    log.debug(f"Camera initialized. Position: {cam_pos}, Target: {cam_target}")

    log.info("Entering main loop...")
    frame = 0
    try:
        while not glfw.window_should_close(window):
            log.debug(f"Frame {frame} start.")
            glfw.poll_events()
            width, height = glfw.get_window_size(window)
            aspect = width / height if height != 0 else 1.0
            log.debug(f"Window size: {width}x{height} (aspect {aspect})")
            try:
                mv, mvinv, proj = build_matrices(cam_pos, cam_target, 70.0, aspect)
                log.debug("Matrices built.")
            except Exception as e:
                log.error("Camera matrix calculation failed: %s", e)
                traceback.print_exc()
                break

            try:
                if "gbufferModelView" in prog:
                    prog["gbufferModelView"].write(mv.astype("f4").tobytes())
                if "gbufferModelViewInverse" in prog:
                    prog["gbufferModelViewInverse"].write(mvinv.astype("f4").tobytes())
                if "projectionMatrix" in prog:
                    prog["projectionMatrix"].write(proj.astype("f4").tobytes())
                if "iTime" in prog:
                    prog["iTime"].value = glfw.get_time()
                if "iResolution" in prog:
                    prog["iResolution"].value = (float(width), float(height))
            except Exception as e:
                log.error("Uniform update failed: %s", e)
                traceback.print_exc()

            for name, unit in IRIS_TEXTURE_UNITS.items():
                try:
                    if name in prog:
                        white_tex.use(location=unit)
                        prog[name].value = unit
                except Exception as e:
                    log.error("Texture/unit assignment failed for %s: %s", name, e)
                    traceback.print_exc()

            try:
                ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)
                ctx.clear(0.1, 0.1, 0.1, 1.0)
                ctx.clear(0.1, 0.1, 0.1, 1.0)
            except Exception as e:
                log.error("GL context setup failed: %s", e)
                traceback.print_exc()

            try:
                vao.render()
                ctx.finish()  # Forces all pending GL commands to complete
                log.debug("VAO rendered.")
            except Exception as e:
                log.error("Render failed: %s", e)
                traceback.print_exc()

            if overlay:
                try:
                    overlay.draw({})
                    log.debug("Post overlay draw")
                except Exception as e:
                    log.error("Overlay draw failed: %s", e)
                    traceback.print_exc()
            else:
                log.debug("Overlay not available, skipping draw")

            try:
                glfw.swap_buffers(window)
                log.debug("Post swap buffers")
            except Exception as e:
                log.error("Buffer swap failed: %s", e)
                traceback.print_exc()

            time.sleep(1)

            frame += 1

    except Exception as e:
        log.error("Main loop crashed: %s", e)
        traceback.print_exc()
    finally:
        try:
            watch.stop()
        except Exception as e:
            log.error("Watcher stop failed: %s", e)
        glfw.terminate()
        log.info("Exiting...")

if __name__ == "__main__":
    log.debug("Script invoked directly.")
    try:
        main()
    except Exception as e:
        log.error("Fatal exception in main(): %s", e)
        traceback.print_exc()
