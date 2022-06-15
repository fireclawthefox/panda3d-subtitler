# Panda3D Subtitler
A subtitle reader/renderer for the Panda3D game engine

## Features
This library extends the game engine by a simple subtitle reader/renderer. You just open an existing subtitle file, sync it to the audio or video and you'll have subtitles in your panda3d application.

Currently this library only supports SubRip subtitle (.srt) files.

## Install
Install the subtitler via pip

```bash
pip install panda3d-subtitler
```

## How to use
To add a browser instance to your running Panda3D application, just instantiate it like shown here:
```python3
from subtitler.subtitler import Subtitler

mySound = loader.loadSfx("someAudioFile.ogg")

subtitles = Subtitler("subtitles")
subtitles.loadSubtitleFile("./mySubtitles.srt")
subtitles.synchronizeToAudio(mySound)
```
