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
(new | create | add) {user.blender_create_menu_options}:
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
see through | xray: key(alt-z)
local [mode]: key(/)
remove: key(x)
shade: key(s)
# Expand/reduce selection
(span | spand | expand) [<number>]: key("ctrl-keypad_plus:{number or 1}")
(shrink | reduce) [<number>]: key("ctrl-keypad_minus:{number or 1}")

details:key(n)
scale:key(s)
snap (camera | cam): key(ctrl-alt-keypad_0)

render: key(f12)
render animation: key(ctrl+f12)

(subsurf | subsurface) <number>: key("ctrl-{number}")

expand: key(ctrl-keypad_plus)
(bev | bevel) [<number>]:
    user.blender_bevel_to_segment(number or 0)
(seg | segments) <number>:
    user.blender_set_bevel_segments(number)
(sham | chamfer):
    user.blender_bevel_to_segment(1)


# Addon: Bool Tool
bool | carve: key(ctrl-keypad_minus)
booley | carvley: key(ctrl-shift-keypad_minus)
^slash$: key(ctrl-keypad_divide)
^slashley$: key(ctrl-shift-keypad_divide)


# Addon: MACHIN3 Tools
focus: key(ctrl-f)


# Addon: (Not sure where these ones came from)
cursor: key(shift-s)


# Addon: Cablerator
cable: key(alt-shift-c)


# Addon: MESHmachine
# Basic menu
[mesh] machine: key(y)
fuse: user.blender_meshmachine("f")
change width: user.blender_meshmachine("w")
flatten: user.blender_meshmachine("e")
unfuse: user.blender_meshmachine("d")
re-fuse: user.blender_meshmachine("r")
unchamfer: user.blender_meshmachine("c")
unbevel: user.blender_meshmachine("w")
unfuck: user.blender_meshmachine("x")
turn corner: user.blender_meshmachine("t")
quad corner: user.blender_meshmachine("q")
mark loop: user.blender_meshmachine("l m")
clear loop: user.blender_meshmachine("l c")
(bool | boolean) (clean | cleanup): user.blender_meshmachine("a")
# TODO: Wire in MESHmachin3 chamfer (clashes with basic chamfer command)
#   chamfer: user.blender_meshmachine("h")
offset: user.blender_meshmachine("o")
stash [it]: user.blender_meshmachine("s")
[view] stashes: user.blender_meshmachine("v")
conform: user.blender_meshmachine("m")
flatten normals: user.blender_meshmachine("n f")
straighten normals: user.blender_meshmachine("n s")
transfer normals: user.blender_meshmachine("n t")
clear normals: user.blender_meshmachine("n c")
symmetrize: user.blender_meshmachine("y")
wedge: user.blender_meshmachine("g")
# The smart selection features don't have a route to menu select them via
# keyboard, so I use the shortcut I've set up.
(el | vee | ess) (sell | select): key(alt-t)
# Faster command - although I should probably just use the shortcut for this
# one.
loop: key(alt-t)


# MISC: Experimental Stuff. Ignore.

# TODO: Implement RPC commands for Blender
subdiv | subdivision [surface]: blender(subdivision)
# Individual blender commands can be cross-referenced with python by right
# clicking on them

 # bpy.ops.object.modifier_add(type='SUBSURF')
# blender_bevel_to_segment
