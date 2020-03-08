(track | eye) mouse: user.toggle_eye_mouse()
[eye] zoom mouse: user.toggle_zoom_mouse()
calibrate: user.calibrate_tracker()
debug overlay: user.debug_overlay()
camera overlay: user.camera_overlay()

<user.click>: user.default_click(click)
<user.click> that: user.click_current(click)