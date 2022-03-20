# script to copy first 10 points in a shapefile
# import modules, set the working directory, and get the driver
import ogr, os, sys
os.chdir(r'U:/RS_Task_Workspaces/bobo/ZAMA/_ALOS2_Report_2022/vectors')
driver = ogr.GetDriverByName('ESRI Shapefile')
# open the input data source and get the layer
polygon_fn = 'F20_2018_total_ground_truth_adds_SelPolygon.shp'

out_path = r'U:/RS_Task_Workspaces/bobo/ZAMA/_ALOS2_Report_2022/img_out'
source_ds  = driver.Open(polygon_fn , 0)
if source_ds  is None:
    print ('Could not open file')
    sys.exit(1)
source_layer = source_ds.GetLayer()
x_min, x_max, y_min, y_max = source_layer.GetExtent()
#**************************************************
# numFeatures = inLayer.GetFeatureCount()
# print ('Feature count: ' + str(numFeatures))
# print ('Feature count:', numFeatures)
# feature0 = inLayer.GetFeature(0)
# geometry = feature0.GetGeometryRef()
# x = geometry.GetX()
# # y = geometry.GetY()
# # print(x,y)
# # feature0.Destroy() #destroy feature
# # inDS.Destroy()   #destroy dataset
# #*****************************************************
# # create a new data source and layer
# if os.path.exists('test.shp'):
#     driver.DeleteDataSource('test.shp')
# outDS = driver.CreateDataSource('test.shp')
# if outDS is None:
#     print ('Could not create file')
#     sys.exit(1)
# # create a new data  layer
# outLayer = outDS.CreateLayer('test', geom_type=ogr.wkbPoint)
# # use the input FieldDefn to add a field to the output
# fieldDefn = inLayer.GetFeature(0).GetFieldDefnRef('id')
# outLayer.CreateField(fieldDefn)
# # get the FeatureDefn for the output layer
# featureDefn = outLayer.GetLayerDefn()
# # loop through the input features
# cnt = 0
# inFeature = inLayer.GetNextFeature()
# while inFeature:
#     # create a new feature
#     outFeature = ogr.Feature(featureDefn)
#     outFeature.SetGeometry(inFeature.GetGeometryRef())
#     outFeature.SetField('id', inFeature.GetField('id'))
#     # add the feature to the output layer
#
#     outLayer.CreateFeature(outFeature)
#     # destroy the features
#     inFeature.Destroy()
#     outFeature.Destroy()
#     # increment cnt and if we have to do more then keep looping
#     cnt = cnt + 1
#     if cnt < 10: inFeature = inLayer.GetNextFeature()
#     else: break
# # close the data sources
# inDS.Destroy()
# outDS.Destroy()
#****************************************************
''' this skript read shapefile, then create raster for the same extent
    -then burn shapefile value into a raster
    -then read raster into an array
    -then for each pixel with value > 0 creates a point.
    -finally those points are saved into another shapefile
    -side product is rasterdized shapefile.
    -it is missing projection information and ability to burn various shape values'''

#*************************************
import  gdal
import numpy as np
# Define pixel_size which equals distance betweens points
pixel_size = 20

# Create the destination data source
x_res = int((x_max - x_min) / pixel_size)
y_res = int((y_max - y_min) / pixel_size)
target_ds = gdal.GetDriverByName('GTiff').Create(os.path.join(out_path,'F20trainPoly_rast20_adds_SelPolygon.tif'), x_res, y_res, gdal.GDT_Byte)
target_ds.SetGeoTransform((x_min, pixel_size, 0, y_max, 0, -pixel_size))
band = target_ds.GetRasterBand(1)
band.SetNoDataValue(255)
# Rasterize
gdal.RasterizeLayer(target_ds, [1], source_layer, burn_values=[1])
# Read as array
array = band.ReadAsArray()
raster = gdal.Open(os.path.join(out_path,'F20trainPoly_rast20_adds_SelPolygon.tif'))
geotransform = raster.GetGeoTransform()
# Convert array to point coordinates
count = 0
roadList = np.where(array == 1)
multipoint = ogr.Geometry(ogr.wkbMultiPoint)
for indexY in roadList[0]:
    indexX = roadList[1][count]
    geotransform = raster.GetGeoTransform()
    originX = geotransform[0]
    originY = geotransform[3]
    pixelWidth = geotransform[1]
    pixelHeight = geotransform[5]
    Xcoord = originX+pixelWidth*indexX
    Ycoord = originY+pixelHeight*indexY
    point = ogr.Geometry(ogr.wkbPoint)
    point.AddPoint(Xcoord, Ycoord)
    multipoint.AddGeometry(point)
    count += 1

# Write point coordinates to Shapefile
shpDriver = ogr.GetDriverByName("ESRI Shapefile")
if os.path.exists('F20_Reg_points_adds_20m.shp'):
    shpDriver.DeleteDataSource('F20_Reg_points_adds_20m.shp')
outDataSource = shpDriver.CreateDataSource('F20_Reg_points_adds_20m.shp')
outLayer = outDataSource.CreateLayer('F20_Reg_points_adds_20m.shp', geom_type=ogr.wkbMultiPoint)
featureDefn = outLayer.GetLayerDefn()
outFeature = ogr.Feature(featureDefn)
outFeature.SetGeometry(multipoint)
outLayer.CreateFeature(outFeature)
outFeature = None

# # Remove temporary files
# os.remove('trainPoly_rast20.tif')
