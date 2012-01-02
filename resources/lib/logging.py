#!/usr/bin/env python

import sys
import xbmc

#enable localization
getLS   = sys.modules[ "__main__" ].__language__

class logging:

    @staticmethod
    def dbg( msg ):
        xbmc.output( "LibraryManager: "+msg.encode('utf-8'), xbmc.LOGDEBUG )

    @staticmethod
    def err( msg ):
        xbmc.output( "LibraryManager: "+msg.encode('utf-8'), xbmc.LOGERROR )


