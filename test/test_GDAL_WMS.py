# gdalinfo "WMS:http://noisy.hq.isogeo.fr:6090/geoserver/wms?request=GetCapabilities&service=WMS&version=1.0.0"
# gdalinfo "WMS:http://demo.opengeo.org/geoserver/wms?request=GetCapabilities&service=WMS&version=1.0.0"

import gdal

wms = "http://noisy.hq.isogeo.fr:6090/geoserver/wms?request=GetCapabilities&service=WMS&version=1.0.0"
flux = gdal.Open(wms)

subdatasets = flux.GetMetadata("SUBDATASETS")
