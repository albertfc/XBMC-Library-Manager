#!/usr/bin/env python

import sys
import xbmc, xbmcgui, xbmcaddon

# Script constants
__scriptname__ = "Library Manager"
__author__     = "Albert Farres"
__license__    = "GPLv3"
__version__    = "0.1"
__url__        = "https://github.com/albertfc/XBMC-Library-Manager"
__email__      = "albertfc@gmail.com"
__status__     = "Prototype"
__settings__   = xbmcaddon.Addon(id="script.LibraryManager")
__language__   = __settings__.getLocalizedString
__cwd__        = __settings__.getAddonInfo('path')

from resources.lib.logging import logging
from resources.lib.utils import place
from resources.lib.movies import MovieWindow
from resources.lib.tvshows import TVshowWindow

#enable localization
getLS   = sys.modules[ "__main__" ].__language__

#get actioncodes from keymap.xml
ACTION_PREVIOUS_MENU = 10

class LibMngClass(xbmcgui.Window):

    def __init__(self):

        self.scalex = self.getWidth() / float( 100 ) 
        self.scaley = self.getHeight() / float( 100 )

        # Create windows
        self.movieWindow = None
        self.tvshowWindow = None
        self.musicWindow = None

        # Create title
	labelp = place()
	labelp.xpos = int( 30*self.scalex )
	labelp.ypos = int( 25*self.scaley )
	labelp.xsize = int( 60*self.scalex )
	labelp.ysize = int( 5*self.scaley )
        self.titleLabel = xbmcgui.ControlLabel( labelp.xpos, labelp.ypos,
                labelp.xsize, labelp.ysize, getLS(0), 'font14', '0xFFBBBBFF')
        self.addControl( self.titleLabel )

        # Create buttons
	buttonp = place()
	buttonp.xpos = int( 35*self.scalex )
	buttonp.ypos = int( 35*self.scaley )
	buttonp.xsize = int( 30*self.scalex ) 
	buttonp.ysize = int( 5*self.scaley )
	basey = 0
        self.movieButton = xbmcgui.ControlButton( buttonp.xpos, basey +
                buttonp.ypos, buttonp.xsize, buttonp.ysize, getLS(1) )
        self.addControl(self.movieButton)
	basey = int( 10*self.scaley )
        self.tvshowButton = xbmcgui.ControlButton( buttonp.xpos, basey +
                buttonp.ypos, buttonp.xsize, buttonp.ysize, getLS(2) )
        self.addControl(self.tvshowButton)
	basey = int( 20*self.scaley )
        self.musicButton = xbmcgui.ControlButton( buttonp.xpos, basey +
                buttonp.ypos, buttonp.xsize, buttonp.ysize, getLS(3) )
        self.addControl(self.musicButton)

        # Set widgets order navigation 
        self.movieButton.controlUp( self.musicButton )
        self.movieButton.controlDown( self.tvshowButton )
        self.tvshowButton.controlUp( self.movieButton )
        self.tvshowButton.controlDown( self.musicButton )
        self.musicButton.controlUp( self.tvshowButton )
        self.musicButton.controlDown( self.movieButton )

        # Set focus 
        self.setFocus( self.movieButton )

    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU:
            self.close()
            
    def onControl(self, control):
	if control == self.movieButton:
            if self.movieWindow is None:
                self.movieWindow = MovieWindow()
            self.movieWindow.doModal()
        if control == self.tvshowButton:
            if self.tvshowWindow is None:
                self.tvshowWindow = TVshowWindow()
            self.tvshowWindow.doModal()
        if control == self.musicButton:
            xbmcgui.Dialog().ok( getLS(4), getLS(5) )


if __name__ == "__main__":

    mydisplay = LibMngClass()
    mydisplay .doModal()
    del mydisplay
    #sys.modules.clear()
    #xbmc.sleep( 5000 )

