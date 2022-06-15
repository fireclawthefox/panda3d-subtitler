from panda3d.core import TextNode, AudioSound
from datetime import datetime
from subtitler.srtSubtitleReader import SRTSubtitle, helper_ConvertTime, helper_ConvertTimeDouble
import logging

class Subtitler(TextNode):
    def __init__(self, name):
        TextNode.__init__(self, name)
        self.sub = SRTSubtitle()
        self.audio = None
        self.video = None
        self.cur_index = -1

        self.node_path = aspect2d.attachNewNode(self)
        self.node_path.setScale(0.07)
        self.node_path.setPos(0, 0, -0.83)
        self.setShadow(0.05, 0.05)
        self.setShadowColor(0, 0, 0, 1)
        self.setAlign(TextNode.ACenter)

        self.node_path.hide()

    def loadSubtitleFile(self, filename):
        self.sub.open(filename)

    def synchronizeToAudio(self, audio):
        """Use this to synchronize the subtitle with the (videos) audio"""
        self.audio = audio

        taskMgr.add(self.subtitleTask, "subtitle {} Task".format(self.name))

    def synchronizeToVideo(self, video):
        """Use this to synchronize the subtitle with the video,
        only use this if you play video files without audio synchronisation!"""
        self.video = video

        taskMgr.add(self.subtitleTask, "subtitle {} Task".format(self.name))

    def stop(self):
        taskMgr.remove("subtitle Task")

    def subtitleTask(self, task):
        cur_t = None
        if self.audio is not None:
            if self.audio.status() != AudioSound.PLAYING: return task.cont
            loops = self.audio.getLoopCount() if self.audio.getLoopCount() > 1 else 1
            cur_t = helper_ConvertTimeDouble(self.audio.getTime() / loops)
        elif self.video is not None:
            if not self.video.isPlaying(): return task.cont
            loops = self.video.getLoopCount() if self.video.getLoopCount() > 1 else 1
            cur_t = helper_ConvertTimeDouble(self.video.getTime() / loops)
        else:
            # we do not have a sync with audio or video
            logging.error("No audio or video was synchronized with this subtitles")
            return task.done
        if cur_t is None: return task.cont

        if self.cur_index == -1:
            self.cur_index = self.sub.getSubtitleIndex(cur_t=cur_t)

        end_t = self.sub.getSubtitleEndT(self.cur_index)
        if end_t is not None:
            if cur_t >= end_t:
                self.setText("")
                self.node_path.hide()

        new_text = self.sub.getSubtitleText(cur_t=cur_t)
        if new_text is not None:
            self.cur_index = self.sub.getSubtitleIndex(cur_t=cur_t)
            self.setText(new_text)
            self.node_path.show()

        return task.cont

