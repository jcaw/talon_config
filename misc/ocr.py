from typing import List
import re

import talon
from talon import ui, Module, actions
from talon.experimental import ocr


module = Module()


def filter_results(results: List[ocr.Result], regexp: str) -> List[ocr.Result]:
    results = list(filter(lambda r: re.search(regexp, r.text), results))
    # TODO: Sort top-left first
    return results


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
        return filter_results(actions.self.ocr_window(), regexp)

    def ocr_find_text_anywhere(regexp: str) -> List[ocr.Result]:
        """Find a regexp across all screens with OCR.

        Results are ordered top-left first.

        """
        return filter_results(actions.self.ocr_everything(), regexp)
