# Project Scheherazade
## AKA - QGIS Story
This is a QGIS plug-in that makes it possible to create web based geographic map stories. The stories requires only a web browser to view and an Internet connection.

Stories are created directly from a QGIS dockable panel and simple forms. Storys can be saved, edited, published and more. Storys are based on OpenLayers3 and supported active layers in the current project.

- WMS (yes most WMS are supported)
- Raster Layers (only png and jpg formats supported by web browser)
- Vector Layers (any and all active vector layers are exported as GeoJSON - **Warning**)

**Note that web sources like WMS are not copied to the publish folder, but raster and vector layers are!**

The story is styled with selectable, and customisable css templates, and based on a html template, that it self is also customisable.
### Project Status
This is **not** production ready!!!

It might be Beta, soon...

To try, you can grab the zip and un-pack into your QGIS plugins folder.
