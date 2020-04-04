app: /emacs/
-
[find] command name: user.emacs_command("describe-key-briefly")
describe key: user.emacs_describe_key()
# Change this to describe command?
describe function: user.emacs_describe_function()
describe command: user.emacs_describe_command()
describe variable: user.emacs_describe_variable()
describe (mode | modes): user.emacs_command("describe-mode")
describe macro: user.emacs_command("helpful-macro")
describe bindings: user.emacs_command("describe-bindings")
# TODO: Inline phrase
(apropos | describe symbol): user.emacs_apropos()
describe that: user.emacs_describe_thing_at_point()
