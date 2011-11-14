#!/usr/bin/env python

import sys
import xbmc

#enable localization
getLS   = sys.modules[ "__main__" ].__language__

class logging:

    @staticmethod
    def dbg( msg ):
        xbmc.output( "LibraryManager: "+msg, xbmc.LOGDEBUG )


