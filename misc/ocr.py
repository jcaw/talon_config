from typing import List
import re

import talon
from talon import ui, Module, actions, ctrl
from talon.experimental import ocr

automator_overlay = actions.user.automator_overlay

module = Module()


class OCRError(RuntimeError):
    """Base class for issues finding the text on page"""


class TextNotFoundError(OCRError):
    """Error raised when text isn't found."""


class MultipleCandidatesError(OCRError):
    """Error raised when there are multiple candidates, but a single match is required."""


def filter_results(results: List[ocr.Result], regexp: str) -> List[ocr.Result]:
    results = list(filter(lambda r: re.search(regexp, r.text), results))
    # TODO: Sort top-left first
    return results


def click_candidate(results, button: int, ensure_one_match: bool):
    if ensure_one_match and len(results) > 1:
        raise MultipleCandidatesError(
            "Multiple results. Could not determine a single result to click."
        )
    original_position = ctrl.mouse_pos()
    actions.mouse_move(*results[0].rect.center)
    if button >= 0:
        actions.mouse_click(button=button)
        actions.mouse_move(*original_position)


@module.action_class
class Actions:
    def ocr_everything() -> List[ocr.Result]:
        """Run OCR on everything across all screens."""
        results = []
        for screen in ui.screens():
            screenshot = talon.screen.capture_rect(screen.rect)
            results.extend(ocr.ocr(screenshot))
        return results

    def ocr_window() -> List[ocr.Result]:
        """Run OCR on just the current window."""
        window = ui.active_window()
        screenshot = talon.screen.capture_rect(window.rect)
        return ocr.ocr(screenshot)

    def ocr_find_text_in_window(regexp: str) -> List[ocr.Result]:
        """Find a regexp in the current window with OCR.

        Results are oredered top-left first.

        """
        results = filter_results(actions.self.ocr_window(), regexp)
        if results:
            return results
        else:
            raise TextNotFoundError(
                f'Could not find text in window via OCR: r"{regexp}"'
            )

    def ocr_find_text_anywhere(regexp: str) -> List[ocr.Result]:
        """Find a regexp across all screens with OCR.

        Results are ordered top-left first.

        """
        results = filter_results(actions.self.ocr_everything(), regexp)
        if results:
            return results
        else:
            raise TextNotFoundError(f'Could not find text via OCR: r"{regexp}"')

    def ocr_click_anywhere(regexp: str, button: int = 0, ensure_one_match: bool = True):
        """Click the ocr result matching `regexp`.

        If you want to allow multiple matches, provide `ensure_one_match`.

        """
        with automator_overlay():
            click_candidate(
                actions.self.ocr_find_text_anywhere(regexp), button, ensure_one_match
            )

    def ocr_click_in_window(
        regexp: str, button: int = 0, ensure_one_match: bool = True
    ):
        """Click the ocr result matching `regexp` in the current window.

        If you want to allow multiple matches, provide `ensure_one_match`.

        """
        with automator_overlay():
            click_candidate(
                actions.self.ocr_find_text_in_window(regexp), button, ensure_one_match
            )
