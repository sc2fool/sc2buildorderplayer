# sc2buildorderplayer

StarCraftII Build Order Player

*Caveat: This script is supplied as-is. I take no responsibilities what so ever and I do not supply support of any kind.*


## About

This a simple tool to help with practicing build orders in StarCraftII. If you're on Windows I recommend to look at [The Spawning Tool Build Advisor](http://store.overwolf.com/app/overwolf-spawning_tool_build_advisor).

The script is only tested and verified to run on Ubuntu 16.10 but should run anywhere if the prerequisites are satisfied.

## Prerequisites

 * Python
 * PyGTK+3

Also this script is not very useful if you don't have a second screen to keep the build order player on. I haven't figured out how to create a proper overlay to stay on top of a fullscreen application. Alternatively you can run the game in windowed mode when practicing your build order.

## How to use

Create a text file for each build order you want to be able to use. I just copy the build order text from [Spawning Tool](http://lotv.spawningtool.com) and saves it as <build order name>.txt in the same directory as this script.
Technically each line is parsed as:
supply gametime description

That makes it very simple to write your own build orders too.

With StarCraftII running, start this script, select the build order you want to practice and start a game.

The script will sync the build order with the game timer using the Client API and highlight the current step in the build order.

To restart press reset-button. To practice another build order simply choose it in the dropdown.

## Resources

 * [battle.net forum thread about the Client API](https://us.battle.net/forums/en/sc2/topic/20748195420)
 * [The Python GTK+ 3 Tutorial](http://python-gtk-3-tutorial.readthedocs.io/en/latest/index.html)
 * [GNOME Platform Demos in Python](https://developer.gnome.org/gnome-devel-demos/stable/py.html.en)
 * [GTK+ 3 Reference Manual](https://developer.gnome.org/gtk3/stable/)
