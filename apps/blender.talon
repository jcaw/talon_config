app: /blender/
-
# Jump to view commands
# Isolate single object
isolate | solo:      key(/)
# Radial menu
view:          key(`)
[view] camera: key(keypad_0)
view current:  key(` 3)
view (region | box) | region: key(B)
view all:      key(home)

view front:    key(keypad_1)
view back:     key(` 9)
view top:      key(keypad_7)
view bottom:   key(` 2)
view right [side]: key(keypad_3)
view left [side]:      key(keypad_9)

# Rotating the view in increments
swing left:    key(keypad_4)
swing right:   key(keypad_6)
swing down:    key(keypad_2)
swing up:      key(keypad_8)

# Toggle orthographic projection
orth | ortho | orthographic | persp | perspective: key(keypad_5)

# Free move mode
fly: key(~)


# Unsorted
toolbar: key(t)
properties: key(n)
new | create: key(A)
(new | create) {user.blender_create_menu_options}:
    key(A)
    insert(blender_create_menu_options)
funk | function:key(f3)
move: key(g)
scale: key(s)
rotate: key(r)
# Inconsistent - depends on context
# trackball: key(r r)
joop | duplicate: key(D)
(joop | duplicate) linked: key(alt-d)
hide: key(h)
unhide all: key(alt-h)
hide others: key(H)
faves: key(q)
annotate: key(d)
