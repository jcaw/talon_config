"""Commands to manipulate hard-coded locations on screen.

Not to be used in general - hard-coding is unreliable. Only use in specific
situations.

"""


from talon import Module, actions, ui, ctrl


class Corner:
    """Holds a position relative to a corner."""

    # Map to strings so we can compare to straight strings.
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"

    def __init__(self, corner: str, x: int, y: int) -> None:
        assert corner in [
            self.TOP_LEFT,
            self.TOP_RIGHT,
            self.BOTTOM_LEFT,
            self.BOTTOM_RIGHT,
        ], corner
        self.corner = corner
        self.x = x
        self.y = y

    @staticmethod
    def absolute_position(corner: str):
        """Get the absolute position of a corner.

        :returns tuple[int, int]: the position of this corner.

        """
        screen = ui.main_screen().rect
        if corner == Corner.TOP_LEFT:
            return (0, 0)
        elif corner == Corner.TOP_RIGHT:
            return (screen.width, 0)
        elif corner == Corner.BOTTOM_LEFT:
            return (0, screen.height)
        elif corner == Corner.BOTTOM_RIGHT:
            return (screen.width, screen.height)
        else:
            raise ValueError(f'Invalid corner: "{corner}"')


# TODO: Can click relative to the screen, allow clicking relative to the window.


module = Module()


@module.action_class
class Actions:
    def corner_hover(position: Corner) -> None:
        """Move mouse to a specific position, relative to a corner."""
        corner = Corner.absolute_position(position.corner)
        x = corner[0] + position.x
        y = corner[1] + position.y
        actions.mouse_move(x, y)

    def corner_click(position: Corner) -> None:
        """Click a position, relative to a corner."""
        actions.self.corner_hover(Corner)
        actions.mouse_click()

    def print_mouse_positions() -> None:
        """Print the mouse position relative to each corner.

        Use to get hard-codable positions.

        """
        mouse_pos = ctrl.mouse_pos()
        print(f"Absolute mouse pos: {mouse_pos}")
        screen = ui.main_screen().rect
        print(f"Main screen:        {screen}")
        for corner in [
            Corner.TOP_LEFT,
            Corner.TOP_RIGHT,
            Corner.BOTTOM_LEFT,
            Corner.BOTTOM_RIGHT,
        ]:
            corner_pos = Corner.absolute_position(corner)
            relative = (mouse_pos[0] - corner_pos[0], mouse_pos[1] - corner_pos[1])
            print(f"Position relative to {corner}: {relative}")
