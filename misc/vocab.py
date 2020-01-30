"""Pieces of vocabulary that are common across commands.

Certain words might have common contractions, alternatives, etc. Some of this
is going to be stored within configs, but global stuff goes here.

"""

## Generic words

# Dragon is bad at recognizing "xt" (as a suffix).
NEXT = "(next | neck)"
# Dragon seems to have trouble with the "st" suffix too.
PREVIOUS = "(last | larse | previous | preev)"


## Words related to videos

VIDEO = "(vid | video)"
SUBTITLES = "(captions | subtitles | subs)"
