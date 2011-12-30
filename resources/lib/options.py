#!/usr/bin/env python

import sys
import xbmc, xbmcgui, xbmcaddon

from resources.lib.logging import logging
from resources.lib.utils import place

#enable localization
getLS   = sys.modules[ "__main__" ].__language__

#get actioncodes from keymap.xml
ACTION_PREVIOUS_MENU = 10


class OptionClass( xbmcgui.Window ):

    def __init__(self, options):

        self.options = options 

        self.scalex = self.getWidth() / float( 100 ) 
        self.scaley = self.getHeight() / float( 100 )

	optionp = place()
	optionp.xpos = int( 5*self.scalex )
	optionp.ypos = int( 5*self.scaley )
	optionp.xsize = int( 60*self.scalex )
	optionp.ysize =  int( 5*self.scaley )

        basex = 0
        self.watchedRadio = xbmcgui.ControlRadioButton( basex + optionp.xpos, 
                optionp.ypos, optionp.xsize, optionp.ysize, 
                getLS(50), font='font14')
        self.watchedRadio.setSelected( options["watched"] )
        self.addControl( self.watchedRadio )

        # Set focus 
        self.setFocus( self.watchedRadio )

    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU:
            self.close()

    def onControl( self, control ):
        return

    def getOptions( self ):
        self.options["watched"] = self.watchedRadio.isSelected()
        return self.options

    @staticmethod
    def getDefOptions():
        options = dict()
        options["watched"] = False
        return options

