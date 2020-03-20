"""Commands to manipulate hard-coded locations on screen.

Not to be used in general - hard-coding is unreliable. Only use in specific
situations.

"""


from talon import ui, ctrl
from talon.voice import Context


class CORNERS:
    # Map to strings so we can compare to straight strings.
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"


# TODO: Can click relative to the screen, allow clicking relative to the window.


def corner_move(relative_to, x, y):
    """Move the mouse to a position relative to a corner."""
    screen = ui.main_screen().rect
    if relative_to == CORNERS.TOP_LEFT:
        corner = (0, 0)
    elif relative_to == CORNERS.TOP_RIGHT:
        corner = (screen.width, 0)
    elif relative_to == CORNERS.BOTTOM_LEFT:
        corner = (0, screen.height)
    elif relative_to == CORNERS.BOTTOM_RIGHT:
        corner = (screen.width, screen.height)
    else:
        raise ValueError(f"Invalid corner: {relative_to}")
    x = corner[0] + x
    y = corner[1] + y
    ctrl.mouse_move(x=x, y=y)


def make_corner_move(relative_to, x, y):
    def do_move(m=None):
        nonlocal relative_to, x, y
        corner_move(relative_to, x, y)

    return do_move


def corner_click(relative_to, x, y, **kwargs):
    """Click a position, relative to a corner."""
    corner_move(relative_to, x, y)
    ctrl.mouse_click(**kwargs)


def make_corner_click(relative_to, x, y, **kwargs):
    def do_click(m=None):
        nonlocal relative_to, x, y, kwargs
        corner_click(relative_to, x, y, **kwargs)

    return do_click


def print_mouse(m):
    """Print the mouse position relative to each corner.

    Use to get hard-codable positions.

    """
    pos = ctrl.mouse_pos()
    print(f"Mouse pos: {pos}")
    screen = ui.main_screen().rect
    print(f"Screen:    {screen}")
    for (position, corner_x, corner_y) in [
        ("top left", 0, 0),
        ("top right", screen.width, 0),
        ("bottom left", 0, screen.height),
        ("bottom right", screen.width, screen.height),
    ]:
        relative = (pos[0] - corner_x, pos[1] - corner_y)
        print(f"Position relative to {position}: {relative}")


# Use for hard-coding buttons.
print_mouse_context = Context("print_mouse_position")
print_mouse_context.keymap({"print mouse": print_mouse})
