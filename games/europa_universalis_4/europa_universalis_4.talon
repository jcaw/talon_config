app: /eu4/
-
# Move the map by hissing. Move the mouse to the edge of the screen, don't use
# keys, because keys don't register reliably.
tag(): user.hiss_edge_map_move

# Camera Zoom
near: user.eu4_set_zoom(1)
middle: user.eu4_set_zoom(3)
further: user.eu4_set_zoom(6)
(zoom | level) <number>: user.eu4_set_zoom(number)
zoom in [<number>]: user.eu4_zoom_in(number or 1)
zoom out [<number>]: user.eu4_zoom_out(number or 1)

# Global Shortcuts
#
# Zoom to home country
go home: key(backspace)
# Guard pause with "and" to stop it firing off too easily.
and pause: key(space)
(close | kill) (all | menus): user.eu4_close_menus()
map <number>: user.eu4_switch_map(number)
speed <number>: user.eu4_set_game_speed(number)
(notification | notey) <number>: user.eu4_hover_notification(number)
<user.eu4_hoverable>: user.corner_hover(eu4_hoverable)
<user.eu4_clickable>: user.corner_click(eu4_clickable)

# Control Groups
set group <number>: user.assign_control_right(number)
group <number>: user.select_control_group(number)
(go | jump) [to] group <number>: user.go_to_control_group(number)
move group <number>: user.move_control_group(number)

# Responses to menus
#
# Confirming
(accept | confirm | OK | maintain diplomat): key(c)
# Declining
(decline | cancel | go to | recall diplomat): key(z)

# Misc shortcuts - most of these are contextual, but we can't evaluate context
# so they're enabled globally.
merge: key(g)
attach: key(a)
create [[new] unit]: key(b)
# TODO: Test & fix these.
unit: key(u)
siege: key(j)

jump {user.eu4_locations}: user.eu4_jump_to_location(eu4_locations)

# TODO: Extract to generic steam context.
overlay: key(shift-tab)


# Named maps
(terrain | train) map:      user.eu4_switch_map(1)
(political | poly) map:     user.eu4_switch_map(2)
trade map:                  user.eu4_switch_map(3)
(religion | religious) map: user.eu4_switch_map(4)
(diplomatic | diplo) map:   user.eu4_switch_map(5)
(areas | regions) map:      user.eu4_switch_map(6)
tech map:                   user.eu4_switch_map(7)
(opinion | relations) map:  user.eu4_switch_map(8)
culture map:                user.eu4_switch_map(9)
(development | devel) map:  user.eu4_switch_map(10)


# Menus
#
# Country Menus
country [view]:                                    user.eu4_open_menu("f1")
court:                                             user.eu4_open_menu("f1 1")
government:                                        user.eu4_open_menu("f1 2")
(diplomacy | diplo):                               user.eu4_open_menu("f1 3")
(economy | econ):                                  user.eu4_open_menu("f1 4")
trade:                                             user.eu4_open_menu("f1 5")
(technology | tech) [western]:                     user.eu4_open_menu("f1 6")
ideas:                                             user.eu4_open_menu("f1 7")
missions:                                          user.eu4_open_menu("f1 8")
(decisions | policies | decisions and policies):   user.eu4_open_menu("f1 9")
(stability | expansion | stability and expansion): user.eu4_open_menu("f1 0")
religion:                                          user.eu4_open_menu("f1 ")
(military | mill):                                 user.eu4_open_menu("f1 .")
subjects:                                          user.eu4_open_menu("f1 '")
estates:                                           user.eu4_open_menu("f1 k")
# Production Menus
(production | prod) [interface]: user.eu4_open_menu("b")
land [units]:                    user.eu4_open_menu("b 1")
naval [units]:                   user.eu4_open_menu("b 2")
coring:                          user.eu4_open_menu("b 3")
missionaries:                    user.eu4_open_menu("b 4")
[local] autonomy:                user.eu4_open_menu("b 5")
culture:                         user.eu4_open_menu("b 6")
buildings:                       user.eu4_open_menu("b 7")
(development | devel):           user.eu4_open_menu("b 8")
# TODO: Better solution to the two estates commands
(production | prod) estates:     user.eu4_open_menu("b 9")
# Ledger Menus
# TODO: Will this conflict?
ledger:                             user.eu4_open_menu("l")
country ledger:                     user.eu4_open_menu("l f1")
# TODO: What's on f2? Colonization?
(military | mill) ledger:           user.eu4_open_menu("l f3")
(economic | economy | econ) ledger: user.eu4_open_menu("l f4")
trade ledger:                       user.eu4_open_menu("l f5")
relations ledger:                   user.eu4_open_menu("l f6")
# Other Menus
find: user.eu4_open_menu("f")
