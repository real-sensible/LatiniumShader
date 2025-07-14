from __future__ import annotations
import pyrr

from utils.debug import get_logger

log = get_logger(__name__)


def build_matrices(cam_pos, cam_target, fov, aspect):
    log.debug(
        "Building matrices pos=%s target=%s fov=%s aspect=%s",
        cam_pos,
        cam_target,
        fov,
        aspect,
    )
    view = pyrr.matrix44.create_look_at(cam_pos, cam_target, [0, 1, 0])
    proj = pyrr.matrix44.create_perspective_projection(fov, aspect, 0.1, 100.0)
    mv = view
    mvinv = pyrr.matrix44.inverse(mv)
    return mv, mvinv, proj
