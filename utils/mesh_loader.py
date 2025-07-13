from __future__ import annotations
from pathlib import Path
import trimesh
import numpy as np


def load_mesh(path: Path):
    """Load a mesh using trimesh and return vertex and index buffers."""
    mesh = trimesh.load(path, force='mesh')
    vertices = np.asarray(mesh.vertices, dtype='f4')
    normals = np.asarray(mesh.vertex_normals, dtype='f4')
    if mesh.visual.kind == 'texture' and mesh.visual.uv is not None:
        uvs = np.asarray(mesh.visual.uv, dtype='f4')
    else:
        uvs = np.zeros((len(vertices), 2), dtype='f4')
    data = np.hstack([vertices, normals, uvs])
    indices = np.asarray(mesh.faces, dtype='i4').reshape(-1)
    return data, indices
