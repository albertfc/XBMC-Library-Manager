#!/usr/bin/env python

import os
import shutil
import glob
import re
import xbmc, xbmcgui, xbmcaddon

# Script constants
__scriptname__ = "Library Manager"
__author__     = "Albert Farres"
__license__    = "GPLv3"
__version__    = "0.1"
__url__        = "n/a"
__email__      = "albertfc@gmail.com"
__status__     = "Prototype"
__settings__   = xbmcaddon.Addon(id="script.LibraryManager")
__language__   = __settings__.getLocalizedString
__cwd__        = __settings__.getAddonInfo('path')

from resources.lib.logging import logging
try:
    from sqlite3 import dbapi2 as sqlite
    logging.dbg( "Loading sqlite3 as DB engine" )
except:
    from pysqlite2 import dbapi2 as sqlite
    logging.dbg("Loading pysqlite2 as DB engine" )

#enable localization
getLS   = sys.modules[ "__main__" ].__language__

#get actioncodes from keymap.xml
ACTION_PREVIOUS_MENU = 10
ACTION_SELECT_ITEM = 7
ACTION_PARENT_DIR = 9

INIT_LIST_ITEM = getLS(15)

class metaStr( str ):

    def __new__(cls,value,meta):
        obj = str.__new__(cls,value.encode('utf8'))
	#obj = str.__new__(cls,value)
        obj.meta = meta
        return obj

class place( object ):
    xpos = None
    ypos = None
    xsize = None 
    ysize = None

class LibMngClass(xbmcgui.Window):

    class widget( object ):
        label = None
        button = None
        wlist = None
        mlist = None
	path  = None
    
    def __init__(self):

        self.scalex = self.getWidth() / float( 100 ) 
        self.scaley = self.getHeight() / float( 100 )

	labelp = place()
	labelp.xpos = int( 35*self.scalex )
	labelp.ypos = int( 5*self.scaley )
	labelp.xsize = int( 60*self.scalex )
	labelp.ysize = int( 5*self.scaley )

	buttonp = place()
	buttonp.xpos = int( 5*self.scalex )
	buttonp.ypos = int( 5*self.scaley )
	buttonp.xsize = int( 25*self.scalex ) 
	buttonp.ysize = int( 5*self.scaley )

	listp = place()
	listp.xpos = int( 5*self.scalex )
	listp.ypos = int( 20*self.scaley )
	listp.xsize = int( 90*self.scalex )
	listp.ysize = int( 60*self.scaley )
	
        # Source widgets 
	basey = 0
        self.src = self.widget()
        self.src.label = xbmcgui.ControlLabel( labelp.xpos, basey + labelp.ypos,
                labelp.xsize, labelp.ysize, getLS(16), 'font14', '0xFFBBBBFF')
        self.addControl( self.src.label )
        self.src.button = xbmcgui.ControlButton( buttonp.xpos, basey +
                buttonp.ypos, buttonp.xsize, buttonp.ysize, getLS(10) )
        self.addControl(self.src.button)
        self.src.wlist = xbmcgui.ControlList( listp.xpos, basey + listp.ypos,
                listp.xsize, listp.ysize, buttonFocusTexture="MenuItemFO.png",
                selectedColor='0xFFBBBBFF')
        self.addControl(self.src.wlist)
        self.src.wlist.addItem( INIT_LIST_ITEM )

        # Destination widgets 
	basey = int( 5*self.scaley )
        self.dst = self.widget()
        self.dst.label = xbmcgui.ControlLabel( labelp.xpos, basey + labelp.ypos,
                labelp.xsize, labelp.ysize, getLS(16), 'font14', '0xFFBBBBFF')
        self.addControl( self.dst.label )
        self.dst.button = xbmcgui.ControlButton( buttonp.xpos, basey +
                buttonp.ypos, buttonp.xsize, buttonp.ysize, getLS(11) )
        self.addControl(self.dst.button)
	#self.dst.wlist = xbmcgui.ControlList( basex + listp.xpos, listp.ypos,
	#        listp.xsize, listp.ysize, buttonFocusTexture="MenuItemFO.png",
	#        selectedColor='0xFFBBBBFF')
	#self.addControl(self.dst.wlist)
	#self.dst.wlist.addItem( INIT_LIST_ITEM )

        # Ok and Cancel
       	okp = place()
	okp.xpos = int( 85*self.scalex )
	okp.ypos = int( 85*self.scaley )
	okp.xsize = int( 10*self.scalex )
	okp.ysize = int( 10*self.scaley )
	self.okButton = xbmcgui.ControlButton( okp.xpos, okp.ypos,
	     okp.xsize, okp.ysize, getLS(12) )
        self.addControl(self.okButton)
       	cancelp = place()
	cancelp.xpos = int( 70*self.scalex )
	cancelp.ypos = int( 85*self.scaley )
	cancelp.xsize = int( 10*self.scalex )
	cancelp.ysize = int( 10*self.scaley )
	self.cancelButton = xbmcgui.ControlButton( cancelp.xpos, cancelp.ypos,
	     cancelp.xsize, cancelp.ysize, getLS(13) )
        self.addControl(self.cancelButton)

        # Options buttion 
       	optionp = place()
	optionp.xpos = int( 5*self.scalex )
	optionp.ypos = int( 85*self.scaley )
	optionp.xsize = int( 15*self.scalex )
	optionp.ysize = int( 10*self.scaley )
	self.optionButton = xbmcgui.ControlButton( optionp.xpos, optionp.ypos,
	     optionp.xsize, optionp.ysize, getLS(14)+"..." )
        self.addControl(self.optionButton)

        # Set widgets order navigation 
        self.src.button.controlUp( self.okButton )
        self.src.button.controlDown( self.dst.button )
        self.dst.button.controlUp( self.src.button )
        self.dst.button.controlDown( self.src.wlist )
        self.src.wlist.controlUp( self.dst.button )
        self.src.wlist.controlDown( self.okButton )
        self.src.wlist.controlLeft( self.okButton )
        self.src.wlist.controlRight( self.okButton )
        self.okButton.controlUp( self.src.wlist )
        self.okButton.controlDown( self.src.button )
        self.okButton.controlLeft( self.cancelButton )
        self.cancelButton.controlUp( self.src.wlist )
        self.cancelButton.controlDown( self.src.button )
        self.cancelButton.controlRight( self.okButton )
        self.cancelButton.controlLeft( self.optionButton )
        self.optionButton.controlUp( self.src.wlist )
        self.optionButton.controlDown( self.src.button )
        self.optionButton.controlRight( self.cancelButton )

        # Set focus 
        self.setFocus( self.src.button )

        # Open DB 
        self.open_conn()

        # Set default options 
        self.options = OptionClass.getDefOptions() 
        self.optionsWindow = OptionClass( options=self.options )

    def open_conn( self ):
        self.db_conn = sqlite.connect( xbmc.translatePath( 
            'special://database/MyVideos34.db' ) )

    def close_conn( self ):
        self.db_conn.close()
 
    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU:
            # Close DB 
            self.close_conn()
            self.close()

    def onControl(self, control):
        if control == self.src.button:
            self.on_widget_button( self.src )
	    self.update_list( self.src )
        if control == self.dst.button:
            self.on_widget_button( self.dst )

        if control == self.src.wlist or control == self.dst.wlist:
            # Get selected item 
            item = control.getSelectedItem()
            # Updated item state 
            item.select( not item.isSelected() )

        if control == self.okButton:
            self.on_ok_button()

	if control == self.cancelButton:
            self.on_cancel_button()

	if control == self.optionButton:
            self.optionsWindow.doModal()
            self.options = self.optionsWindow.getOptions()
            if self.src.mlist:
	        self.update_list( self.src )

    def on_cancel_button( self ):
        # Close DB 
	self.close_conn()
        self.close()

    def on_widget_button( self, widget ):
        dialog = xbmcgui.Dialog()
        # Get path lists 
        paths = self.get_path_list( )
        # Get selected option 
        option_idx = dialog.select( getLS(23), paths )
        if option_idx < 0:
            return 
	# Check path availability  
	if not os.path.exists( paths[option_idx] ):
	  dialog.ok( getLS(20), getLS(21), getLS(22) )
	  return
        # Save option 
        widget.path = paths[option_idx]
        # Set source lable properly 
        widget.label.setLabel( paths[option_idx] )
        # Update list 
	#self.update_list( widget )
	#self.setFocus( widget.wlist )

    def on_ok_button( self ):
        # Check values 
        dialog = xbmcgui.Dialog()
        if self.src.path is None:
            dialog.ok( getLS(30), getLS(31) )
            return
        if self.dst.path is None:
            dialog.ok( getLS(32), getLS(33) )
            return
        if self.src.path == self.dst.path:
            dialog.ok( getLS(34), getLS(35) )
            return
        sel_items = []
        for i in range( self.src.wlist.size() ):
            if self.src.wlist.getListItem( i ).isSelected(): 
                sel_items.append( i )
        if len( sel_items ) > 0:
            if not dialog.yesno( getLS(36), "%d " % len( sel_items) + getLS(37)  , getLS(38) ):
                return 
        else:
            dialog.ok( getLS(39), getLS(40) )
            return
        # Move Movies 
        progress = xbmcgui.DialogProgress() 
        progress.create( getLS(36) )
        for i in sel_items:
            progress.update( sel_items.index( i ) * 100 / len( sel_items),
                    "", getLS(41)+" %s" % self.src.mlist[i] )
            self.move_movie( self.src.mlist[i], self.src.path,
                    self.dst.path )
            if progress.iscanceled():
                break
        progress.close()
        # Update lists 
        self.update_list( self.src )
	#self.update_list( self.dst )


    def update_list( self, widget ):
        if widget.path:
            # Reset list 
            widget.wlist.reset()
            # Popullate file list 
            widget.mlist = self.get_movie_list( widget.path.meta )
            widget.wlist.addItems( widget.mlist )
 
    def get_path_list( self ):
        # Create empty list
        res = []
        # Create query 
        query = "SELECT idPath, strPath \
                 FROM   path \
                 WHERE  strContent = \"movies\""
        # Create a cursor
        c = self.db_conn.cursor()
        # Launch query 
        c.execute( query )
        # Build result 
        for idp, strp in c:
            res.append( metaStr( strp, idp ) )
        # Close cursor 
        c.close()
        # Return result 
        return res

    def get_movie_list( self, id_path ):
        # Create empty list 
        res = []
        # Create query 
        query = "SELECT f.idFile, m.c00 \
                 FROM   movie m, files f \
                 WHERE  m.idFile = f.idFile AND f.idPath = ?"
        if self.options["watched"]:
            query += "  AND f.playcount > 0 "
	query +="ORDER BY m.c00"
        # Create values 
        value = id_path, 
        # Create a cursor
        c = self.db_conn.cursor()
        # Launch query 
        c.execute( query, value )
        # Build result 
        for idf, mov in c:
            res.append( metaStr( mov, idf ) )
        # Close cursor 
        c.close()
        # Return result 
        return res

    def move_movie( self, movie, old_path, new_path ):
        ## Update file with new id 
        # Create query 
        query = "UPDATE files \
                 SET    idPath=? WHERE idFile=?"  
        # Create values 
        value = new_path.meta, movie.meta
	# Create a cursor
        c = self.db_conn.cursor()
        # Launch query 
	c.execute( query, value )

	### Move file 
	## Get filename 
	# Create query 
        query = "SELECT f.strFilename \
                 FROM   files f \
                 WHERE  f.idFile = ?"
        # Create values 
        value = movie.meta, 
        # Launch query 
	c.execute( query, value )
        # Build result 
	mfile = c.fetchone()[0].encode('utf8')
	#mfile = str( c.fetchone()[0] )

        ## Deal with stacked files 
        if mfile.startswith( "stack://" ):
            # Update db file with new values 
            query = "UPDATE files \
                     SET    strFilename=? WHERE idFile=?"  
            # Create values 
            value = mfile.replace( old_path, new_path ), movie.meta
            # Launch query 
            c.execute( query, value )
            #" Remove whites spaces arround fnames 
            mfiles = map( lambda x:x.strip(), mfile[8:].split( "," ) )
        else:
            mfiles = [old_path+mfile]

        ## Do the move 
        for mfile in mfiles:
            # Get movie file and related files (e.g. subtitles files)
            src = str( mfile )
            logging.dbg( "srcfile: %s" % src )
            dst = mfile.replace( old_path, new_path ) 
            logging.dbg( "dstfile: %s" % dst )

            # Get cache file names
            thsrc = xbmc.getCacheThumbName( src )
            logging.dbg( "srcthumb: %s" % thsrc )
            thdst = xbmc.getCacheThumbName( dst )
            logging.dbg( "dstthumb: %s" % thdst )
 
	    # replace braces on filename for [[] and []] to be able to use glob
            root, ext = os.path.splitext( src )
            srcfn = glob.glob( re.sub( r'(\[|])', r'[\1]', root ) + ".*" ) 
            dstfn = map( lambda x:x.replace( old_path, new_path ), srcfn )

            # Get thumbnail fname
            srcfn.append( xbmc.translatePath( 'special://thumbnails/Video' ) 
                    + "/" + thsrc[0] + "/" + thsrc )
            dstfn.append( xbmc.translatePath( 'special://thumbnails/Video' ) 
                    + "/" + thdst[0] + "/" + thdst )

            # Get auto-thumbnail fname
            srcfn.append( xbmc.translatePath( 'special://thumbnails/Video' ) 
                    + "/" + thsrc[0] + "/auto-" + thsrc )
            dstfn.append( xbmc.translatePath( 'special://thumbnails/Video' ) 
                    + "/" + thdst[0] + "/auto-" + thdst )

            # get Fanart fname
            srcfn.append( xbmc.translatePath( 'special://thumbnails/Video' ) 
                    + "/Fanart/" + thsrc )
            dstfn.append( xbmc.translatePath( 'special://thumbnails/Video' ) 
                    + "/Fanart/" + thdst )

            # Move files
            for i in range( len( srcfn ) ):
                try:
                    shutil.move( srcfn[i], dstfn[i] )
                    logging.dbg( "move %s %s" % ( srcfn[i], dstfn[i] ) )
                except IOError:
                    logging.dbg( "Error moving %s %s" % ( srcfn[i], dstfn[i] ) )
                    pass

        # Commit Changes 
        self.db_conn.commit()
        # Close cursor 
        c.close()


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


if __name__ == "__main__":

    mydisplay = LibMngClass()
    mydisplay .doModal()
    del mydisplay
    #sys.modules.clear()
    #xbmc.sleep( 5000 )

