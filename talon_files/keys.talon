<user.newapi.keys.keychord>: key(keychord)

<user.newapi.keys.letter>: key(letter)
<user.newapi.keys.symbol>: key(symbol)
<user.newapi.keys.special>: key(special)

# Standalone arrows are different, to cope with "up" misrecognitions
<user.newapi.keys.standalone_arrow>: key(standalone_arrow)

# Use the generic number rule so we can type any spoken number.
#
# Prefix numbers with "num" to avoid ambiguity with repeat rule.
numb <number>: user.newapi.keys.press_number(number)

# Should be able to specify a series of uppercase letters.
#
# TODO: Audit this
(ship | uppercase) <user.newapi.keys.letters> [(lowercase | sunk)]:
    user.newapi.keys.uppercase_letters(letters)
