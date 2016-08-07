# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Convert Canvas layers to OpenLayers 3 layer string
 
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

import qgis.core, os.path
from qgis.core import QgsPoint, QgsCoordinateTransform, QgsCoordinateReferenceSystem
from PyQt4.QtGui import QMessageBox
from shutil import copy2

def iterate(publishPath):
	canvasLayers = qgis.utils.iface.mapCanvas().layers()
	ol3layers = ""
	for canvasLayer in reversed(canvasLayers):
		
		# DO if layer is Vector
		if canvasLayer.type() == 0:
			qgis.core.QgsVectorFileWriter.writeAsVectorFormat(canvasLayer, os.path.join(os.path.dirname(publishPath+"/"), '%s.json' % canvasLayer.name()), 'utf-8', canvasLayer.crs(), 'GeoJson') # Save layer to GeoJSON
			
			# SLD style is not implemented in Open Layers 3 so sld file is not used
			# canvasLayer.saveSldStyle(os.path.join(os.path.dirname(publishPath+"/"), '%s.sld' % canvasLayer.name()))
			
			ol3layers += u",\n new ol.layer.Vector({\n title: '%s',\n source: new ol.source.Vector({\n format: new ol.format.GeoJSON(),\n url: '%s.json'\n })\n })" % (canvasLayer.name(), canvasLayer.name())

		# DO if layer is raster (file or WMS)
		if canvasLayer.type() == 1:
			
			# WMS layer
			if canvasLayer.rasterType() == 3:
				sourceString = canvasLayer.source()
				sourceDict = dict(x.split('=') for x in sourceString.split('&'))
				ol3layers += u'\n ,\n new ol.layer.Tile({\n  title: "%s",\n source: new ol.source.TileWMS({\n  url: "%s",\n  params: { layers: "%s" }\n })\n })' % (canvasLayer.name(), sourceDict[u'url'], sourceDict[u'layers'])

			# Image layer (only supported formats work in browser i.e. GeoTiff doesn't work!)
			if canvasLayer.rasterType() < 3:
				sourceString = canvasLayer.source()
				approvedFormat = (".png", ".jpg") # only accept jpg and png files!
				if sourceString.lower().endswith(approvedFormat):
					# Copy rasterfile to publish directory
					destinationFileName = canvasLayer.name() + sourceString[-4:]
					copy2(sourceString, os.path.join(os.path.dirname(publishPath+"/"), destinationFileName )) 
					layerCrs = canvasLayer.crs().authid().split(":")[1]
					transf = QgsCoordinateTransform( QgsCoordinateReferenceSystem(int(layerCrs)), QgsCoordinateReferenceSystem(4326) )
					minX = canvasLayer.extent().xMinimum()
					minY = canvasLayer.extent().yMinimum()
					pointLL = transf.transform(QgsPoint(minX, minY))
					maxX = canvasLayer.extent().xMaximum()
					maxY = canvasLayer.extent().yMaximum()
					pointUR = transf.transform(QgsPoint(maxX, maxY))
					layerExtent = str(pointLL.x())+","+str(pointLL.y())+","+str(pointUR.x())+","+str(pointUR.y())
					layerSize = str(canvasLayer.width()) +","+ str(canvasLayer.height())
					ol3layers += u',\n new ol.layer.Image({\n  source: new ol.source.ImageStatic({\n  url: "%s",\n  imageExtent: ol.extent.applyTransform([%s], ol.proj.getTransform("EPSG:4326", "EPSG:3857"))\n })})' % (destinationFileName, layerExtent)
					#QMessageBox.information(qgis.utils.iface.mainWindow(),(u"Message!"), sourceDict[u'url'])
	return ol3layers





