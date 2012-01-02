#!/usr/bin/env python

import sys
import xbmc

from resources.lib.logging import logging

try:
    from sqlite3 import dbapi2 as sqlite
    logging.dbg( "Loading sqlite3 as DB engine" )
except:
    from pysqlite2 import dbapi2 as sqlite
    logging.dbg("Loading pysqlite2 as DB engine" )


class place( object ):
    xpos = None
    ypos = None
    xsize = None 
    ysize = None

class metaStr( unicode ):

    def __new__(cls,value,meta):
	obj = unicode.__new__(cls,value)
        obj.meta = meta
        return obj

class dbMng( object ):

    def __init__(self):
        self.db_conn = None

    def open_conn( self ):
        self.db_conn = sqlite.connect( xbmc.translatePath( 
            'special://database/MyVideos34.db' ) )

    def close_conn( self ):
        if self.db_conn:
            self.db_conn.close()
        self.db_conn = None

    def create_cursor( self ):
        if self.db_conn:
            return self.db_conn.cursor()
        else:
            return None

    def commit( self ):
        if self.db_conn:
            return self.db_conn.commit()
        else:
            return None
 
