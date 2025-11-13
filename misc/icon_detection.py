"""Icon detection utilities for finding and clicking UI elements using image recognition."""

from typing import Optional, Tuple
from talon import Module, actions, ui, screen
from talon.experimental import locate


module = Module()


@module.action_class
class IconDetectionActions:
    def find_icon_in_window(icon_path: str, threshold: float = 0.90) -> Optional[Tuple[int, int]]:
        """Find an icon in the current window using image recognition.

        Args:
            icon_path: Path to the icon image to search for
            threshold: Match threshold (0.0-1.0), default 0.90

        Returns the screen coordinates (x, y) of the icon if found, None otherwise.
        """
        window = ui.active_window()
        screenshot = screen.capture_rect(window.rect)
        result = locate.locate_in_image(icon_path, screenshot, threshold=threshold)
        if result:
            # Translate coordinates from screenshot to screen space
            return (window.rect.x + result.x, window.rect.y + result.y)
        return None

    def click_icon_in_window(icon_path: str, threshold: float = 0.90, button: int = 0) -> bool:
        """Find and click an icon in the current window using image recognition.

        Args:
            icon_path: Path to the icon image to search for
            threshold: Match threshold (0.0-1.0), default 0.90
            button: Mouse button to click (0=left, 1=right, 2=middle)

        Returns True if icon was found and clicked, False otherwise.
        """
        coords = actions.user.find_icon_in_window(icon_path, threshold)
        if coords:
            actions.mouse_move(*coords)
            actions.sleep("100ms")
            actions.mouse_click(button)
            return True
        return False
