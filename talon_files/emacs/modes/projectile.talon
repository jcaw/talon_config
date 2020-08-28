tag: emacs
user.emacs-minor-mode: projectile-mode
-
(switch | open) (proj | project): user.emacs_command("projectile-switch-project")
(proj | project) (files | dired): user.emacs_command("projectile-dired")
save (proj project): user.emacs_command("projectile-save-project-buffers")

(proj | project) replace: user.emacs_command("projectile-replace")
# TODO: Projectile search?
# (proj | project) search: user.emacs_command("helm-projectile-rg")
(proj | project) command: user.emacs_command("projectile-run-command in root")
(proj | project) shell: user.emacs_command("projectile-run-async-shell-command-in-root")
# TODO: Maybe remove this?
(proj | project) (tasks | to dooz): user.emacs_command("magit-todos-list")

# (proj | project) run: user.emacs_command("projectile-run-project")
run (proj | project): user.emacs_command("projectile-run-project")
# (proj | project) test: user.emacs_command("projectile-test-project")
test (proj | project): user.emacs_command("projectile-test-project")
# (proj | project) compile: user.emacs_command("projectile-compile-project")
compile (proj | project): user.emacs_command("projectile-compile-project")
(proj | project) repeat: user.emacs_command("projectile-repeat-last-command")

[proj | project] durr locals: user.emacs_command("projectile-edit-dir-locals")
(proj | project) (config | settings): user.emacs_command("projectile-configure-project")
