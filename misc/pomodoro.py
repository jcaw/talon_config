from talon import Module, imgui, cron, actions
import math
import threading
import time
from typing import Optional

module = Module()


lock = threading.Lock()
start_time = None
current_duration = None
pomodoro_type = None
pause_time = None
finished = False
cancel_job = None


# TODO: Better placement
@imgui.open(y=20, x=5)
def gui(gui: imgui.GUI):
    global cancel_job
    if pomodoro_type is not None:
        with lock:
            current_time = pause_time if pause_time else time.monotonic()
            remaining_time = math.ceil(
                (current_duration + start_time - current_time) / 60
            )
            if remaining_time <= 0:
                # Flash effect
                flashes_per_second = 1.5
                suffix = (
                    "FINISHED" if int(time.monotonic() * flashes_per_second) % 2 else ""
                )
                gui.text(f"{pomodoro_type} -- {suffix}")
            else:
                # remaining_time = (current_duration + start_time - current_time) / 60
                gui.text(f"{pomodoro_type} {remaining_time:02d}")


def delete_cancel_cron():
    global cancel_job
    try:
        cron.cancel(cancel_job)
    except:
        pass
    cancel_job = None


def check_pomodoro():
    global sound_job
    with lock:
        if start_time and time.monotonic() > start_time + current_duration:
            # TODO: Play alarm
            delete_cancel_cron()
            finished = True
            # TODO: Cron this?
            for i in range(4):
                # Implementation at time of writing can't play parallel sounds,
                # so this will repeat the ding.
                actions.user.play_bell_high()


@module.action_class
class Actions:
    def pomodoro_start(type_: Optional[str] = "W", time_: Optional[int] = 25 * 60):
        """Start a pomodoro of `type` of length `time`."""
        global start_time, pomodoro_type, pause_time, finished, cancel_job, current_duration

        with lock:
            delete_cancel_cron()
            cancel_job = cron.interval("1s", check_pomodoro)

            start_time = time.monotonic()
            pomodoro_type = type_
            current_duration = time_
            pause_time = None
            finished = False
        gui.show()

    def pomodoro_pause():

        """Pause the active pomodoro."""
        global pause_time
        with lock:
            if not pause_time:
                pause_time = time.monotonic()

    def pomodoro_unpause():

        """Unpause the active pomodoro."""
        global pause_time, current_time
        with lock:
            if pause_time:
                current_time -= pause_time - time.monotonic()
                pause_time = None

    def pomodoro_cancel():
        """Cancel the active pomodoro."""
        global start_time, pomodoro_type, pause_time, current_duration
        with lock:
            delete_cancel_cron()
            if not pomodoro_type:
                raise RuntimeError("No pomodoro running.")
            pomodoro_type = None
            start_time = None
            pause_time = None
            current_duration = None
        gui.hide()
