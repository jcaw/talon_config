import math
import threading
from typing import Callable

from talon import cron, actions, Module, Context
from talon_plugins import eye_mouse


_NORTH_THETA = math.atan2(0, -1)
_GAZE_MIDPOINT = (0.5, 0.5)


def angle_from_north(center, point):
    """Get the angle of `point` from center, relative to north.

    Unit is degrees, not radians.

    """
    # center_phase = cmath.phase(complex(*center))
    # point_phase = cmath.phase(complex(*point))
    # # Amount to rotate (clockwise, in degrees) to normalize to north.
    # offset = -45
    # return (center_phase - point_phase) * 180 / cmath.pi + offset
    vector = (
        point[0] - center[0],
        point[1] - center[1],
    )
    vector_theta = math.atan2(vector[0], vector[1])
    angle = (_NORTH_THETA - vector_theta) * (180.0 / math.pi)
    return angle


def edge_mouse_scroll(north, south, east, west):
    """Map scroller that moves the mouse to the edge of the screen."""
    screen = eye_mouse.main_screen.rect
    if east:
        x = 0
    elif west:
        x = screen.width
    else:
        x = round(screen.width / 2)
    if north:
        y = 0
    elif south:
        y = screen.height
    else:
        y = round(screen.height / 2)
    # TODO: Maybe figure out a way of not hammering this
    actions.mouse_move(x, y)


class KeyMover:
    """Allows movement by holding keys."""

    def __init__(
        self, north_key="up", south_key="down", east_key="left", west_key="right"
    ):
        """Create a new mover that scrolls with keys."""
        self.north_key = north_key
        self.south_key = south_key
        self.east_key = east_key
        self.west_key = west_key
        self._pressed_keys = set()
        self._lock = threading.Lock()

    def do_move(self, north, south, east, west):
        """Update scroll with the given directions.

        This method can be passed to `EyeScroller`.

        """
        with self._lock:
            for direction, key in [
                (north, self.north_key),
                (south, self.south_key),
                (east, self.east_key),
                (west, self.west_key),
            ]:
                if direction:
                    if key not in self._pressed_keys:
                        actions.key(f"{key}:down")
                        self._pressed_keys.add(key)
                elif key in self._pressed_keys:
                    actions.key(f"{key}:up")
                    self._pressed_keys.remove(key)


class EyeScroller(object):
    """Scrolls the map where the user is looking."""

    _POLL_INTERVAL = "16ms"

    def __init__(self, move_function: Callable[[bool, bool, bool, bool], None]):
        """Create a new eye map scroller.

        :param move_function: this function will be called periodically to
          update the movement direction. It should take four directions, north,
          east, south and west, indicating which directions it should be moving
          in.

        """
        self._job = None
        self._move_function = move_function

    def start(self):
        self._update_scroll()
        self._job = cron.interval(self._POLL_INTERVAL, self._update_scroll)

    def stop(self):
        # Guard everything in case of spurious stops
        if self._job:
            cron.cancel(self._job)
            self._job = None
            # Move mouse to neutral position
            self._move_function(False, False, False, False)

    @staticmethod
    def _get_zones(rect):
        """Get the look zone angles for a particular rect.

        I.e:

                   Origin
                      |
                   0  |  1
            .---------+---------.
            |       | | |       |
           7|----.   |||   .----|2
            |     >---#---<     |
           6|----'   | |   '----|3
            |       |   |       |
            '-------------------'
                   5     4

        """
        width = rect.width
        height = rect.height
        zone_limits = [None] * 8
        zone_limits[0] = (width * 0.25, 0)
        zone_limits[1] = (width * 0.75, 0)
        zone_limits[2] = (width, height * 0.25)
        zone_limits[3] = (width, height * 0.75)
        zone_limits[4] = (width * 0.75, height)
        zone_limits[5] = (width * 0.25, height)
        zone_limits[6] = (0, height * 0.75)
        zone_limits[7] = (0, height * 0.25)
        center = (
            rect.center.x,
            rect.center.y,
        )
        return [angle_from_north(center, point) for point in zone_limits]

    def _update_scroll(self):
        if len(eye_mouse.mouse.eye_hist) < 2:
            return
        left_eye, right_eye = eye_mouse.mouse.eye_hist[-1]
        gaze_position = (left_eye.gaze + right_eye.gaze) / 2
        gaze_found = (
            -0.02 < gaze_position.x < 1.02
            and -0.02 < gaze_position.y < 1.02
            # TODO: Won't work if only picking up one eye
            and bool(left_eye or right_eye)
        )
        # TODO: Maybe cache this on entry? Not gonna change during.
        if gaze_found:
            zones = self._get_zones(eye_mouse.main_screen.rect)
            gaze_angle = angle_from_north(
                _GAZE_MIDPOINT, (gaze_position.x, gaze_position.y)
            )
            # TODO: Maybe deadzone?
            west = zones[1] <= gaze_angle < zones[4]
            south = zones[3] <= gaze_angle < zones[6]
            east = zones[5] <= gaze_angle
            north = zones[7] <= gaze_angle or gaze_angle < zones[2]
            self._move_function(north, south, east, west)


module = Module()
module.tag(
    "hiss_edge_map_move",
    "Activates strategy game map scroll - hiss to look around by moving mouse to screen edge.",
)
module.tag(
    "hiss_arrows_map_move",
    "Activates strategy game map scroll - hiss to look around via arrow keys.",
)


# Note we explicitly respect hiss-to-move on the zoom mouse.
edge_mouse_context = Context()
edge_mouse_context.matches = r"""
tag: user.hiss_edge_map_move
user.zoom_mouse_zooming: False
"""
arrows_context = Context()
arrows_context.matches = r"""
tag: user.hiss_arrows_map_move
user.zoom_mouse_zooming: False
"""


_edge_scroller = EyeScroller(edge_mouse_scroll)
_arrows_mover = KeyMover("up", "down", "left", "right")
_arrows_scroller = EyeScroller(_arrows_mover.do_move)


@edge_mouse_context.action_class("self")
class EdgeMouseActions:
    def on_hiss(start: bool):
        if start:
            _edge_scroller.start()
        else:
            _edge_scroller.stop()


@arrows_context.action_class("self")
class ArrowsActions:
    def on_hiss(start: bool):
        if start:
            _arrows_scroller.start()
        else:
            _arrows_scroller.stop()
