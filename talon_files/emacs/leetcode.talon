tag: emacs
-
# Note Emacs Leetcode won't work directly on windows. It requires running Emacs
# under Windows Subsystem for Linux, + some hacking
(new | start) leetcode: user.emacs_command("leetcode")

# These would be bound to leetcode exclusively, but detecting an open leetcode
# session is difficult.
(leetcode | leet) try: user.emacs_command("leetcode-try")
(leetcode | leet) submit: user.emacs_command("leetcode-submit")
(leetcode | leet) refresh: user.emacs_command("leetcode-refresh")
(leetcode | leet) show [current] problem: user.emacs_command("leetcode-show-current-problem")
