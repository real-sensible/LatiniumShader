#!/usr/bin/env python3
import sys
from pathlib import Path
import glfw
import moderngl
from array import array

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_VSH = SCRIPT_DIR / "gbuffers_textured.vsh"
DEFAULT_FSH = SCRIPT_DIR / "gbuffers_textured.fsh"

def _read_shader(path):
    return path.read_text()

class Viewer:
    def __init__(self, vertex_path, fragment_path):
        if not glfw.init():
            raise RuntimeError("Failed to initialize GLFW")
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 2)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
        window = glfw.create_window(800, 600, "Minimal Shader Viewer", None, None)
        if not window:
            glfw.terminate()
            raise RuntimeError("Failed to create GLFW window")
        glfw.make_context_current(window)
        self.window = window
        self.ctx = moderngl.create_context()

        vs_src = _read_shader(vertex_path)
        fs_src = _read_shader(fragment_path)
        print("=== VERTEX SHADER ===\n", vs_src)
        print("=== FRAGMENT SHADER ===\n", fs_src)
        self.prog = self.ctx.program(vertex_shader=vs_src, fragment_shader=fs_src)

        vertices = array(
            "f",
            [
                -1.0, -1.0, 0.0, 0.0,
                 1.0, -1.0, 1.0, 0.0,
                -1.0,  1.0, 0.0, 1.0,
                 1.0,  1.0, 1.0, 1.0,
            ],
        )
        self.vbo = self.ctx.buffer(vertices.tobytes())
        self.vao = self.ctx.vertex_array(
            self.prog, [(self.vbo, "2f 2f", "in_pos", "in_uv")]
        )

        # Bind white texture to all sampler2D uniforms
        white_tex = self.ctx.texture((2, 2), 4, data=b'\xff\xff\xff\xff' * 4)
        white_tex.build_mipmaps()
        possible_uniforms = [
            "texture", "lightmap", "shadowcolor0",
            "shadowtex0", "shadowtex1", "latiniumGIEnvMap"
        ]
        for i, name in enumerate(possible_uniforms):
            if name in self.prog:
                white_tex.use(location=i)
                self.prog[name].value = i

    def run(self):
        while not glfw.window_should_close(self.window):
            glfw.poll_events()
            self.ctx.clear(0.0, 0.0, 0.0, 1.0)
            self.vao.render(mode=moderngl.TRIANGLE_STRIP)
            glfw.swap_buffers(self.window)
        glfw.terminate()

def main(argv=None):
    args = list(argv) if argv is not None else sys.argv[1:]
    vsh = Path(args[0]) if args else DEFAULT_VSH
    fsh = Path(args[1]) if len(args) > 1 else DEFAULT_FSH
    viewer = Viewer(vsh, fsh)
    viewer.run()

if __name__ == "__main__":
    main()
