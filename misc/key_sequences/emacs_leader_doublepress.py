"""Allows the leader key in Emacs to be double pressed to revert back to Talon."""

from talon import Module, actions
from user.emacs.utils import voicemacs


module = Module()


fresh_sequence = False


@module.action_class
class Actions:
    def emacs_leader_doublepress_handler(fallback: str = "alt-m"):
        """Acts as the Emacs leader key on first press, Talon leader on second."""
        global fresh_sequence
        try:
            leader_key, last_pressed = voicemacs.rpc_call(
                "voicemacs-leader-key-details"
            )
        except Exception as e:
            print("Could not contact Voicemacs. Defaulting to send the leader.")
            leader_key = fallback
            last_pressed = False
        print(f"Last key was leader key: {last_pressed}")
        # Hacky conversion - doesn't need to be perfect.
        leader_key = (
            leader_key.replace("M", "alt-")
            .replace("C", "ctrl-")
            .replace("S", "win-")
            .replace("--", "-")
        )
        # `fresh_sequence` is used to revert behaviour to the default on a
        # triple press
        if last_pressed and not fresh_sequence:
            # Press again to terminate the sequence
            actions.key(leader_key)
            fresh_sequence = True
            actions.user.key_sequence_start()
        else:
            try:
                actions.user.key_sequence_quit()
            finally:
                actions.key(leader_key)
                fresh_sequence = False
