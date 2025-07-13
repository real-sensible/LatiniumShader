import imgui
from imgui.integrations.glfw import GlfwRenderer

class Overlay:
    def __init__(self, window):
        self.show = True
        self.renderer = GlfwRenderer(window)

    def draw(self, textures: dict[str, int]):
        if not self.show:
            return
        self.renderer.process_inputs()
        imgui.new_frame()

        if imgui.begin("Debug Textures", True)[0]:
            for name, tex in textures.items():
                imgui.text(name)
                imgui.image(tex, 128, 128)
        imgui.end()

        imgui.render()
        self.renderer.render(imgui.get_draw_data())
