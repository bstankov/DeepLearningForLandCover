'''
generatePnt_2.py
the scripts reead a raster's extent
-
 -then create output shp file
 then reads another shape with some regular points coming from training site polygons
 -each point lat and long is stored into outpu shp file
 -in addition at each point location we extract
 values for each band and store into shp file
 -at the end we have input bands and label values for each point '''
import numpy as np
import random
import gdal
import sys,os
try:
    from osgeo import ogr, osr, gdal
except:
    sys.exit('ERROR: cannot find GDAL/OGR modules')
from shapely.geometry import Polygon, Point
version_num = int(gdal.VersionInfo('VERSION_NUM'))
from osgeo import osr,ogr
if version_num < 1100000:
    sys.exit('ERROR: Python bindings of GDAL 1.10 or later required')
#
# src_ds = gdal.Open( r"U:\RS_Task_Workspaces\bobo\ZAMA\L7_45-19_20200822_sub.tif" )
# if src_ds is None:
#     print ('Unable to open INPUT.tif')
#     sys.exit(1)
#
# print ("[ RASTER BAND COUNT ]: ", src_ds.RasterCount)
# for band in range( src_ds.RasterCount ):
#     band += 1
#     print( "[ GETTING BAND ]: ", band)
#     srcband = src_ds.GetRasterBand(band)
#     if srcband is None:
#         continue
#
#     stats = srcband.GetStatistics( True, True )
#     if stats is None:
#         continue
#
#     print ("[ STATS ] =  Minimum=%.3f, Maximum=%.3f, Mean=%.3f, StdDev=%.3f" % ( \
#                 stats[0], stats[1], stats[2], stats[3] ))
# poly = Polygon([ (-120, 59),(-118, 60)])
import shapely.wkt

from shapely.geometry import Point, Polygon
from shapely import speedups
import osgeo.ogr, osgeo.osr
#open an image and get info ......
gdal.UseExceptions()
os.chdir(r'U:\RS_Task_Workspaces\bobo\ZAMA\_ALOS2_Report_2022\input')
# img = r'U:\RS_Task_Workspaces\bobo\ZAMA\F20mos_20m_train32611.tif'
#img =r'U:\RS_Task_Workspaces\bobo\ZAMA\input\North_SW_ground_mosaic_20200808_adds.tif'
img = 	r'U:\RS_Task_Workspaces\bobo\ZAMA\_ALOS2_Report_2022\input\stack_S2_Ph_alp_32611_20mClipPolygon.tif'

#the image includes 10 Sent 2 bands plus one band indicating training polygons
ds = gdal.Open(img)
proj = ds.GetProjection()
print("proj:",proj)

raster_wkt = ds.GetProjection()
spatial_ref = osr.SpatialReference()
spatial_ref.ImportFromWkt(raster_wkt)
print("prj sr:", spatial_ref.ExportToPrettyWkt())

print('File list:', ds.GetFileList())

rows = ds.RasterYSize
cols = ds.RasterXSize
print('cols:', cols, 'rows',rows)

gt = ds.GetGeoTransform() # captures origin and pixel size
xOrigin = gt[0]
yOrigin = gt[3]
pixelWidth =gt[1]
pixelHeight =gt[5]
ul = gdal.ApplyGeoTransform(gt,0,0)
ur = gdal.ApplyGeoTransform(gt,ds.RasterXSize,0)
ll =  gdal.ApplyGeoTransform(gt,0,ds.RasterYSize)
lr = gdal.ApplyGeoTransform(gt,ds.RasterXSize,ds.RasterYSize)
cent = gdal.ApplyGeoTransform(gt,ds.RasterXSize/2,ds.RasterYSize/2)
print('Upper Left Corner:', ul,'Upper Right Corner:',ur,'Lower Left Corner:',ll,'Lower Right Corner:',lr )
print('Image Structure Metadata:', ds.GetMetadata('IMAGE_STRUCTURE'))

numOfbands =  ds.RasterCount
print("bands",numOfbands)
# proj1 = osr.SpatialReference(wkt=ds.GetProjection())
#epsg = spatial_ref.ExportToPrettyWkt().GetAttrValue('AUTHORITY',1)
epsg = spatial_ref.GetAttrValue('AUTHORITY',1)
print("epsg:",epsg)
#put bands into a list
bandList = []
# read in bands and store all the data in bandList
for i in range(numOfbands):
    band = ds.GetRasterBand(i+1)
    data = band.ReadAsArray(0, 0, cols, rows)
    bandList.append(data)
print("bnd list:",len(bandList))
    #************************************************
speedups.disable()
# Create a Polygon
# coords = [(-120, 60), (-120,59.5), (-118,59.5), (-118,60)]
coords2 = [(ul), (ll), (lr), (ur)]
# poly = Polygon(coords)
poly2 = Polygon(coords2)
# print(poly)
print(poly2)

#*************REad input ranodm points shapefile.........
#this shp file was created using play_vec.py
# regular_pnts =r'U:\RS_Task_Workspaces\bobo\ZAMA\vectors\trainPolypoints20_32611.shp'
regular_pnts =r'U:\RS_Task_Workspaces\bobo\ZAMA\_ALOS2_Report_2022\vectors\F20_Reg_points_adds_20m32611.shp'

drv =ogr.GetDriverByName('ESRI Shapefile')
indataSet = drv.Open(regular_pnts)
inlayer = indataSet.GetLayer()
n_feat = 0
coor_x = []
coor_y = []
for feat in inlayer:
    # print (feat.GetField('FID'))
    multipoint = feat.GetGeometryRef()

    for i in range(multipoint.GetGeometryCount()):
        point = multipoint.GetGeometryRef(i)  # <--- Get the geom at index i
        mx, my = point.GetX(), point.GetY()
        # print("my:", mx, my)
        coor_x.append((mx))
        coor_y.append(my)
print("corx",coor_x)
print("cory",coor_y)

layerDefinition = inlayer.GetLayerDefn()
for i in range(layerDefinition.GetFieldCount()):
    print("layers:",layerDefinition.GetFieldDefn(i).GetName())  #no fields
featureCount = inlayer.GetFeatureCount()
print ("Number of features in %s: %d" % (os.path.basename(regular_pnts),featureCount))

#proces of creating of  an output shapefile
driver = ogr.GetDriverByName("ESRI Shapefile")
# will create a spatial reference locally to tell the system what the reference will be
spatialReference = osgeo.osr.SpatialReference()
# here we define this reference to be the EPSG code
spatialReference.ImportFromEPSG(int(epsg))
# will select the driver for our shp-file creation.
# driver = osgeo.ogr.GetDriverByName('ESRI Shapefile')
# so there we will store our data
ds = driver.CreateDataSource('F20_correct_4_DL_13March.shp') #create data source
if ds is None:
    print ('Could not create file')
    sys.exit(1)
# this will create a corresponding layer for our data with given spatial information.
outlayer = ds.CreateLayer('F20_correct_4_DL_13March',spatialReference, geom_type=ogr.wkbPoint)
# gets parameters of the current shapefile
# add fields to the output
# layer_defn = outlayer.GetLayerDefn()
field_id = ogr.FieldDefn('id', ogr.OFTString)
field_id.SetWidth(6)
outlayer.CreateField(field_id)
#
field_b2 = ogr.FieldDefn('B2', ogr.OFTInteger)
field_b2.SetWidth(6)
outlayer.CreateField(field_b2)
#
field_b3 = ogr.FieldDefn('B3', ogr.OFTInteger)
field_b3.SetWidth(6)
outlayer.CreateField(field_b3)

field_b4 = ogr.FieldDefn('B4', ogr.OFTInteger)
field_b4.SetWidth(6)
outlayer.CreateField(field_b4)

field_b5 = ogr.FieldDefn('B5', ogr.OFTInteger)
field_b5.SetWidth(6)
outlayer.CreateField(field_b5)

field_b6 = ogr.FieldDefn('B6', ogr.OFTInteger)
field_b6.SetWidth(6)
outlayer.CreateField(field_b6)

field_b7 = ogr.FieldDefn('B7', ogr.OFTInteger)
field_b7.SetWidth(6)
outlayer.CreateField(field_b7)

field_b8 = ogr.FieldDefn('B8', ogr.OFTInteger)
field_b8.SetWidth(6)
outlayer.CreateField(field_b8)

field_b8A = ogr.FieldDefn('B8A', ogr.OFTInteger)
field_b8A.SetWidth(6)
outlayer.CreateField(field_b8A)

field_b11 = ogr.FieldDefn('B11', ogr.OFTInteger)
field_b11.SetWidth(6)
outlayer.CreateField(field_b11)

field_b12 = ogr.FieldDefn('B12', ogr.OFTInteger)
field_b12.SetWidth(6)
outlayer.CreateField(field_b12)

field_b13 = ogr.FieldDefn('Phi', ogr.OFTReal)
field_b12.SetWidth(10)
outlayer.CreateField(field_b13)

field_b14 = ogr.FieldDefn('Alpha', ogr.OFTReal)
field_b14.SetWidth(10)
outlayer.CreateField(field_b14)

field_b15 = ogr.FieldDefn('ASLC', ogr.OFTInteger)
field_b15.SetWidth(6)
outlayer.CreateField(field_b15)


outlayer.CreateField(ogr.FieldDefn("Latitude", ogr.OFTReal))
outlayer.CreateField(ogr.FieldDefn("Longitude", ogr.OFTReal))
#read image values for each band at coordinate locations....
for r in range(len(coor_x)):
    feature = ogr.Feature(outlayer.GetLayerDefn())  # create a feature
    feature.SetField('id', str(r+1)) #set attributes
    # Set the attributes using the values from
    # compute pixel offset
    xOffset = int((coor_x[r] - xOrigin) / pixelWidth)
    yOffset = int((coor_y[r] - yOrigin) / pixelHeight)
    print("xofset_Yofset:", xOffset , xOffset )
    s = str(coor_x[r]) + ' ' + str(coor_y[r]) + ' ' + str(xOffset) + ' ' + str(yOffset) + ' '
    S2_list = []
    for j in range(13):
        # read data and add the value to the string
        data = bandList[j]
        value = data[yOffset, xOffset]  # math matrix notation order
        #print("value:",value)
        pyval = value.item()  #convert np.uint16 to integer*******************************old
        #pyval = value  #change
        # print("valuetype:",type(type(pyval)), pyval)
        #S2_list.append(int(pyval)) #**********old
        S2_list.append(pyval)  #change
        s = s + str(value) + ' '
    print("s:",s)
    #populate rest of the fields.
    print("Phi<ALPH:", S2_list[10], S2_list[11])

    #*******************    SHIFTED ROWS TO FIX
    feature.SetField('B2', S2_list[0])
    feature.SetField('B3', (S2_list[1]))
    feature.SetField('B4', (S2_list[2]))
    feature.SetField('B5', (S2_list[3]))
    feature.SetField('B6', (S2_list[4]))
    feature.SetField('B7', (S2_list[5]))
    feature.SetField('B8', (S2_list[6]))
    feature.SetField('B8A', (S2_list[7]))
    feature.SetField('B11', (S2_list[8]))
    feature.SetField('B12', (S2_list[9]))
    feature.SetField('Phi', (S2_list[10]))  #float
    feature.SetField('Alpha', float(S2_list[11])) #
    feature.SetField('ASLC', int(S2_list[12]))

    S2_list.clear()
    feature.SetField("Latitude", coor_x[r])
    feature.SetField("Longitude", coor_y[r])
    # create the WKT for the feature using Python string formatting
    wkt = "POINT(%f %f)" % (float(coor_x[r]), float(coor_y[r]))

    # Create the point from the Well Known Txt
    point = ogr.CreateGeometryFromWkt(wkt)
    feature.SetGeometry(point)  #set the feature geometry using a point
    outlayer.CreateFeature(feature) #create a feature in the layer (shapefile)
    feature.Destroy()
    # i=i+1
ds.Destroy()
indataSet.Destroy()
