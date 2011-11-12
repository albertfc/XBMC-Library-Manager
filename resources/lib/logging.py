#!/usr/bin/env python

import xbmc

class logging:

    @staticmethod
    def dbg( msg ):
        xbmc.output( "LibraryManager: "+msg, xbmc.LOGDEBUG )


