from talon.track.geom import Point2d

from talon_plugins import eye_zoom_mouse
from talon_plugins.eye_zoom_mouse import config


# Zoom level
config.img_scale = 6
# How many datapoints to include in the eye average.
# Bigger = smoother but slower motion
config.eye_avg = 5
# Move the mouse while zoomed?
config.track_mouse = False
# Zoom frames
config.frames = 5

ZOOM_BOX_WIDTH = 1200
ZOOM_BOX_HEIGHT = 900


#############################################################################


def DeriveScreenArea(img_scale, zoom_box_width, zoom_box_height):
    """Derive the area to zoom in on from the target window and zoom level."""
    return Point2d(
        round(zoom_box_width / img_scale), round(zoom_box_height / img_scale)
    )


# Grab an area that will result in the specified zoom box height & width.
config.screen_area = DeriveScreenArea(config.img_scale, ZOOM_BOX_WIDTH, ZOOM_BOX_HEIGHT)


# Enable zoom mouse on startup.
eye_zoom_mouse.active.enable()
eye_zoom_mouse.active.check()
