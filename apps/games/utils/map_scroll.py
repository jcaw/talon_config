import math
import sys

from talon import cron, ctrl
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
    vector = (point[0] - center[0], point[1] - center[1])
    vector_theta = math.atan2(vector[0], vector[1])
    angle = (_NORTH_THETA - vector_theta) * (180.0 / math.pi)
    return angle


# import keyboard

# class CachedKey(object):
#     """Key that can be held, that caches the current state."""

#     def __init__(self, key):
#         self.key = key
#         self._pressed = False

#     def update(self, should_be_pressed):
#         if should_be_pressed and not self._pressed:
#             print("Holding")
#             keyboard.press(self.key)
#             self._pressed = True
#         elif self._pressed and not should_be_pressed:
#             print("Releasing")
#             keyboard.release(self.key)
#             self._pressed = False


# class EyeMapScroller(object):
#     """Scrolls the map where the user is looking."""

#     _POLL_INTERVAL = "20ms"

#     def __init__(self, north="up", east="right", south="down", west="left"):
#         self._north = CachedKey(north)
#         self._east = CachedKey(east)
#         self._south = CachedKey(south)
#         self._west = CachedKey(west)
#         self._job = None

#     def __enter__(self):
#         self._update_scroll()
#         self._job = cron.interval(self._POLL_INTERVAL, self._update_scroll)

#     def __exit__(self, *_):
#         if self._job:
#             cron.cancel(self._job)
#         # Release all keys
#         for key in [self._north, self._south, self._east, self._west]:
#             key.update(False)

#     @staticmethod
#     def _get_zones(rect):
#         """Get the look zone angles for a particular rect.

#         I.e:

#                    Origin
#                       |
#                    0  |  1
#              ---------+--------
#             |       \ | /       |
#            7|----\   \|/   /----|2
#             |     >---#---<     |
#            6|----/   / \   \----|3
#             |       /   \       |
#              -------------------
#                    5     4

#         """
#         width = rect.width
#         height = rect.height
#         zone_limits = [None] * 8
#         zone_limits[0] = (width * 0.25, 0)
#         zone_limits[1] = (width * 0.75, 0)
#         zone_limits[2] = (width, height * 0.25)
#         zone_limits[3] = (width, height * 0.75)
#         zone_limits[4] = (width * 0.75, height)
#         zone_limits[5] = (width * 0.25, height)
#         zone_limits[6] = (0, height * 0.75)
#         zone_limits[7] = (0, height * 0.25)
#         return [angle_from_north(rect.center, point) for point in zone_limits]

#     def _update_scroll(self):
#         if len(eye_mouse.mouse.eye_hist) < 2:
#             return
#         left_eye, right_eye = eye_mouse.mouse.eye_hist[-1]
#         gaze_position = (left_eye.gaze + right_eye.gaze) / 2
#         gaze_found = (
#             -0.02 < gaze_position.x < 1.02
#             and -0.02 < gaze_position.y < 1.02
#             # TODO: Won't work if only picking up one eye
#             and bool(left_eye or right_eye)
#         )
#         # TODO: Maybe cache this on entry? Not gonna change during.
#         if gaze_found:
#             zones = self._get_zones(eye_mouse.main_screen.rect)
#             gaze_angle = angle_from_north(
#                 _GAZE_MIDPOINT, (gaze_position.x, gaze_position.y)
#             )
#             # TODO: Maybe deadzone?
#             self._scroll_with_keys(gaze_angle, zones)
#             east = zones[1] <= gaze_angle < zones[4]
#             south = zones[3] <= gaze_angle < zones[6]
#             west = zones[5] <= gaze_angle
#             north = zones[7] <= gaze_angle or gaze_angle < zones[2]
#             self._scroll_with_mouse(north, south, east, west)

#     def _scroll_with_keys(self, north, south, east, west):
#         self._east.update()
#         self._south.update()
#         # Angle can't be below zero or above 360 so we handle these
#         # differently.
#         self._west.update()
#         self._north.update()


class EyeMapScroller(object):
    """Scrolls the map where the user is looking."""

    _POLL_INTERVAL = "20ms"

    def __init__(self):
        self._job = None

    def __enter__(self):
        self._update_scroll()
        self._job = cron.interval(self._POLL_INTERVAL, self._update_scroll)

    def __exit__(self, *_):
        if self._job:
            cron.cancel(self._job)
        # Move mouse to neutral position
        self._set_mouse(eye_mouse.main_screen.rect, False, False, False, False)

    @staticmethod
    def _get_zones(rect):
        """Get the look zone angles for a particular rect.

        I.e:

                   Origin
                      |
                   0  |  1
             ---------+--------
            |       \ | /       |
           7|----\   \|/   /----|2
            |     >---#---<     |
           6|----/   / \   \----|3
            |       /   \       |
             -------------------
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
        return [angle_from_north(rect.center, point) for point in zone_limits]

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
            east = zones[1] <= gaze_angle < zones[4]
            south = zones[3] <= gaze_angle < zones[6]
            west = zones[5] <= gaze_angle
            north = zones[7] <= gaze_angle or gaze_angle < zones[2]
            self._set_mouse(eye_mouse.main_screen.rect, north, east, south, west)

    def _set_mouse(self, screen_rect, north, east, south, west):
        if west:
            x = 0
        elif east:
            x = screen_rect.width
        else:
            x = round(screen_rect.width / 2)
        if north:
            y = 0
        elif south:
            y = screen_rect.width
        else:
            y = round(screen_rect.width / 2)
        # TODO: Maybe figure out a way of not hammering this
        ctrl.mouse_move(x, y)
