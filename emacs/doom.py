from talon import Context, actions

emacs_command = actions.user.emacs_command


context = Context()
context.matches = r"""
tag: user.emacs
user.emacs-is-doom: True
"""


@context.action_class("self")
class DoomActions:
    def search(text: str = None):
        emacs_command("+default/search-project")

    def emacs_restart():
        emacs_command("doom/restart-and-restore")

    def emacs_quit():
        emacs_command("save-buffers-kill-terminal")

    def go_back():
        emacs_command("better-jumper-jump-backward")

    def go_forward():
        emacs_command("better-jumper-jump-forward")

    def find_definition():
        emacs_command("+lookup/definition")

    def find_definition_other_window():
        emacs_command("+lookup/definition-other-window")

    def find_references():
        emacs_command("+lookup/references")

    def find_references_other_window():
        emacs_command("+lookup/references-other-window")

    def find_implementations():
        emacs_command("+lookup/implementations")

    def find_implementations_other_window():
        emacs_command("+lookup/implementations-other-window")

    def show_documentation():
        emacs_command("+lookup/documentation")

    def emacs_toggle_fold():
        emacs_command("+fold/toggle")

    def emacs_fold():
        emacs_command("+fold/close")

    def emacs_unfold():
        emacs_command("+fold/open")

    def emacs_fold_all():
        emacs_command("+fold/close-all")

    def emacs_unfold_all():
        emacs_command("+fold/open-all")

    def emacs_previous_fold():
        emacs_command("+fold/previous")

    def emacs_next_fold():
        emacs_command("+fold/next")
