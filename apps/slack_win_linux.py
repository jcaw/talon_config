from talon import Context, actions
ctx = Context()
ctx.matches = r"""
os: windows
os: linux
app: /slack/
"""

@ctx.action_class('user')
class UserActions:
    def slack_messages() -> None:          actions.key('ctrl-shift-k')
    def slack_threads() -> None:           actions.key('ctrl-shift-t')
    def slack_history() -> None:           actions.key('TODO')
    def slack_forward():                   actions.key('TODO')
    def slack_activity() -> None:          actions.key('ctrl-shift-m')
    def slack_directory() -> None:         actions.key('ctrl-shift-e')
    def slack_starred_items() -> None:     actions.key('ctrl-shift-s')
    def slack_unread():                    actions.key('TODO maybe ctrl-j')
    
    def next_unread_channel() -> None:     actions.key('alt-shift-down')
    def previous_unread_channel() -> None: actions.key('alt-shift-up')
    
    def slack_attach_snippet():            actions.key('ctrl-shift-enter')
    
    def fullscreen():                      actions.key('ctrl-shift-f')
    
    # TODO: Extract
    def edit_last_message() -> None:       actions.key('ctrl-up')
    def toggle_bullets():                  actions.key('ctrl-shift-8')
    def toggle_number_list():              actions.key('ctrl-shift-7')
    def toggle_quote():                    actions.key('ctrl-shift->')
    def upload_file():                     actions.key('ctrl-u')
    def list_app_shortcuts():              actions.key('ctrl-/')
    def toggle_bold():                     actions.key('ctrl-b')
    def toggle_italic():                   actions.key('ctrl-i')
    def toggle_strikethrough():            actions.key('ctrl-shift-x')

@ctx.action_class('edit')
class EditActions:
    def search(): actions.key('ctrl-j')
