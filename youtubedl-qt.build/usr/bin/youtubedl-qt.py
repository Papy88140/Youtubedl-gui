#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, io, os, re
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QAbstractButton
from PyQt5.QtGui import QIcon, QPixmap
from xdg.BaseDirectory import xdg_config_home
from PyQt5.QtCore import Qt
import configparser

class DropLabel(QLabel):
    def __init__(self, *args, **kwargs):
        QLabel.__init__(self, *args, **kwargs)
        self.path = {}
        self.pixmap = {}
        self.mode = "video"
        self.pixmap["video"] = QPixmap("/usr/share/pixmaps/youtubedl-qt/video.jpg")
        self.pixmap["audio"] = QPixmap("/usr/share/pixmaps/youtubedl-qt/audio.jpg")
        self.pixmap["download"] = QPixmap("/usr/share/pixmaps/youtubedl-qt/download.jpg")
        self.setPixmap(self.pixmap[self.mode])
        self.setAcceptDrops(True)
        self.mouseReleaseEvent = self.changePixmap

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            self.setPixmap(self.pixmap["download"])
            event.acceptProposedAction()

    def dropEvent(self, event):

        text = event.mimeData().text()

        # téléchargement du fichier
        url = text
        folder = self.path[self.mode]

        # contrôle de l'url

        # Youtube

        if url[0:23] == "https://www.youtube.com" and url.find("?v=") > 0 :
            url=url.split("&")[0]

            if self.mode == "video" :
                subprocess.run([os.getenv("HOME")+"/.local/bin/youtube-dl", "-o"+folder+"%(title)s.%(ext)s", url])
            else :
                subprocess.run([os.getenv("HOME")+"/.local/bin/youtube-dl", "-x","--audio-format","mp3","-o"+folder+"%(title)s.%(ext)s", url])

        # Soundcloud

        if url[0:22] == "https://soundcloud.com" and url.split("?")[0].find("/set/") < 0 :
            url=url.split("?")[0]
            if self.mode == "audio" :
                subprocess.run([os.getenv("HOME")+"/.local/bin/youtube-dl", "-x","--audio-format","mp3","-o"+folder+"%(title)s.%(ext)s", url])
            else :
                pass

        self.setPixmap(self.pixmap[self.mode])

        event.acceptProposedAction()

    def changePixmap(self, event):
        # if event.button() == Qt.LeftButton:

        if self.mode == "video":
            self.mode = "audio"
        else :
            self.mode = "video"
        self.setPixmap(self.pixmap[self.mode])

    def printEvent(self,event):
        if event.button() == Qt.LeftButton:
            print("bouton gauche")
        else:
            print("bouton droit")

class App(QWidget):
        def __init__(self):
            super().__init__()
            self.title = 'Youtube-Dl'
            self.initUI()

        def initUI(self):

            config = configparser.RawConfigParser(allow_no_value=True)

            f = open(os.path.join(xdg_config_home, "user-dirs.dirs"))
            user_config = "[XDG_USER_DIR]\n" + f.read()
            f.close()
            user_config = re.sub('\$HOME', os.path.expanduser("~"), user_config)
            user_config = re.sub('"', '', user_config)

            config.readfp(io.StringIO(user_config))

            self.setWindowTitle(self.title)

            # Create widget
            self.label = DropLabel(self)
            self.label.path={}
            self.label.path["audio"] = config.get("XDG_USER_DIR", "XDG_MUSIC_DIR")+"/youtubeDL/"
            self.label.path["video"] = config.get("XDG_USER_DIR", "XDG_VIDEOS_DIR")+"/youtubeDL/"

            self.localbinpath = os.getenv("HOME")+"/.local/bin"

            # verification des dossiers de téléchargement et de youtube-dl

            if not os.path.exists(self.localbinpath):
                os.mkdir(self.localbinpath)
            subprocess.run(["wget","-q","-P",self.localbinpath,"-N","https://yt-dl.org/downloads/latest/youtube-dl"])
            subprocess.run(["chmod","+x",self.localbinpath+"/youtube-dl"])

            if  not os.path.exists(self.label.path["audio"]):
                os.mkdir(self.label.path["audio"])
            if  not os.path.exists(self.label.path["video"]):
                os.mkdir(self.label.path["video"])

            self.setFixedSize(self.label.pixmap[self.label.mode].width(),self.label.pixmap[self.label.mode].height())

            self.setWindowFlags(Qt.WindowStaysOnTopHint)

            self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
