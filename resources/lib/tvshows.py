#!/usr/bin/env python

import sys
import os
import errno
import shutil
import glob
import re
import xbmc, xbmcgui, xbmcaddon

from resources.lib.logging import logging
from resources.lib.options import OptionClass
from resources.lib.utils import place, metaStr, dbMng

#enable localization
getLS   = sys.modules[ "__main__" ].__language__

#get actioncodes from keymap.xml
ACTION_PREVIOUS_MENU = 10
ACTION_SELECT_ITEM = 7
ACTION_PARENT_DIR = 9

INIT_LIST_ITEM = getLS(15)

class TVshowWindow(xbmcgui.Window):

    class widget( object ):
        label = None
        button = None
        w1list = None
        w2list = None
        tslist = None
        eplist = None
	path = None
        show = None
    
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
	listp.xsize = int( 40*self.scalex )
	listp.ysize = int( 60*self.scaley )
	
        # Source widgets 
	basey = 0
        basex = 0
        self.src = self.widget()
        self.src.label = xbmcgui.ControlLabel( basex + labelp.xpos, basey + labelp.ypos,
                labelp.xsize, labelp.ysize, getLS(16), 'font14', '0xFFBBBBFF')
        self.addControl( self.src.label )
        self.src.button = xbmcgui.ControlButton( basex + buttonp.xpos, basey +
                buttonp.ypos, buttonp.xsize, buttonp.ysize, getLS(10) )
        self.addControl(self.src.button)
        self.src.w1list = xbmcgui.ControlList( basex + listp.xpos, basey + listp.ypos,
                listp.xsize, listp.ysize, buttonFocusTexture="MenuItemFO.png",
                selectedColor='0xFFBBBBFF')
        self.addControl(self.src.w1list)
        self.src.w1list.addItem( INIT_LIST_ITEM )
        basex = int( 50*self.scalex )
        self.src.w2list = xbmcgui.ControlList( basex + listp.xpos, basey + listp.ypos,
                listp.xsize, listp.ysize, buttonFocusTexture="MenuItemFO.png",
                selectedColor='0xFFBBBBFF')
        self.addControl(self.src.w2list)
        self.src.w2list.addItem( INIT_LIST_ITEM )

        # Destination widgets 
	basey = int( 5*self.scaley )
        self.dst = self.widget()
        self.dst.label = xbmcgui.ControlLabel( labelp.xpos, basey + labelp.ypos,
                labelp.xsize, labelp.ysize, getLS(16), 'font14', '0xFFBBBBFF')
        self.addControl( self.dst.label )
        self.dst.button = xbmcgui.ControlButton( buttonp.xpos, basey +
                buttonp.ypos, buttonp.xsize, buttonp.ysize, getLS(11) )
        self.addControl(self.dst.button)
	
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
        self.dst.button.controlDown( self.src.w1list )
        self.src.w1list.controlUp( self.dst.button )
        self.src.w1list.controlDown( self.okButton )
        self.src.w1list.controlLeft( self.okButton )
        self.src.w1list.controlRight( self.src.w2list )
        self.src.w2list.controlUp( self.dst.button )
        self.src.w2list.controlDown( self.okButton )
        self.src.w2list.controlLeft( self.src.w1list )
        self.src.w2list.controlRight( self.okButton )
        self.okButton.controlUp( self.src.w1list )
        self.okButton.controlDown( self.src.button )
        self.okButton.controlLeft( self.cancelButton )
        self.cancelButton.controlUp( self.src.w1list )
        self.cancelButton.controlDown( self.src.button )
        self.cancelButton.controlRight( self.okButton )
        self.cancelButton.controlLeft( self.optionButton )
        self.optionButton.controlUp( self.src.w1list )
        self.optionButton.controlDown( self.src.button )
        self.optionButton.controlRight( self.cancelButton )

        # Set focus 
        self.setFocus( self.src.button )

        # Set default options 
        self.options = OptionClass.getDefOptions() 
        self.optionsWindow = OptionClass( options=self.options )

        # DB mng
        self.db = dbMng()

    def doModal( self ):
        # Open DB 
        self.db.open_conn()
        return super( TVshowWindow, self ).doModal()

    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU:
            # Close DB 
            self.db.close_conn()
            self.close()

    def onControl(self, control):
        if control == self.src.button:
            self.on_widget_button( self.src )
	    self.update_tvshow_list( self.src )
        if control == self.dst.button:
            self.on_widget_button( self.dst )

        if control == self.src.w1list:
            if self.src.path:
                self.src.show = self.src.tslist[control.getSelectedPosition()] 
                self.update_episode_list( self.src )
                # Set focus on ep. list
                self.setFocus( self.src.w2list )

        if control == self.src.w2list:
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
            if self.src.eplist:
	        self.update_episode_list( self.src )

    def on_cancel_button( self ):
        # Close DB 
	self.db.close_conn()
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
        for i in range( self.src.w2list.size() ):
            if self.src.w2list.getListItem( i ).isSelected(): 
                sel_items.append( i )
        if len( sel_items ) > 0:
            if not dialog.yesno( getLS(60), "%d " % len( sel_items ) 
                    + getLS(61)  , getLS(38) ):
                return 
        else:
            dialog.ok( getLS(62), getLS(63) )
            return
        # Move TV shows
        progress = xbmcgui.DialogProgress() 
        progress.create( getLS(60) )
        for i in sel_items:
            progress.update( sel_items.index( i ) * 100 / len( sel_items ),
                    "", getLS(41)+" %s" % self.src.eplist[i].encode('utf-8') )
            self.move_episode( self.src.eplist[i], self.src.path,
                    self.dst.path )
            if progress.iscanceled():
                break
        progress.close()
        # Update lists 
        self.update_episode_list( self.src )

    def update_tvshow_list( self, widget ):
        if widget.path:
            # Reset list 
            widget.w1list.reset()
            # Popullate file list 
            widget.tslist = self.get_tvshow_list( widget.path )
            widget.w1list.addItems( widget.tslist )

    def update_episode_list( self, widget ):
        if widget.show:
            # Reset list 
            widget.w2list.reset()
            # Popullate file list 
            widget.eplist = self.get_episode_list( widget.show ) 
            widget.w2list.addItems( widget.eplist ) 
 
    def get_path_list( self ):
        # Create empty list
        res = []
        # Create query 
        query = "SELECT idPath, strPath \
                 FROM   path \
                 WHERE  strContent = \"tvshows\""
        # Create a cursor
        c = self.db.create_cursor()
        # Launch query 
        c.execute( query )
        # Build result 
        for idp, strp in c:
            res.append( metaStr( strp, idp ) )
        # Close cursor 
        c.close()
        # Return result 
        return res

    def get_tvshow_list( self, path ):
        # Create empty list 
        res = []
        # Create query 
        query = "SELECT ts.idShow, ts.c00  \
                 FROM   tvshowlinkpath tslp, tvshow ts \
                 WHERE  tslp.idShow = ts.idShow AND idPath IN \
                        ( SELECT idPath \
                          FROM   path \
                          WHERE  strPath LIKE ? ) \
	         ORDER BY ts.c00"
        # Create values 
        value = path+"%", 
        # Create a cursor
        c = self.db.create_cursor()
        # Launch query 
        c.execute( query, value )
        # Build result 
        for ids, tvs in c:
            res.append( metaStr( tvs, ids ) )
        # Close cursor 
        c.close()
        # Return result 
        return res

    def get_episode_list( self, show ):
        # Create empty list 
        res = []
        # Create query 
        query = "SELECT e.c12, e.c13, e.c00, e.idFile \
                 FROM   tvshowlinkepisode tsle, episode e, files f \
                 WHERE  tsle.idEpisode = e.idEpisode AND e.idFile = f.idFile \
                        AND tsle.idShow = ?"
        if self.options["watched"]:
            query += "  AND f.playcount > 0 "
        # Create values 
        value = show.meta, 
        # Create a cursor
        c = self.db.create_cursor()
        # Launch query 
        c.execute( query, value )
        # Build result 
        for s, e, name, eid in c:
            res.append( metaStr( "%02dx%02d - %s" % ( int(s), int(e), name ), 
                eid ) )
        # Close cursor 
        c.close()
        # Return result 
        return sorted( res )

    def move_episode( self, episode, old_path, new_path ):
        logging.dbg( "moving episode '%s' from '%s' to '%s'" % ( episode,
            old_path, new_path ) ) 

	# Create a cursor
        c = self.db.create_cursor()

	## Get filename, path, show and episode id and season number
	# Create query 
        query = "SELECT e.idEpisode, f.strFilename, p.strPath, p.idPath, \
                        tsle.idShow, e.c12 \
                 FROM   episode e, files f, path p, tvshowlinkepisode tsle \
                 WHERE  e.idFile = f.idFile AND f.idPath = p.idPath \
                        AND tsle.idEpisode = e.idEpisode AND f.idFile = ?"
        # Create values 
        value = episode.meta, 
        # Launch query 
	c.execute( query, value )
        # Build result 
        res = c.fetchone()
	eid   = res[0]
	efile = unicode( res[1] )
	epath = unicode( res[2] )
	eidpath = res[3]
        eidshow = res[4]
        season = int( res[5] )
        logging.dbg( "filename: '%s'" % ( epath+efile ) )

        # Compute new path
        new_epath = epath.replace( old_path, new_path )

        ## Check if new path exists on DB 
        # Create query 
        query = "SELECT p.idPath \
                 FROM   path p \
                 WHERE  p.strPath = ?"
        # Create values 
        value = new_epath, 
        # Launch query 
	c.execute( query, value )
        # Build result 
	res = c.fetchone()
        if res:
            new_eidpath = res[0]
        else:
            logging.dbg( "Path does not exist on db" )
            ## Insert new path on DB
            # Create query 
            query = "INSERT INTO path \
                            ( strPath, strContent, strScraper) \
                     VALUES ( ?, '', '')"
            # Create values 
            value = new_epath,
            # Launch query 
            c.execute( query, value )
            # Get new id
            new_eidpath = c.lastrowid
            logging.dbg( "New path id: %d" %( new_eidpath ) )

        # Try to Create new path on system
        try:
            os.makedirs( new_epath )
            logging.dbg( "Creating directory '%s'" % ( new_epath ) )
        except OSError, e:
            if e.errno == errno.EEXIST:
                pass
            else:
                logging.err( "Error Creating directory '%s': %s" % (
                    new_epath, e.strerror ) )
                return

        ## Get new show id and path 
        # Create query 
        query = "SELECT p.strPath, tslp.idShow \
                 FROM   tvshowlinkpath tslp, path p \
                 WHERE  tslp.idPath = p.idPath"
        # Launch query 
        c.execute( query )
        # check result
        for new_tspath, new_idshow in c:
            if unicode( new_tspath ) in new_epath:
                break
        else:
            # Create a new TV show on DB
            logging.dbg( "Cannot find a proper TV show for this path '%s'.\
 Creating a new one." % ( new_epath) )
            new_tspath, new_idshow = self.create_new_tvshow( eidshow, old_path,
                    new_path, c )
            if new_idshow is None:
                return

        ## Update file with new path id 
        # Create query 
        query = "UPDATE files \
                 SET    idPath = ? \
                 WHERE  idFile = ?"  
        # Create values 
        value = new_eidpath, episode.meta
        # Launch query 
        c.execute( query, value )

        ## Update episode link with new show id 
        # Create query 
        query = "UPDATE tvshowlinkepisode \
                 SET    idShow = ? \
                 WHERE  idEpisode = ?"  
        # Create values 
        value = new_idshow, eid
        # Launch query 
        c.execute( query, value )

        ## Copy season fanart cache
        # http://forum.xbmc.org/showthread.php?p=324453#post324453
        dst = "season" + unicode( new_tspath ) + xbmc.getLocalizedString( 20358 )
        dst = dst % season
        src = dst.replace( new_path, old_path ) 
        logging.dbg( "src season fanart: %s" % src )
        logging.dbg( "dst season fanart: %s" % dst )
        # Get cache file names
        thsrc = xbmc.getCacheThumbName( src )
        thdst = xbmc.getCacheThumbName( dst )
        # Get thumbnail fname
        srcfn = xbmc.translatePath( 'special://thumbnails/Video' ) + "/" + thsrc[0] + "/" + thsrc 
        dstfn =  xbmc.translatePath( 'special://thumbnails/Video' ) + "/" + thdst[0] + "/" + thdst 
        # Copy files
        try:
            shutil.copy( srcfn, dstfn )
            logging.dbg( "copy %s %s" % ( srcfn, dstfn ) )
        except IOError, e:
            logging.err( "Error copying '%s' to '%s': %s" % ( srcfn, dstfn, e ) )
            pass

        ## Do the move 
        src = epath+efile
        logging.dbg( "srcfile: %s" % src )
        dst = src.replace( old_path, new_path ) 
        logging.dbg( "dstfile: %s" % dst )
        # Get cache file names
        thsrc = xbmc.getCacheThumbName( src )
        thdst = xbmc.getCacheThumbName( dst )
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
        # Move files
        for i in range( len( srcfn ) ):
            try:
                shutil.move( srcfn[i], dstfn[i] )
                logging.dbg( "move %s %s" % ( srcfn[i], dstfn[i] ) )
            except IOError, e:
                logging.err( "Error moving %s %s: %s" % ( srcfn[i], dstfn[i],
                    e ) )
                pass

        # Commit Changes 
        self.db.commit()
        # Close cursor 
        c.close()

    def create_new_tvshow( self, old_idshow, old_path, new_path, c ):
        
        ## Create new record on tvshow table
        # Create query 
        query = "INSERT INTO tvshow \
                 ( c00, c01, c02, c03, c04, c05, c06, c07, c08, c09, c10, c11,\
                   c12, c13, c14, c15, c16, c17, c18, c19, c20, c21 ) \
                    SELECT c00, c01, c02, c03, c04, c05, c06, c07, c08, c09, \
                           c10, c11, c12, c13, c14, c15, c16, c17, c18, c19, \
                           c20, c21 \
                    FROM tvshow \
                    WHERE idShow = ? "
        # Create values 
        value = old_idshow,
        # Launch query 
        c.execute( query, value )
        # Get new id
        new_idshow = c.lastrowid

        ## Get old tvshow path and compute the new one
        # Create query 
        query = "SELECT p.strPath \
                 FROM   tvshowlinkpath tslp, path p \
                 WHERE  tslp.idPath = p.idPath AND tslp.idShow = ?"
        # Create values 
        value = old_idshow,
        # Launch query 
        c.execute( query, value )
        # Build result 
        old_tspath = unicode( c.fetchone()[0] )
        new_tspath = old_tspath.replace( old_path, new_path )

        ## Try to Create new path on system
        try:
            os.makedirs( new_tspath )
            logging.dbg( "Creating directory '%s'" % ( new_tspath ) )
        except OSError, e:
            if e.errno == errno.EEXIST:
                pass
            else:
                logging.dbg( "Error Creating directory '%s': %s" % (
                    new_tspath, e.strerror ) )
                return None, None

        ## Create new record on path table
        # Create query 
        query = "INSERT INTO path \
                        ( strPath, strContent, strScraper) \
                 VALUES ( ?, '', '' )"
        # Create values 
        value = new_tspath,
        # Launch query 
        c.execute( query, value )
        # Get new id
        new_tsidpath = c.lastrowid

        ## Link new tvshow id with new tvshow path 
        # Create query 
        query = "INSERT INTO tvshowlinkpath \
                        ( idShow, idPath ) \
                 VALUES ( ?, ? )"
        # Create values 
        value = new_idshow, new_tsidpath 
        # Launch query 
        c.execute( query, value )

        ## Copy thumbs
        # Get cache thumbs file names
        thsrc = xbmc.getCacheThumbName( old_tspath )
        thdst = xbmc.getCacheThumbName( new_tspath )
        srcfn = []
        dstfn = []
        # Get thumbnail fname
        srcfn.append( xbmc.translatePath( 'special://thumbnails/Video' ) 
                + "/" + thsrc[0] + "/" + thsrc )
        dstfn.append( xbmc.translatePath( 'special://thumbnails/Video' ) 
                + "/" + thdst[0] + "/" + thdst )
        # Get Fanart fname
        srcfn.append( xbmc.translatePath( 'special://thumbnails/Video' ) 
                + "/Fanart/" + thsrc )
        dstfn.append( xbmc.translatePath( 'special://thumbnails/Video' ) 
                + "/Fanart/" + thdst )
        # Copy files
        for i in range( len( srcfn ) ):
            try:
                shutil.copy( srcfn[i], dstfn[i] )
                logging.dbg( "copy %s %s" % ( srcfn[i], dstfn[i] ) )
            except IOError, e:
                logging.err( "Error copying '%s' to '%s': %s" % ( srcfn[i], 
                    dstfn[i], e ) )
                pass

        return new_tspath, new_idshow
                 


