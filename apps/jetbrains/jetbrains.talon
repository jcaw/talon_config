# Requires https://plugins.jetbrains.com/plugin/10504-voice-code-idea
app: jetbrains
-
recent:      user.idea("action FindRecentFiles")
format code: user.idea("action ReformatCode")
scrape:      user.idea("action GotoAction")
refack:      user.idea("action Refactorings.QuickListPopupAction")

pop def:     user.idea("action QuickImplementations")
pop type:    user.idea("action ExpressionTypeInfo")
pop params:  user.idea("action ParameterInfo")

breakpoints: user.idea("action ViewBreakpoints")

# TODO: Run project
run (prog | program): user.idea("action RunProject")
run menu:    user.idea("action ChooseRunConfiguration")
# TODO: Build/rebuild
compile:     user.idea("action Build")
recompile:   user.idea("action ReBuild")
run test:    user.idea("action RunClass")
rerun:       user.idea("action Rerun")
resume:      user.idea("action Resume")

ferror:      user.idea("action GotoNextError")
berror:      user.idea("action GotoPreviousError")
