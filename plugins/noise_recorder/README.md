# Noise Recorder

Talon script that allows you to record noise data while watching videos on
YouTube, Vimeo, etc. Just drop it somewhere in your Talon `user` folder to use
it (or clone it as a git submodule).

The objective is to rapidly produce enough data to train noise recognition
models as an alternative form of input. Here's an example of something
[similar](https://github.com/chaosparrot/parrot.py) using a different set of
noises (the noises collected by Talon/this script avoid vocalization). Click to
watch:

[![parrot.py author playing Starcraft 2 with eye tracking and noises](https://img.youtube.com/vi/okwLAHQdSVI/maxresdefault.jpg)](https://www.youtube.com/watch?v=okwLAHQdSVI)

## This Script

When you fullscreen a video, it will select a noise and start recording,
prompting you in the top-left corner. Repeatedly make the noise, pausing for
around a second each time (like you would on http://noise.talonvoice.com). The
noise will be recorded with all of your microphones at once to generate as much
data as possible, and saved in `recordings/noises` in your `.talon` folder
(`talon` on Windows). When you exit fullscreen, the recording will stop.

In case you accidentally fullscreen a video, short recordings (less than 4
seconds) are ignored. Long recordings are split into 5-minute increments, so you
can make the noise for as long as you want.

Once you have some data, post on the [Slack](http://talonvoice.slack.com).

## Customisation

Currently works on YouTube, Vimeo and Twitch. Feel free to add more sites like
Netflix - just add them to the `context`.

The script will always record the noise for which you have recorded the least
data. If you would like to avoid specific noises, comment them out directly.

## Caveats

Each microphone may be provided under many sources, so it may be recorded
multiple times. Each source generates its own folder, so for now just
ignore/delete duplicates.

If multiple sources have identical names, only one will be recorded.
