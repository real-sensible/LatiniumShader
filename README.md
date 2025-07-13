# Latinium Shader Mini Lab

This repository provides a minimal Python-based viewer for developing
Minecraft shaders. It uses GLFW and ModernGL to emulate Iris' uniform
contract and includes utilities for loading meshes, hot reloading
shader files and displaying debug information via Dear ImGui.

## Requirements

- Python 3.11+
- `PyGLFW`
- `ModernGL`
- `trimesh`
- `pyrr`
- `imgui-bundle`
- `watchdog`

Install the dependencies with pip:

```bash
pip install glfw moderngl trimesh pyrr imgui-bundle watchdog
```

## Usage

Run the viewer with the default shaders:

```bash
python viewer.py
```

It will load the sample `models/box.gltf` and render it with the
`shaders/gbuffers_textured` pair. Editing shader files triggers an
automatic recompilation.
