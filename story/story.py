# -*- coding: utf-8 -*-
"""
/***************************************************************************
 story
                                 A QGIS plugin
 Description story
                              -------------------
        begin                : 2016-07-23
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Klas Karlsson
        email                : klaskarlsson@hotmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt
from PyQt4.QtGui import QAction, QIcon, QMessageBox, QFileDialog
# Initialize Qt resources from file resources.py
import resources, math, httpd, os, time

# Import the code for the DockWidget
from story_dockwidget import storyDockWidget
import os.path

# Import xml stuff
import xml.etree.ElementTree as ET

# Import QGIS gui stuff
from qgis.core import QgsMessageLog, QgsPoint, QgsCoordinateTransform, QgsCoordinateReferenceSystem
#from qgis.gui import QgsMapCanvas

# Import other stuff
import shutil, webbrowser
from os import listdir
import sys

# Import layer to openlayers 3 layers...
import layer2ol3, startWebServer


class story:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'story_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Story')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'story')
        self.toolbar.setObjectName(u'story')

        #print "** INITIALIZING story"

        self.pluginIsActive = False
        self.dockwidget = None
        



    	
    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('story', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action


    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/story/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Story'),
            callback=self.run,
            parent=self.iface.mainWindow())

    #--------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        #print "** CLOSING story"

        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None

        self.pluginIsActive = False


    def unload(self):
        """Removes the plug-in menu item and icon from QGIS GUI."""

        #print "** UNLOAD story"

        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Story'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    #--------------------------------------------------------------------------
    
    """Definitions for Panel Actions
       Should have a corresponding self.dockwidget.object.event.connect(self.name) in run(self):
    """
    # Move to Next Slide
    def navigateNext(self):
    	global currentSlide, slideTitle
    	self.save_current_slide()
    	if (currentSlide < len(slideTitle) - 1):
    		currentSlide += 1
    	self.open_current_slide()
    	#QgsMessageLog.logMessage("Current slide is: %s " % (currentSlide), 'Story', QgsMessageLog.INFO)
    
    # Move to Previous Slide
    def navigatePrevious(self):
    	global currentSlide
    	self.save_current_slide()
    	if (currentSlide > 0):
    		currentSlide -= 1
    	self.open_current_slide()
    	#QgsMessageLog.logMessage("Current slide is: %s " % (currentSlide), 'Story', QgsMessageLog.INFO)
    
    # Move slide sooner - one step
    def move_sooner(self):
    	#QMessageBox.information(self.iface.mainWindow(),self.tr(u"Message!"), u"Not yet implemented!")
    	if (currentSlide > 0):
    		self.save_current_slide()
    		global currentSlide, slideTitle, slideContent, slideZoom, slidePosition
    		slideTitle[currentSlide-1],slideTitle[currentSlide] = slideTitle[currentSlide],slideTitle[currentSlide-1]
    		slideContent[currentSlide-1],slideContent[currentSlide] = slideContent[currentSlide],slideContent[currentSlide-1]
    		slideZoom[currentSlide-1],slideZoom[currentSlide] = slideZoom[currentSlide],slideZoom[currentSlide-1]
    		slidePosition[currentSlide-1],slidePosition[currentSlide] = slidePosition[currentSlide],slidePosition[currentSlide-1]
    		slideOption[currentSlide-1],slideOption[currentSlide] = slideOption[currentSlide],slideOption[currentSlide-1]
    		currentSlide -= 1
    		self.open_current_slide()
    	
    # Move slide later - one step
    def move_later(self):
    	#QMessageBox.information(self.iface.mainWindow(),self.tr(u"Message!"), u"Not yet implemented!")
    	global currentSlide, slideTitle, slideContent, slideZoom, slidePosition
    	if (currentSlide < (len(slideTitle)-1)):
    		self.save_current_slide()
    		slideTitle[currentSlide+1],slideTitle[currentSlide] = slideTitle[currentSlide],slideTitle[currentSlide+1]
    		slideContent[currentSlide+1],slideContent[currentSlide] = slideContent[currentSlide],slideContent[currentSlide+1]
    		slideZoom[currentSlide+1],slideZoom[currentSlide] = slideZoom[currentSlide],slideZoom[currentSlide+1]
    		slidePosition[currentSlide+1],slidePosition[currentSlide] = slidePosition[currentSlide],slidePosition[currentSlide+1]
    		slideOption[currentSlide+1],slideOption[currentSlide] = slideOption[currentSlide],slideOption[currentSlide+1]
    		currentSlide += 1
    		self.open_current_slide()
    
    
    # Remove current Slide
    def slide_remove(self):
    	#QMessageBox.information(self.iface.mainWindow(),self.tr(u"Message!"), u"Current Slide: %s" % (currentSlide))
    	reply = QMessageBox.question(self.iface.mainWindow(), self.tr(u'Continue?'), self.tr('Remove Current Slide?'), QMessageBox.Yes, QMessageBox.No)
    	if reply == QMessageBox.Yes:
    		global currentSlide, slideTitle, slideContent, slideZoom, slidePosition
    		del slideTitle[currentSlide]
    		del slideContent[currentSlide]
    		del slideZoom[currentSlide]
    		del slidePosition[currentSlide]
    		del slideOption[currentSlide]
    		if (currentSlide == len(slideTitle)):
    			currentSlide -= 1
    		self.open_current_slide()

    # Add Slide after current
    def slide_add(self):
    	#QMessageBox.information(self.iface.mainWindow(),self.tr(u"Message!"), self.tr(u"This is a test..."))
    	global currentSlide
    	self.save_current_slide()
    	currentSlide += 1
    	slideTitle.insert(currentSlide, self.tr(u"Slide Title"))
    	slideContent.insert(currentSlide, self.tr(u"Content"))
    	slideZoom.insert(currentSlide, self.get_current_zoom())
    	slidePosition.insert(currentSlide, self.get_current_map())
    	slideOption.insert(currentSlide, self.dockwidget.cmbSlideOption.setCurrentIndex(0))
    	self.open_current_slide()
    	#QgsMessageLog.logMessage("Current slide is: %s " % (currentSlide), 'Story', QgsMessageLog.INFO)
    
    # Set Slide Option
    def change_slide_option(self):
    	if (self.dockwidget.cmbSlideOption.currentIndex() > 0):
    		global slideOption, currentSlide
    		slideOption[currentSlide] = self.dockwidget.cmbSlideOption.currentText()
    		#QMessageBox.information(self.iface.mainWindow(),self.tr(u"Message!"), self.tr(u"Option: %s" % self.dockwidget.cmbSlideOption.currentText()))
    		
    # Changing Story Style
    def change_style(self):
    	#open story in self.dockwidget.txtStoryCSS
    	styleSource = os.path.join(os.path.dirname(os.path.realpath(__file__)),"storysource/%s" % (self.dockwidget.cmbStoryStyle.currentText()))
    	ss = open(styleSource, 'r')
    	self.dockwidget.txtStoryCSS.setPlainText(ss.read())
    		

    # Get position and zoom from map canvas center
    def get_position_from_map(self):
    	#QMessageBox.information(self.iface.mainWindow(),self.tr(u"Message!"), self.tr(u"This is a test..."))
    	self.dockwidget.txtSlidePosition.setText(self.get_current_map())
    	self.dockwidget.spinSlideZoom.setValue(int(self.get_current_zoom()))
    
    
    # Open story-file
    def select_create_file(self):
    	global currentSlide, storyFile, storyTitle, slideTitle, slideContent, slideZoom, slidePosition, slideOption
    	fileName = QFileDialog.getOpenFileName(None,self.tr(u"Open Story file"),os.path.expanduser('~'),"STORY files (*.story)")
    	if (os.path.isfile(fileName)):
    		try:
    			e = ET.parse(fileName)
    			root = e.getroot()
    			storyTitle = root.find("storyTitle").text
    			self.dockwidget.txtStoryTitle.setText(root.find("storyTitle").text)
    			self.dockwidget.txtStoryCSS.setPlainText(root.find("storyStyleEdit").text)
    			
    			titleList = list()
    			for st in root.iter("slideTitle"):
    				titleList.append(st.text)
    			slideTitle = titleList

    			contentList = list()
    			for sc in root.iter("slideContent"):
    				contentList.append(sc.text.replace("%%%","<").replace("!!!","&"))
    			slideContent = contentList

    			zoomList = list()
    			for sz in root.iter("slideZoom"):
    				zoomList.append(int(sz.text))
    			slideZoom = zoomList

    			positionList = list()
    			for sp in root.iter("slidePosition"):
    				positionList.append(sp.text)
    			slidePosition = positionList

    			optionList = list()
    			for so in root.iter("slideOption"):
    				optionList.append(so.text)
    			slideOption = optionList

    			currentSlide = 0
    			self.open_current_slide()
    			#QMessageBox.information(self.iface.mainWindow(),self.tr(u"Message!"), "This is a file")
    		except:
    			QMessageBox.warning(self.iface.mainWindow(),self.tr(u"Error!"), self.tr(u"The story file: %s\nCould not be opened!\n\n%s" % (fileName, sys.exc_info()[0])))
    			fileName = ""
    		
    	else:
    		QMessageBox.information(self.iface.mainWindow(),self.tr(u"Message!"), self.tr(u"This file does not exist!"))
    		
    	self.dockwidget.txtStoryFile.setText(fileName)
    	storyFile = fileName
    	
    # Save story-file
    def save_story(self):
    	self.save_current_slide()
    	global storyTitle, storyStyle, storyBaseMap, slideTitle, slideContent, slideZoom, slidePosition, storyFile, slideOption
    	if (storyFile == ""):
    		fileName = QFileDialog.getSaveFileName(None,self.tr(u"Save New or Replace Current StoryFile"),os.path.expanduser('~'),"STORY files (*.story)")
    		if fileName != "":
    			if not fileName.lower().endswith('.story'):
    				fileName += ".story"
    			self.dockwidget.txtStoryFile.setText(fileName)
    			storyFile = fileName
    	storyTitle = self.dockwidget.txtStoryTitle.text()
    	storyStyle = self.dockwidget.cmbStoryStyle.currentText()
    	storyTemplate = self.dockwidget.cmbStoryTemplate.currentText()
    	storyFile = self.dockwidget.txtStoryFile.text()
    	storyText = u"<?xml version=\"1.0\"?>\n"
    	storyText += u"<story>\n<storyTitle>%s</storyTitle>\n" % (storyTitle)
    	storyText += u"<storyStyle>%s</storyStyle>\n" % (storyStyle)
    	storyText += u"<storyStyleEdit>%s</storyStyleEdit>\n" % (self.dockwidget.txtStoryCSS.toPlainText())
    	storyText += u"<storyTemplate>%s</storyTemplate>\n" % (storyTemplate)
    	storyText += u"<slides>\n"
    	for x in range(0, len(slideTitle)):
    		storyText += u"<slide id=\"%s\">\n" % (x)
    		storyText += u"<slideTitle>%s</slideTitle>\n" % (slideTitle[x])
    		storyText += u"<slideOption>%s</slideOption>\n" % (slideOption[x])
    		storyText += u"<slideContent>%s</slideContent>\n" % (slideContent[x].replace("<","%%%").replace("&","!!!"))
    		storyText += u"<slideZoom>%s</slideZoom>\n" % (slideZoom[x])
    		storyText += u"<slidePosition>%s</slidePosition>\n" % (slidePosition[x])
    		storyText += u"</slide>\n"
    	storyText += u"</slides>\n"
    	storyText += u"<storyFile>%s</storyFile>\n</story>" % (storyFile)
    	if (storyFile != ""):
    		f = open(storyFile,'w')
    		f.write(storyText.encode('utf-8'))
    		f.close()
    	
    # Render story to HTML/JS
    def create_story(self):
    	self.save_current_slide()
    	global storyTitle, slideTitle, slideContent, slideZoom, slidePosition, publishPath
    	if (len(self.dockwidget.txtStoryCSS.toPlainText()) < 200):
    		self.change_style()
    	storyFolder = QFileDialog.getExistingDirectory(None,self.tr(u"Select folder to generate story"),publishPath)
    	if (storyFolder != ""):
    		publishPath = storyFolder
    		storyTitle = self.dockwidget.txtStoryTitle.text()
    		qgisLayers = layer2ol3.iterate(u"%s" % storyFolder)
    		sf = open( os.path.join(os.path.dirname(os.path.realpath(__file__)),"storysource/%s" % (self.dockwidget.cmbStoryTemplate.currentText())), 'r')
    		storyHtml = sf.read()
    		storyHtml = storyHtml.replace("{{storyTitle}}", storyTitle)
    		storyHtml = storyHtml.replace("{{qgisLayers}}", qgisLayers)
    		slideDivs = ""
    		slideList = ""
    		zoomList = ""
    		positionList = ""
    		for x in range(0, len(slideTitle)):
    			slideDivs += "<div id=\"id%s\" class=\"slide %s\"><h1>%s</h1><p>%s</p></div>\n" % (x, slideOption[x], slideTitle[x], slideContent[x])
    			slideList += "\"id%s\"," % (x)
    			zoomList += "%s," % (slideZoom[x])
    			positionList += "[%s]," % (slidePosition[x])
    		storyHtml = storyHtml.replace("{{startPosition}}", "[%s]" % (slidePosition[0]))
    		storyHtml = storyHtml.replace("{{startZoom}}", str(slideZoom[0]))
    		storyHtml = storyHtml.replace("{{slideDivs}}", slideDivs)
    		storyHtml = storyHtml.replace("{{slideList}}", slideList[:-1])
    		storyHtml = storyHtml.replace("{{zoomList}}", zoomList[:-1])
    		storyHtml = storyHtml.replace("{{positionList}}", positionList[:-1])
    	
    		#QMessageBox.information(self.iface.mainWindow(),self.tr(u"Message!"), sourceHtml)
    		f = open( os.path.join(storyFolder, "index.htm"), 'w' )
    		f.write(storyHtml.encode('utf-8'))
    		f.close()
    		styleSource = self.dockwidget.txtStoryCSS.toPlainText()
    		#styleSource = os.path.join(os.path.dirname(os.path.realpath(__file__)),"storysource/%s" % (self.dockwidget.cmbStoryStyle.currentText()))
    		styleDestination = os.path.join(storyFolder, "story.css")
    		s = open( styleDestination, 'w')
    		s.write(styleSource.encode('utf-8'))
    		s.close()
    		#shutil.copy(styleSource, styleDestination)
    		#startWebServer.stopServer()
    		#startWebServer.infolder(storyFolder)
                os.chdir(storyFolder)
                srv = httpd.TinyWebServer()
                srv.create("localhost", 8080)
                srv.start()
    		webbrowser.open("http://localhost:8080")
    		#time.sleep(60)
                wait_to_stop = QMessageBox.question(self.iface.mainWindow(), self.tr(u'Continue?'), self.tr('Press OK to stop Story Server.'), QMessageBox.Ok)
                if wait_to_stop == QMessageBox.Ok:
                	srv.stop()
                #webbrowser.open(os.path.join(storyFolder, "index.htm"))
     		#QMessageBox.information(self.iface.mainWindow(),self.tr(u"Message!"), self.tr(u"Number of Slides: %s" % (len(slideTitle)))
    	
    # Store current slide form to variable
    def save_current_slide(self):
    	global currentSlide, slideTitle, slideContent, slideZoom, slidePosition, slideOption
    	#QgsMessageLog.logMessage("Count: %s Current Index: %s " % (len(slideTitle), currentSlide), 'Story', QgsMessageLog.INFO)
    	slideTitle[currentSlide] = self.dockwidget.txtSlideTitle.text()
    	slideContent[currentSlide] = self.dockwidget.txtSlideContent.toPlainText()
    	slideZoom[currentSlide] = self.dockwidget.spinSlideZoom.value()
    	slidePosition[currentSlide] = self.dockwidget.txtSlidePosition.text()
    	slideOption[currentSlide] = self.dockwidget.cmbSlideOption.currentText()
    	
    # Open current slide variables in slide form
    def open_current_slide(self):
    	global currentSlide, slideTitle, slideContent, slideZoom, slidePosition, slideOption
    	#QgsMessageLog.logMessage("Count: %s Current Index: %s " % (len(slideTitle), currentSlide), 'Story', QgsMessageLog.INFO)
    	self.dockwidget.txtSlideTitle.setText(slideTitle[currentSlide])
    	self.dockwidget.txtSlideContent.setPlainText(slideContent[currentSlide])
    	self.dockwidget.spinSlideZoom.setValue(int(slideZoom[currentSlide]))
    	self.dockwidget.txtSlidePosition.setText(slidePosition[currentSlide])
    	optIndex = self.dockwidget.cmbSlideOption.findText(slideOption[currentSlide], Qt.MatchFixedString)
    	if optIndex >= 0:
    		self.dockwidget.cmbSlideOption.setCurrentIndex(optIndex)
    	#QgsMessageLog.logMessage("Current slide title: %s " % (slideTitle[currentSlide]), 'Story', QgsMessageLog.INFO)
    	#QgsMessageLog.logMessage("Current slide content: %s " % (slideContent[currentSlide]), 'Story', QgsMessageLog.INFO)
    	self.dockwidget.lblSlideNumber.setText(self.tr('Slide %s/%s') % (currentSlide + 1, len(slideTitle)))
    	self.pan_zoom_current()
    	
    # Function to get and transform canvas center to Lon/Lat - return QgsPoint
    def get_current_map(self):
    	curX = self.iface.mapCanvas().extent().center().x()
    	curY = self.iface.mapCanvas().extent().center().y()
    	EPSG = self.iface.mapCanvas().mapRenderer().destinationCrs().authid().split(":")[1]
    	transf = QgsCoordinateTransform( QgsCoordinateReferenceSystem(int(EPSG)), QgsCoordinateReferenceSystem(4326) )
    	centerPoint = transf.transform(QgsPoint(curX, curY))
    	centerCoordinate = str(centerPoint.x()) + "," + str(centerPoint.y())
    	return centerCoordinate
    	
    # Get canvas scale and transform to zoom approximation
    def get_current_zoom(self):
    	mapZoomLevel = int(math.log(591657550.500000 /self.iface.mapCanvas().scale(),2))
    	return mapZoomLevel
    	
    # Pan and zoom canvas to current slide settings
    def pan_zoom_current(self):
    	global currentSlide, slideZoom, slidePosition
    	#QgsMessageLog.logMessage("Current position: %s " % (slidePosition[currentSlide]), 'Story', QgsMessageLog.INFO)
    	mapScale = 591657550.500000 / (math.pow(2,slideZoom[currentSlide]))
    	coord = slidePosition[currentSlide].split(",")
    	latlonPoint = QgsPoint(float(coord[0]),float(coord[1]))
    	EPSG = self.iface.mapCanvas().mapRenderer().destinationCrs().authid().split(":")[1]
    	transf = QgsCoordinateTransform( QgsCoordinateReferenceSystem(4326), QgsCoordinateReferenceSystem(int(EPSG)) )
    	mapCenter = transf.transform(latlonPoint)
    	self.iface.mapCanvas().zoomScale(mapScale)
    	self.iface.mapCanvas().setCenter(mapCenter)
    	self.iface.mapCanvas().refresh()
    	
    # Clear field and variable for storyFile
    def clear_story_file(self):
    	global storyFile
    	storyFile = ""
    	self.dockwidget.txtStoryFile.setText("")
    	
    # Populate Templates and Styles with htm and css files from storysource folder
    def read_templates_and_styles(self):
    	global storyTemplate, storyStyle
    	sourcefiles = sorted([f for f in listdir(os.path.join(os.path.dirname(os.path.realpath(__file__)),"storysource")) if os.path.isfile(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)),"storysource"), f))])
    	for sourcefile in sourcefiles:
    		if sourcefile.lower().endswith('.htm'):
    			#QgsMessageLog.logMessage(sourcefile, 'Story', QgsMessageLog.INFO)
    			self.dockwidget.cmbStoryTemplate.addItem(sourcefile)
    		if sourcefile.lower().endswith('.css'):
    			#QgsMessageLog.logMessage(sourcefile, 'Story', QgsMessageLog.INFO)
    			self.dockwidget.cmbStoryStyle.addItem(sourcefile)
    			
    # Clear and Reset Story
    def story_clear(self):
    	# If you are sure?
    	reply = QMessageBox.question(self.iface.mainWindow(), self.tr(u'Continue?'), self.tr('Reset Story Completely?'), QMessageBox.Yes, QMessageBox.No)
    	if reply == QMessageBox.Yes:
    		global currentSlide, slideTitle, slideOption, slideContent, slidePosition, slideZoom, storyTitle
    		del slideTitle[:]
    		#del slideOption[:]
    		del slideContent[:]
    		del slidePosition[:]
    		del slideZoom[:]
    		self.dockwidget.cmbSlideOption.setCurrentIndex(0)
    		slideOption[0] = self.dockwidget.cmbSlideOption.currentText()
    		publishPath = os.path.expanduser('~')
    		self.dockwidget.txtStoryTitle.setText(self.tr("The main Story Title"))
    		self.clear_story_file()
    		currentSlide = 0
    		storyTitle = ""
    		slideTitle.insert(currentSlide, self.tr("Slide Title"))
    		slideContent.insert(currentSlide, self.tr("Content"))
    		slideZoom.insert(currentSlide, self.get_current_zoom())
    		slidePosition.insert(currentSlide, self.get_current_map())
    		self.open_current_slide()
    		
    
    #--------------------------------------------------------------------------
    def run(self):
        """Run method that loads and starts the plugin"""
        if not self.pluginIsActive:
            self.pluginIsActive = True

            #print "** STARTING story"

            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.dockwidget == None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = storyDockWidget()

            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            # show the dockwidget
            # TODO: fix to allow choice of dock location
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)
            self.dockwidget.show()
            
            # Variables for story content
            global publishPath
            publishPath = os.path.expanduser('~')
            global currentSlide
            currentSlide = 0
            global storyTitle
            self.dockwidget.txtStoryTitle.setText(self.tr("The main Story Title"))
            global storyStyle
            global storyTemplate
            global slideTitle
            slideTitle = list("")
            global slideOption
            slideOption = list("")
            global slideContent
            slideContent = list("")
            global slideZoom
            slideZoom = list("")
            global slidePosition
            slidePosition = list("")
            global storyFile
            storyFile = ""
            slideTitle.insert(currentSlide, self.tr("Slide Title"))
            slideContent.insert(currentSlide, self.tr("Content"))
            slideOption.insert(currentSlide, self.dockwidget.cmbSlideOption.currentText())
            slideZoom.insert(currentSlide, self.get_current_zoom())
            slidePosition.insert(currentSlide, self.get_current_map())
            self.open_current_slide()
            #QgsMessageLog.logMessage("current slide option: %s" % (self.dockwidget.cmbSlideOption.currentText()), 'Story', QgsMessageLog.INFO)
            
            self.read_templates_and_styles()
            
            """ Catchers for panel button clicks
            each catch must have corresponding def name():
            """
            self.dockwidget.btnStoryReset.clicked.connect(self.story_clear)
            self.dockwidget.btnPreviousSlide.clicked.connect(self.navigatePrevious)
            self.dockwidget.btnNextSlide.clicked.connect(self.navigateNext)
            self.dockwidget.btnRemoveSlide.clicked.connect(self.slide_remove)
            self.dockwidget.btnAddSlide.clicked.connect(self.slide_add)
            self.dockwidget.btnGetSlidePositionFromMap.clicked.connect(self.get_position_from_map)
            self.dockwidget.btnFindFile.clicked.connect(self.select_create_file)
            self.dockwidget.btnSaveStory.clicked.connect(self.save_story)
            self.dockwidget.btnCreateStory.clicked.connect(self.create_story)
            self.dockwidget.btnMoveLater.clicked.connect(self.move_later)
            self.dockwidget.btnMoveSooner.clicked.connect(self.move_sooner)
            self.dockwidget.btnClearFile.clicked.connect(self.clear_story_file)
            self.dockwidget.cmbSlideOption.activated.connect(self.change_slide_option)
            self.dockwidget.cmbStoryStyle.activated.connect(self.change_style)
            
            #QMessageBox.information(self.iface.mainWindow(),self.tr(u"Message!"), layer2ol3.iterate(u"%s" % publishPath))

