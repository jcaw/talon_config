(track | eye) mouse: user.newapi.mouse.toggle_eye_mouse()
[eye] zoom mouse: user.newapi.mouse.toggle_zoom_mouse()
calibrate: user.newapi.mouse.calibrate_tracker()
debug overlay: user.newapi.mouse.debug_overlay()
camera overlay: user.newapi.mouse.camera_overlay()

<user.newapi.mouse.click>: user.newapi.mouse.default_click(click)
<user.newapi.mouse.click> that: user.newapi.mouse.click_current(click)