# Emacs Utils

These are universal utilities for Emacs. Most of the code here is used to wire into Emacs and invoke RPC calls, as well as pass information to/from Talon and expose that information in a way that's useful.

## Overview

I open a persistent socket connection to Emacs, then Emacs and Talon can both invoke the passing of information. This allows me to call Emacs commands (and functions) via RPC, ask for information from Emacs, and send state updates to Talon so I can change Talon's behaviour based on Emacs' state. Scan through the scripts to see what functionality exists.

## Bugs

The Voicemacs socket connection is sometimes buggy - this is likely because sockets in Emacs are janky in general, but there could be another cause. Occasionally, if Talon or the Emacs server is restarted, the old Voicemacs connection can hang, and Talon won't be able to connect. I just restart both Talon and Emacs when that happens.

I don't plan to fix this soon. Talon should eventually get a formal RPC protocol, at which point I'll rewrite the whole thing from scratch.

## Emacs Requirements

[Voicemacs](https://github.com/jcaw/voicemacs) is the Emacs-side package - it needs to be installed for the Voicemacs-dependent functionality to work.

My personal config is heavily built on Voicemacs, so functionality is very limited without it.
