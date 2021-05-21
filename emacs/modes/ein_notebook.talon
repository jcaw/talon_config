tag: user.emacs
user.emacs-minor-mode: ein:notebook-mode
-
# [exe]cute
(submit | forrun | cute): user.emacs_command("ein:worksheet-execute-cell-and-goto-next-km")
run (cell | so): user.emacs_command("ein:worksheet-execute-cell")
run all [cells]: user.emacs_command("ein:worksheet-execute-all-cells")
run [cells] above: user.emacs_command("ein:worksheet-execute-all-cells-above")
run [cells] below: user.emacs_command("ein:worksheet-execute-all-cells-above")
clear all cells: user.emacs_command("ein:worksheet-clear-all-output-km")
clear [output | cell]: user.emacs_command("ein:worksheet-clear-output-km")

(new | insert) cell [below]: user.emacs_command("ein:worksheet-insert-cell-below-km")
(new | insert) cell above: user.emacs_command("ein:worksheet-insert-cell-above-km")

fossell: user.emacs_command("ein:worksheet-goto-next-input-km")
bassell: user.emacs_command("ein:worksheet-goto-prev-input-km")
move cell up: user.emacs_command("ein:worksheet-move-cell-up-km")
move cell down: user.emacs_command("ein:worksheet-move-cell-down-km")

killsell: user.emacs_command("ein:worksheet-kill-cell")
(copsell | copy cell): user.emacs_command("ein:worksheet-copy-cell-km")
paste cell [below]: user.emacs_command("ein:worksheet-yank-cell-km")
# Commented out, couldn't find the command to mark cells
# sell cell: user.emacs_command("ein:worksheet-mark-cell")
merge cells: user.emacs_command("ein:worksheet-merge-cell-km")
[change | set] cell type: user.emacs_command("ein:worksheet-change-cell-type-km")
split cell: user.emacs_command("ein:worksheet-split-cell-at-point-km")

disk: user.emacs_command("ein:notebook-save-notebook-command-km")
