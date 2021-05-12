<user.keychord>: key(keychord)

# TODO: Maybe convert all these over to `insertable`?
<user.letter>: key(letter)
<user.symbol>: key(symbol)
<user.special>: key(special)

pad <user.insertable>: user.insert_key_padded(insertable)

# Standalone arrows are different, to cope with "up" misrecognitions
<user.standalone_arrow>: key(standalone_arrow)

# Use the generic number rule so we can type any spoken number.
#
# Prefix numbers with "num" to avoid ambiguity with repeat rule.
(numb | num | number) <number>: user.type_number(number)
# Also allow decimals
(numb | num | number) <number> (point | dot) <digits>:
    user.type_number(number)
    insert(".")
    user.type_number(digits)

# "sky" for a series of uppercase letters. Terminate and go back to lowercase
# with "sunk".
sky <user.letters> [sunk]: user.insert_uppercase(letters)


# TODO: Remove these once I've broken the old habits
harp:
    user.play_thunk()
    app.notify("It's \"hip\" now.", "Don't say \"harp\"")
    # key(space)
batch:
    user.play_thunk()
    app.notify("It's \"bat\" again now.", "Don't say \"batch\"")
    # key(space)
batch:
    user.play_thunk()
    app.notify("It's \"zip\" again now.", "Don't say \"zen\"")
    # key(space)
