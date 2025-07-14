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

## Experimental ReSTIR GI Helpers

The `utils/restir.py` module introduces a minimal set of data
structures to experiment with reservoir based resampling techniques
as described in NVIDIA's ReSTIR GI paper. It implements weighted
reservoir sampling in pure Python so that higher level experiments
or prototypes can be built directly inside the viewer. The current
implementation is intentionally lightweight and does **not** provide a
full path tracer, but it forms the groundwork for integrating advanced
GI algorithms in the future.

Example usage:

```python
from utils.restir import Reservoir, Sample

reservoir = Reservoir()
# example candidate sample with arbitrary values
candidate = Sample(position=np.zeros(3), normal=np.array([0,0,1]),
                   radiance=np.ones(3), pdf=1.0)
reservoir.update(candidate, weight=1.0)
```

