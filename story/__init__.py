# -*- coding: utf-8 -*-
"""
/***************************************************************************
 story
                                 A QGIS plugin
 Description story
                             -------------------
        begin                : 2016-07-23
        copyright            : (C) 2016 by Klas Karlsson
        email                : klaskarlsson@hotmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load story class from file story.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .story import story
    return story(iface)
