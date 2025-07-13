#!/usr/bin/env python3
"""ModernGL-based viewer implementing the mini-Iris laboratory roadmap."""
from __future__ import annotations

import time

import sys
import traceback
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
MODEL_PATH = SCRIPT_DIR / "models" / "Box.glb"

IRIS_TEXTURE_UNITS = {
    "texture": 0,
    "lightmap": 1,
    "shadowtex0": 2,
    "shadowtex1": 3,
    "shadowcolor0": 4,
    "latiniumGIEnvMap": 5,
}

def recompile(ctx: moderngl.Context, vertex_path: Path, fragment_path: Path):
    print(f"[DEBUG] Recompiling shaders: {vertex_path}, {fragment_path}")
    try:
        vs_src = read_shader(vertex_path)
        fs_src = read_shader(fragment_path)
        prog = ctx.program(vertex_shader=vs_src, fragment_shader=fs_src)
        print("[DEBUG] Shader compilation successful.")
        return prog
    except Exception as e:
        print("[ERROR] Shader compilation failed:", e)
        traceback.print_exc()
        raise

import imgui
def main(argv: list[str] | None = None) -> None:
    imgui.create_context()
    print("[TRACE] Entered main()")
    args = argv if argv is not None else sys.argv[1:]
    vsh = Path(args[0]) if args else SCRIPT_DIR / "shaders" / "gbuffers_textured.vsh"
    fsh = Path(args[1]) if len(args) > 1 else SCRIPT_DIR / "shaders" / "gbuffers_textured.fsh"
    print(f"[DEBUG] Vertex shader: {vsh}, Fragment shader: {fsh}")

    print("[INFO] Initializing GLFW...")
    if not glfw.init():
        print("[ERROR] Failed to init GLFW")
        raise RuntimeError("Failed to init GLFW")

    print("[INFO] Creating window...")
    window = glfw.create_window(800, 600, "Latinium Viewer", None, None)
    if not window:
        print("[ERROR] Failed to create window")
        glfw.terminate()
        raise RuntimeError("Failed to create window")

    glfw.make_context_current(window)
    print("[INFO] Creating ModernGL context...")
    try:
        ctx = moderngl.create_context()
        print("[DEBUG] ModernGL context created:", ctx)
    except Exception as e:
        print("[ERROR] ModernGL context creation failed:", e)
        traceback.print_exc()
        glfw.terminate()
        raise

    try:
        prog = recompile(ctx, vsh, fsh)
    except Exception as e:
        print("[ERROR] Initial shader compilation failed:", e)
        glfw.terminate()
        raise

    print("[INFO] Shader _members:")
    for name, member in prog._members.items():
        print(f"{name}: {type(member).__name__}")

    print("Program attributes:")
    for attr in prog._members:
        if isinstance(prog._members[attr], moderngl.Attribute):
            print(f"  {attr}")

    print(f"[DEBUG] Loading mesh from: {MODEL_PATH}")
    try:
        data, indices = load_mesh(MODEL_PATH)
        print("[DEBUG] Mesh loaded successfully.")
        print("First 5 vertices:")
        print(data[:5])
    except Exception as e:
        print("[ERROR] Mesh loading failed:", e)
        traceback.print_exc()
        glfw.terminate()
        raise

    print("Data shape:", data.shape)
    print("Indices shape:", indices.shape)
    print("Indices dtype:", indices.dtype)
    print("Max index:", indices.max())

    print("[INFO] Creating VBO/IBO...")
    try:
        vbo = ctx.buffer(data.tobytes())
        if indices.dtype != np.uint32:
            print("[DEBUG] Indices dtype not uint32, converting...")
            indices = indices.astype(np.uint32)
        ibo = ctx.buffer(indices.tobytes())
    except Exception as e:
        print("[ERROR] Buffer creation failed:", e)
        traceback.print_exc()
        glfw.terminate()
        raise

    vao_content = [
        (vbo, "3f", "in_pos"),
        (vbo, "3f", "in_normal"),
        (vbo, "2f", "in_uv"),
    ]

    print("[INFO] Creating VAO...")
    try:
        vao = ctx.vertex_array(prog, vao_content, ibo)
        print("[DEBUG] VAO created:", vao)
    except Exception as e:
        print("[ERROR] VAO creation failed:", e)
        traceback.print_exc()
        glfw.terminate()
        raise

    print("[INFO] Creating default white texture...")
    try:
        white_tex = ctx.texture((1, 1), 4, b"\xff\xff\xff\xff")
        print("[DEBUG] White texture created.")
    except Exception as e:
        print("[ERROR] Texture creation failed:", e)
        traceback.print_exc()
        glfw.terminate()
        raise

    print("[INFO] Creating overlay...")
    overlay = None
    try:
        overlay = Overlay(window)
        print("[DEBUG] Overlay created.")
    except Exception as e:
        print("[ERROR] Overlay creation failed:", e)
        traceback.print_exc()

    def reload_shaders():
        nonlocal prog, vao
        print("[INFO] Reloading shaders...")
        try:
            prog = recompile(ctx, vsh, fsh)
            vao = ctx.vertex_array(prog, vao_content, ibo)
            print("[INFO] Shaders reloaded successfully.")
        except Exception as e:
            print("[ERROR] Shader reload failed:", e)
            traceback.print_exc()

    print("[INFO] Starting watcher...")
    try:
        watch = watcher.watch([vsh.parent, fsh.parent], reload_shaders)
        print("[DEBUG] Watcher started.")
    except Exception as e:
        print("[ERROR] Watcher failed:", e)
        traceback.print_exc()

    cam_pos = np.array([3.0, 3.0, 3.0])
    cam_target = np.array([0.0, 0.0, 0.0])
    print(f"[DEBUG] Camera initialized. Position: {cam_pos}, Target: {cam_target}")

    print("[INFO] Entering main loop...")
    frame = 0
    try:
        while not glfw.window_should_close(window):
            print(f"[TRACE] Frame {frame} start.")
            glfw.poll_events()
            width, height = glfw.get_window_size(window)
            aspect = width / height if height != 0 else 1.0
            print(f"[DEBUG] Window size: {width}x{height} (aspect {aspect})")
            try:
                mv, mvinv, proj = build_matrices(cam_pos, cam_target, 70.0, aspect)
                print("[DEBUG] Matrices built.")
            except Exception as e:
                print("[ERROR] Camera matrix calculation failed:", e)
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
                print("[ERROR] Uniform update failed:", e)
                traceback.print_exc()

            for name, unit in IRIS_TEXTURE_UNITS.items():
                try:
                    if name in prog:
                        white_tex.use(location=unit)
                        prog[name].value = unit
                except Exception as e:
                    print(f"[ERROR] Texture/unit assignment failed for {name}:", e)
                    traceback.print_exc()

            try:
                ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)
                ctx.clear(0.1, 0.1, 0.1, 1.0)
                ctx.clear(0.1, 0.1, 0.1, 1.0)
            except Exception as e:
                print("[ERROR] GL context setup failed:", e)
                traceback.print_exc()

            try:
                vao.render()
                ctx.finish()  # Forces all pending GL commands to complete
                print("[TRACE] VAO rendered.")
            except Exception as e:
                print("[ERROR] Render failed:", e)
                traceback.print_exc()

            if overlay:
                try:
                    overlay.draw({})
                    print("[TRACE] Post overlay draw")
                except Exception as e:
                    print("[ERROR] Overlay draw failed:", e)
                    traceback.print_exc()
            else:
                print("[TRACE] Overlay not available, skipping draw")

            try:
                glfw.swap_buffers(window)
                print("[TRACE] Post swap buffers")
            except Exception as e:
                print("[ERROR] Buffer swap failed:", e)
                traceback.print_exc()

            time.sleep(1)

            frame += 1

    except Exception as e:
        print("[ERROR] Main loop crashed:", e)
        traceback.print_exc()
    finally:
        try:
            watch.stop()
        except Exception as e:
            print("[ERROR] Watcher stop failed:", e)
        glfw.terminate()
        print("[INFO] Exiting...")

if __name__ == "__main__":
    print("[TRACE] Script invoked directly.")
    try:
        main()
    except Exception as e:
        print("[ERROR] Fatal exception in main():", e)
        traceback.print_exc()
