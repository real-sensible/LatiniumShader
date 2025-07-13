from __future__ import annotations
import imgui_bundle
from imgui_bundle import imgui


class Overlay:
    def __init__(self):
        self.show = True

    def draw(self, textures: dict[str, int]):
        if not self.show:
            return
        if imgui.begin("Debug Textures", True)[0]:
            for name, tex in textures.items():
                imgui.text(name)
                imgui.image(tex, 128, 128)
        imgui.end()
