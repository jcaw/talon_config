<user.keychord>: key(keychord)

<user.letter>: key(letter)
<user.symbol>: key(symbol)
<user.special>: key(special)

# Standalone arrows are different, to cope with "up" misrecognitions
<user.standalone_arrow>: key(standalone_arrow)

# Use the generic number rule so we can type any spoken number.
#
# Prefix numbers with "num" to avoid ambiguity with repeat rule.
(numb | num) <number>: user.type_number(number)
# Also allow decimals
(numb | num) <number> (point | dot) <digits>:
    user.type_number(number)
    insert(".")
    user.type_number(digits)

# Should be able to specify a series of uppercase letters.
#
# TODO: Audit this
(ship | uppercase) <user.letters> [(lowercase | sunk)]:
    user.uppercase_letters(letters)
