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
from PyQt4.QtGui import QMessageBox

def iterate(publishPath):
	canvasLayers = qgis.utils.iface.mapCanvas().layers()
	ol3layers = ""
	for canvasLayer in canvasLayers:
		"""
		canvasLayer.name() is the layer name (str)
		canvasLayer.type() is 0 = vector, 1 = raster (int)
		canvasLayer.souurce() is complete source string (str)
		canvasLayer.isValid() test validity (bool)
		"""
		#ol3layers += canvasLayer.name() + "\nLayer Type: "
		#ol3layers += str(canvasLayer.type()) + "\nValid: "
		#ol3layers += str(canvasLayer.isValid()) + "\nSouurce: "
		#ol3layers += canvasLayer.source() + "\n" + "\n"
		if canvasLayer.type() == 0:
			#QMessageBox.information(qgis.utils.iface.mainWindow(),(u"Message!"), os.path.join(os.path.dirname(publishPath+"/"), '%s.json' % canvasLayer.name()))
			qgis.core.QgsVectorFileWriter.writeAsVectorFormat(canvasLayer, os.path.join(os.path.dirname(publishPath+"/"), '%s.json' % canvasLayer.name()), 'utf-8', canvasLayer.crs(), 'GeoJson') # Save layer to GeoJSON
			#qgis.core.QgsVectorFileWriter.writeAsVectorFormat(canvasLayer, os.path.join(os.path.dirname(publishPath+"/"), '%s.kml' % canvasLayer.name()), 'utf-8', canvasLayer.crs(), 'KML') # Save layer to KML - Slow!!
			canvasLayer.saveSldStyle(os.path.join(os.path.dirname(publishPath+"/"), '%s.sld' % canvasLayer.name()))
			ol3layers += u",\n new ol.layer.Vector({\n title: '%s',\n source: new ol.source.Vector({\n format: new ol.format.GeoJSON(),\n url: '%s.json'\n })\n })" % (canvasLayer.name(), canvasLayer.name())
		if canvasLayer.type() == 1:
			# WMS layer
			if canvasLayer.rasterType() == 3:
				sourceString = canvasLayer.source()
				sourceDict = dict(x.split('=') for x in sourceString.split('&'))
				ol3layers += u'\n ,\n new ol.layer.Tile({\n  title: "%s",\n source: new ol.source.TileWMS({\n  url: "%s",\n  params: { layers: "%s" }\n })\n })' % (canvasLayer.name(), sourceDict[u'url'], sourceDict[u'layers'])
				#QMessageBox.information(qgis.utils.iface.mainWindow(),(u"Message!"), sourceDict[u'url'])
	return ol3layers











