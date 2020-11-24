tag: user.emacs
-
# From region
multi [region]: user.emacs_command("mc/edit-lines")
multi lines: user.emacs_command("mc/edit-lines")
multi home: user.emacs_command("mc/edit-beginnings-of-lines")
multi knock: user.emacs_command("mc/edit-ends-of-lines")

# In region
multi string: user.emacs_command("mc/mark-all-in-region")
multi regex: user.emacs_command("mc/mark-all-in-region-regexp")

# Semantic
multi <number>:
    user.emacs_command("mc/mark-next-like-this")
    # Prefix arg doesn't work here, have to manual repeat
    repeat(number - 1)
multi park: user.emacs_command("mc/mark-pop")
multi all: user.emacs_command("mc/mark-all-dwim")
multi (that | thing): user.emacs_command("TODO")
multi (tag | pair): user.emacs_command("mc/mark-sgml-tag-pair")

# Navigation
multi (down | next | neck): user.emacs_command("mc/mark-next-like-this")
multi (up | last | larse): user.emacs_command("mc/mark-previous-like-this")
