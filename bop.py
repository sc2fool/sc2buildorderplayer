#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Build Order Player - BOP

A simple GUI to sync a build order with in game time.

"""
import sys
import glob
import os

import cairo
import requests
from requests.exceptions import ConnectionError

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Notify', '0.7')
from gi.repository import GLib
from gi.repository import Gio
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import Notify


UI_URL = "http://localhost:6119/ui"
GAMETIME_URL = "http://localhost:6119/game/displayTime"


class BuildOrderItem(Gtk.ListBoxRow):
    def __init__(self, data):
        super(Gtk.ListBoxRow, self).__init__()
        self.data = data
        self.add(Gtk.Label(label=data, xalign=0))


class BOPMainWindow(Gtk.Window):
    def __init__(self, app):
        Gtk.Window.__init__(self, title="SC2 Build Order Player", application=app)
        Notify.init("bop")

        self.set_default_size(600, 200)
        self.set_border_width(10)
        self.set_position(Gtk.WindowPosition.CENTER)

        box_outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(box_outer)

        topbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box_outer.pack_start(topbox, False, True, 0)

        filecombo = Gtk.ComboBoxText.new()
        self.selected_buildorder = None
        self.path = os.path.abspath(app.buildorders_path)
        for filename in glob.glob(os.path.join(self.path, "*.txt")):
            filename = os.path.basename(filename)
            if not self.selected_buildorder:
                self.selected_buildorder = filename
            filecombo.append_text(filename)
        filecombo.set_active(0)
        filecombo.connect("changed", self.filecombo_changed)
        topbox.pack_start(filecombo, True, True, 0)

        resetbutton = Gtk.Button(label="Reset", expand=False)
        resetbutton.connect("button-press-event", self.resetbutton_clicked)
        topbox.pack_start(resetbutton, True, True, 10)

        timelabeltext = Gtk.Label(label="Game timer:", halign=Gtk.Align.END)
        topbox.pack_start(timelabeltext, False, True, 0)

        timelabel = Gtk.Label(label="--:--", halign=Gtk.Align.START)
        topbox.pack_start(timelabel, False, True, 10)

        buildorderlist = Gtk.ListBox(expand=True)
        box_outer.pack_end(buildorderlist, False, True, 0)
        buildorderlist.show_all()

        self.timelabel = timelabel
        self.items = []
        self.buildorderlist = buildorderlist

        self.get_buildorderlist()
        self.set_buildorderlist()

        GLib.timeout_add(1000, self.update_timelabel, None)

        self.current_index = 0

    def notify(self, message):
        notification = Notify.Notification.new("", message)
        notification.set_timeout(5000)
        notification.show()

    def filecombo_changed(self, widget):
        text=widget.get_model()[widget.get_active_iter()][0]
        self.selected_buildorder = text
        self.resetbutton_clicked(None, None)

    def resetbutton_clicked(self, widget, data):
        self.timelabel.set_markup("--:--")
        self.clear_buildorderlist()
        self.get_buildorderlist()
        self.set_buildorderlist()

    def clear_buildorderlist(self):
        for item in self.buildorderlist.get_children():
            self.buildorderlist.remove(item)

    def get_buildorderlist(self):
        self.items = []
        with open(os.path.join(self.path, self.selected_buildorder)) as fd:
            for line in fd:
                line = line.strip()
                supply, gametime, item = line.split(None, 2)
                self.items.append(line)
        self.current_index = 0

    def set_buildorderlist(self, game_time=0):
        if self.current_index < 5:
            start_offset = 0
            end_offset = 11
        else:
            start_offset = self.current_index - 5
            end_offset = self.current_index + 6
        selected_child = None
        for item in self.items[start_offset:end_offset]:
            new_item = BuildOrderItem(item)
            if item == self.items[self.current_index]:
                selected_child = new_item
                if game_time > 0:
                    self.notify(item)
            self.buildorderlist.add(new_item)
        self.buildorderlist.select_row(selected_child)
        self.buildorderlist.show_all()

    def update_buildorderlist(self, mi, ss):
        game_ts = int(mi * 60 + ss)
        try:
            item = self.items[self.current_index]
        except IndexError as err:
            return
        str_mi, str_ss = item.split()[1].split(":")
        build_ts = int(str_mi) * 60 + int(str_ss)
        if game_ts >= build_ts:
            self.clear_buildorderlist()
            self.set_buildorderlist(game_ts)
            self.current_index = self.current_index + 1

    def is_running(self):
        try:
            req = requests.request('GET', UI_URL)
        except ConnectionError as e:
            print("Is StarCraftII runing?")
            return False
        screens = req.json().get("activeScreens")
        return True if len(screens) == 0 else False

    def update_timelabel(self, data):
        if (self.is_running()):
            try:
                req = requests.request('GET', GAMETIME_URL)
            except ConnectionError as e:
                print("Is StarCraftII runing?")
                return False

            dt = req.json().get("displayTime")
            mi = dt // 60
            ss = dt % 60
            str = "{}:{}".format(int(mi),int(ss))
            self.timelabel.set_markup(str)
            self.update_buildorderlist(mi, ss)

        return True


class BOPApplication(Gtk.Application):
    def __init__(self, *args, **kwargs):
        Gtk.Application.__init__(self,
                                 *args,
                                 flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
                                 **kwargs)
        self.add_main_option("path", ord("p"), GLib.OptionFlags.NONE,
                             GLib.OptionArg.STRING, "Path to build order files", None)

    def do_command_line(self, command_line):
        options = command_line.get_options_dict()
        options = options.end().unpack()
        if "path" in options:
            self.buildorders_path = options["path"]
        else:
            self.buildorders_path = ""
        self.activate()
        return 0

    def do_activate(self):
        win = BOPMainWindow(self)
        win.show_all()

    def do_startup(self):
        Gtk.Application.do_startup(self)


if __name__ == '__main__':
    app = BOPApplication()
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)

# vi: set fileencoding=utf-8 :
