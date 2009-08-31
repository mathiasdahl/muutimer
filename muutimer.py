#!/usr/bin/env python

"""
MuuTimer - Simple kitchen timer using TK for GUI

Copyright (C) 2009 Mathias Dahl

Version: 0.1
Keywords: timer, command line
Author: Mathias Dahl <mathias.dahl@gmail.com>
Maintainer: Mathias Dahl
URL: http://klibb.com/cgi-bin/wiki.pl/MuuTimer

MuuTimer is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

MuuTimer is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with MuuTimer.  If not, see <http://www.gnu.org/licenses/>.

Change history

Date        Sign     Comment
====        ====     =======
2009-08-31  Mathias  Added copyright and history section.
"""

from Tkinter import *
from optparse import OptionParser
from threading import Timer
import time
import os

class MuuTimer:

    def __init__(self, master):

        self.setOptions()
        self.debugStuff()
        self.buildGUI(master)

        self.displayTime()

        if not self.options.no_start:
            self.startTimer()
            self.timerStarted = True
        else:
            self.timerStarted = False

    def debugStuff(self):

        # Debug stuff
        self.debugMessage("Debug enabled")
        self.debugMessage("sound = " + self.soundFile)
        self.debugMessage("time = " + str(self.origtime))

    def buildGUI(self, master):

        # Build GUI
        self.master = master
        self.master.bind('<Destroy>', self.shutDown)

        # Main frame
        self.frame = Frame(master)
        self.frame.pack(fill=BOTH)
        self.frame.master.title("Muu Timer - " + self.action)

        # Action label
        self.action = Label(self.frame, text = self.action)
        self.action.pack(side = TOP, fill=X)

        # Time label
        self.label = Label(self.frame, text = "Time: ")
        self.label.pack(side = LEFT)

        # Time remaining
        self.labelTime = Label(self.frame, width=30)
        self.labelTime.pack(side = LEFT, fill = X)

        # Stop/start button
        self.button = Button(self.frame, text="Start")
        self.button.pack(side = RIGHT)
        self.button.configure(command=self.buttonPushed)
        self.button.bind("<KeyPress>", self.keyPress)
        self.button.focus_set()

    def setOptions(self):

        usage = """usage: %prog [options]

When using the different time options they will all add up so that you
can, for example, set the timer to one hour and fifteen minutes by
using -H 1 and -m 15 at the same time."""

        # Create parser
        parser = OptionParser(usage = usage)

        # Add argument list
        parser.add_option("-s", "--seconds", action="store",      dest="seconds", help="Time in seconds")
        parser.add_option("-m", "--minutes", action="store",      dest="minutes", help="Time in minutes")
        parser.add_option("-H", "--hours",   action="store",      dest="hours",   help="Time in hours")
        parser.add_option("-a", "--action",  action="store",      dest="action",  help="Set the action name")
        parser.add_option("",   "--tick",    action="store_true", dest="tick",    help="Turn tick sound on")
        parser.add_option("",   "--no-finish-sound",  action="store_true", dest="no_finish_sound",    help="Turn finish sound off")
        parser.add_option("",   "--no-start",  action="store_true", dest="no_start",    help="Turn auto start off")
        parser.add_option("",   "--time-in-title",  action="store_true", dest="time_in_title",    help="Display time in the window title")
        parser.add_option("",   "--sound",   action="store",      dest="sound",   help="Sound file to play when time reaches zero. Must be a 16 bit WAV file")
        parser.add_option("-d", "--debug",   action="store_true", dest="debug",   help="Enable debug output")

        # Parse
        (self.options, args) = parser.parse_args()

        # Check options
        if not self.options.sound:
            self.soundFile = "uh_oh2.wav"
        else:
            self.soundFile = self.options.sound

        if not self.options.seconds:
            self.origtime = 0
        else:
            self.origtime = int(self.options.seconds)

        if self.options.minutes:
            self.origtime = self.origtime + int(self.options.minutes) * 60

        if self.options.hours:
            self.origtime = self.origtime + int(self.options.hours) * 3600

        if self.origtime == 0:
            self.origtime = 5 * 60

        if not self.options.action:
            self.action = "Some action"
        else:
            self.action = self.options.action

        self.time = self.origtime

    def formatTime(self, seconds):
        return time.ctime(3600 * 23 + seconds)[11:19]

    def startTimer(self):
        self.timer  = Timer(1, self.updateTime)
        self.timer.start()
        self.button.configure(text = "Stop")

    def shutDown(self, detail):
        self.timer.cancel()

    def updateTime(self):

        self.time = self.time - 1
        self.displayTime()

        if self.time > 0:
            self.startTimer()
            self.playTickSound()
        else:
            self.playFinishSound()
            self.button.configure(text = "Start")
            self.timer.cancel()
            self.time = self.origtime
            self.timerStarted = False

    def playSound(self):
        os.system("aplay " + self.soundFile)

    def playFinishSound(self):
        if not self.options.no_finish_sound:
            self.playSound2(self.soundFile)

    def playTickSound(self):
        if self.options.tick:
            self.playSound2("tick.wav")

    def playSound2(self, file):

        # Thanks to Bill Dandreta:
        # http://mail.python.org/pipermail/python-list/2004-October/288905.html

        if sys.platform.startswith('win'):
            from winsound import PlaySound, SND_FILENAME, SND_ASYNC
            PlaySound(file, SND_FILENAME|SND_ASYNC)
        elif sys.platform.find('linux')>-1:
            from wave import open as waveOpen
            from ossaudiodev import open as ossOpen
            s = waveOpen(file,'rb')
            (nc,sw,fr,nf,comptype, compname) = s.getparams( )
            dsp = ossOpen('/dev/dsp','w')

            try:
                from ossaudiodev import AFMT_S16_NE
            except ImportError:
                if byteorder == "little":
                    AFMT_S16_NE = ossaudiodev.AFMT_S16_LE
                else:
                    AFMT_S16_NE = ossaudiodev.AFMT_S16_BE

            dsp.setparameters(AFMT_S16_NE, nc, fr)
            data = s.readframes(nf)
            s.close()
            dsp.write(data)
            dsp.close()

    def displayTime(self):
        theTime = self.formatTime(self.time)
        self.labelTime.configure(text = theTime)
        if self.options.time_in_title:
            self.frame.master.title(theTime)
        
    def buttonPushed(self):

        if self.timerStarted:
            self.timer.cancel()
            self.timerStarted = False
            self.button.configure(text = "Start")
        else:
            self.timerStarted = True
            self.button.configure(text = "Stop")
            self.startTimer()
            self.displayTime()

    def keyPress(self, event):

        if event.keysym == "Escape":
            self.master.destroy()
            self.timer.cancel()

    def debugMessage(self, message):
        if self.options.debug:
            print message

root = Tk()
muutimer = MuuTimer(root)
root.mainloop()
