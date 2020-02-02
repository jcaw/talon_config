from talon.voice import Context

context = Context("symbols")


# TODO: Formalise this, use alternatives, extract automatically from basic symbols

additional_symbols = {
    "ellipses": "…",
    "comma and": ", ",
    "arrow": "->",
    "dub arrow": "=>",
    "indirect": "&",
    "dereference": "*",
}


context.keymap(
    {
        # "op dub": " => ",
        # "(op | pad) colon": " : ",
        # "(op equals | assign)": " = ",
        # "op (minus | subtract | sub)": " - ",
        # "op (plus | add)": " + ",
        # "op (times | multiply)": " * ",
        # "op divide": " / ",
        # "op mod": " % ",
        # "[op] (minus | subtract | sub) equals": " -= ",
        # "[op] (plus | add) equals": " += ",
        # "[op] (times | multiply) equals": " *= ",
        # "[op] divide equals": " /= ",
        # "[op] mod equals": " %= ",
        # "(op | is) greater [than]": " > ",
        # "(op | is) less [than]": " < ",
        # "(op | is) equal": " == ",
        # "(op | is) not equal": " != ",
        # "(op | is) greater [than] or equal": " >= ",
        # "(op | is) less [than] or equal": " <= ",
        # "(op (power | exponent) | to the power [of])": " ** ",
        # "(op | logical) and": " && ",
        # "op or": " || ",
        # "[op] (logical | bitwise) and": " & ",
        # "[op] bitwise or": " | ",
        # "[op] logical or": " || ",
        # "(op | logical | bitwise) (ex | exclusive) or": " ^ ",
        # "[(op | logical | bitwise)] (left shift | shift left)": " << ",
        # "[(op | logical | bitwise)] (right shift | shift right)": " >> ",
        # "(op | logical | bitwise) and equals": " &= ",
        # "(op | logical | bitwise) or equals": " |= ",
        # "(op | logical | bitwise) (ex | exclusive) or equals": " ^= ",
        # "[(op | logical | bitwise)] (left shift | shift left) equals": " <<= ",
        # "[(op | logical | bitwise)] (left right ||4 shift right) equals": " >>= ",
    }
)
