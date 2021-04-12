app: /discord/
-
# Commands

# Messages are at index 1 - little confusing, add an offset so they're at 0.
[switch] (room | server) <number>: user.discord_switch_server(number + 1)
messages: key(ctrl-1)
