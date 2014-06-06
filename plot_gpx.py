#!/usr/bin/env python
# Licence: GPLv2.0

import sys, os, math
import xml.etree.cElementTree as ET
import string

import pygtk
pygtk.require("2.0")

import matplotlib
matplotlib.use('GTK')

import gtk
import gtk.glade

from matplotlib.figure import *
from matplotlib.axes import *
from matplotlib.backends.backend_gtk import *
from pylab import *

def get_highest_speed(et):
    mainNS=string.Template("{http://www.topografix.com/GPX/1/0}$tag")

    wptTag=mainNS.substitute(tag="trkpt")
    nameTag=mainNS.substitute(tag="speed")
    highest_speed = 0
    for wpt in et.findall("//"+wptTag):
        spd = float(wpt.findtext(nameTag))
        if spd > highest_speed:
            highest_speed = spd
    return highest_speed

def collect_info(gpx_filename):
    cmin = 0
    mainNS=string.Template("{http://www.topografix.com/GPX/1/0}$tag")
    wptTag=mainNS.substitute(tag="trkpt")
    speedTag=mainNS.substitute(tag="speed")
    timeTag=mainNS.substitute(tag="time")
    et=ET.parse(open(gpx_filename))
    highest_speed = get_highest_speed(et)
    wptinfo = []
    for wpt in et.findall("//"+wptTag):
        wptinfo.append(float(wpt.findtext(speedTag)) * 3.5)
    return wptinfo

def movavg(s, n):
    """
    returns an n period moving average for the time series s
       
    s is a list ordered from oldest (index 0) to most recent (index -1)
    n is an integer

        returns a numeric array of the moving average

    See also ema in this module for the exponential moving average.
    """
    s = array(s)
    c = cumsum(s)
    return (c[n-1:] - c[:-n+1]) / float(n-1)

class app:
    target = ""
    def __init__(self):
        self.init_app()

    def init_app(self):
        gladefile = "speed_graph.glade"
        windowname = "win"
        self.wTree = gtk.glade.XML (gladefile,windowname)
        dic = { "on_btn_draw_clicked" : self.draw }
        self.wTree.signal_autoconnect(dic)

        self.figure = Figure(figsize=(5,4), dpi=70)
        self.axis = self.figure.add_subplot(111)

        self.axis.set_xlabel('Waypoint')
        self.axis.set_ylabel('Speed')
        self.axis.set_title('Driving Speed')
        self.axis.grid(False)

        self.canvas = FigureCanvasGTK(self.figure)
        self.canvas.show()
        self.graphview = self.wTree.get_widget("vbox")
        self.graphview.pack_start(self.canvas, True, True)  

    def draw(self, widget):
        while True:
            try:
                gpx_filename = self.wTree.get_widget("filechooserbutton1").get_filename()                    
                data = collect_info(gpx_filename)
                ma20 = movavg(data, 50)
                self.axis.plot(data, 'bo')
                vind = array([i for i, o in enumerate(data) if o!=-1])
                self.axis.plot(vind[50-1:], ma20, 'r', linewidth=2)
                
                #self.axis.legend((ga[0], gb[0]), ("A", "B"), shadow = True)
                #self.axis.set_xlim(-width,len(ind))

                self.canvas.destroy()
                self.canvas = FigureCanvasGTK(self.figure)
                self.canvas.show()
                self.grahview = self.wTree.get_widget("vbox")
                self.grahview.pack_start(self.canvas, True, True)
                break

            except ValueError:
                print "Error: ", ValueError
                break
        return

app = app()
gtk.main()
