tag: user.emacs
user.emacs-major-mode: magit-status-mode
-
mark <number>: user.magit_mark_lines(number)
stage <number>:
    user.magit_mark_lines(number)
    user.emacs_command("magit-stage")
unstage <number>:
    user.magit_mark_lines(number)
    user.emacs_command("magit-unstage")


# Staging
stage [that|thing]: user.emacs_command("magit-stage")
stage all: user.emacs_command("magit-stage-modified")
unstage [that|thing]: user.emacs_command("magit-unstage")
unstage all: user.emacs_command("magit-unstage-all")

# Committing
commit: user.emacs_command("magit-commit-create")
extend [commit]: user.emacs_command("magit-commit-extend")
reword [commit]: user.emacs_command("magit-commit-amend")

# Pushing
push remote:
    user.emacs_command("magit-push-current-to-pushremote")
    user.play_bell_high()
force push remote:
    user.emacs_command("magit-push")
    # Ideally this should be RPC but within the command these are unlikely to be
    # rebound
    key(- F p)
    user.play_bell_high()
push upstream:
    user.emacs_command("magit-push-current-to-upstream")
    user.play_bell_high()
push elsewhere:
    user.emacs_command("magit-push-current")
    user.play_bell_high()

# Pulling
pull remote: user.emacs_command("magit-pull-from-pushremote")
pull upstream: user.emacs_command("magit-pull-from-upstream")
pull elsewhere: user.emacs_command("magit-pull-branch")

# Fetching
fetch remote: user.emacs_command("magit-fetch-from-pushremote")
fetch upstream: user.emacs_command("magit-fetch-from-upstream")
fetch elsewhere: user.emacs_command("magit-fetch-other")
fetch all remotes: user.emacs_command("magit-fetch-all")

# Remoting
add remote: user.emacs_command("magit-remote-add")

# Branching
checkout: user.emacs_command("magit-checkout")
switch branch: user.emacs_command("magit-checkout")
checkout (local | branch): user.emacs_command("magit-branch-checkout")
create branch: user.emacs_command("magit-branch-and-checkout")

# Merging
merge branch: user.emacs_command("magit-merge-plain")

# Stashing
stash (all | changes | that | thing): user.emacs_command("magit-stash-both")

# Resetting
reset hard: user.emacs_command("magit-reset-hard")
reset soft: user.emacs_command("magit-reset-soft")
reset mixed: user.emacs_command("magit-reset-mixed")

# Submenus
help: user.emacs_command("magit-dispatch")

# Unsorted
refresh: user.emacs_command("magit-refresh")
toggle: user.emacs_command("magit-section-toggle")
mark: user.emacs_command("set-mark-command")
apply: user.emacs_command("magit-apply")
reverse: user.emacs_command("magit-reverse")
discard: user.emacs_command("magit-discard")
cherry pick: user.emacs_command("magit-cherry-pick")
(new | create) tag: user.emacs_command("magit-tag-create")
tag release: user.emacs_command("magit-tag-release")
(show | list) stashes: user.emacs_command("magit-stash-list")


# Submenus (popups)
cherries: user.emacs_command("magit-cherry")
branching: user.emacs_command("magit-branch")
bisecting: user.emacs_command("magit-bisect")
committing: user.emacs_command("magit-commit")
[show] diff [that|thing]: user.emacs_command("magit-diff-dwim")
diffing: user.emacs_command("magit-diff")
# TODO: Audit
diff settings: user.emacs_command("magit-diff-refresh")
ediff [that|thing]: user.emacs_command("magit-ediff-dwim")
ediffing: user.emacs_command("magit-ediff")
fetching: user.emacs_command("magit-fetch")
pulling: user.emacs_command("magit-pull")
logging: user.emacs_command("magit-log")
# TODO: Audit
log settings: user.emacs_command("magit-log-refresh")
merging: user.emacs_command("magit-merge")
remoting: user.emacs_command("magit-remote")
submodules: user.emacs_command("magit-submodule")
subtrees: user.emacs_command("magit-subtree")
pushing: user.emacs_command("magit-push")
rebasing: user.emacs_command("magit-rebase")
tagging: user.emacs_command("magit-tag")
notes: user.emacs_command("magit-notes")
reverting: user.emacs_command("magit-revert")
apply patches: user.emacs_command("magit-am")
format patches: user.emacs_command("magit-patch")
resetting: user.emacs_command("magit-reset")
[show] (refs | references): user.emacs_command("magit-show-refs")
stashing: user.emacs_command("magit-stash")
run command: user.emacs_command("magit-run")
worktree: user.emacs_command("magit-worktree")
