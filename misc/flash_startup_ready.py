from talon import app, actions


def notify_talon_is_ready():
    # Notification, sticks around a while. Annoying.
    app.notify("Talon Ready", "Talon is ready to use.")

    # Alternate approach - flash screen.
    # with actions.user.automator_overlay("Talon Ready"):
    #     actions.sleep("300ms")


app.register("launch", notify_talon_is_ready)
