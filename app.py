#! /usr/bin/env python2
import time
import ee
from flask import Flask, render_template, request

def maskS2clouds(image):
    qa = image.select('QA60')
    cloudBitMask = ee.Number(2).pow(10).int()
    cirrusBitMask = ee.Number(2).pow(11).int()
    mask = qa.bitwiseAnd(cloudBitMask).eq(0).And(qa.bitwiseAnd(cirrusBitMask).eq(0))
    return image.updateMask(mask).divide(10000)

glbls = {'dataTypeSelect':'NDVI',
         'startdate':'2016-04-01',
         'enddate':'2016-09-01',
         'minLat':-11.1,'maxLat':-10.9,'minLon':-76.2,'maxLon':-76.0}

ee.data.setDeadline(200000) 
local = False
# 1._ GEE connection

if local:
    ee.Initialize()
    msg = 'Choose a rectangular region'
    output = 'output.html'
else:
# for appengine deployment or development appserver
    import cnfg
    msg = 'Choose a SMALL rectangular region'
    ee.Initialize(cnfg.EE_CREDENTIALS, 'https://earthengine.googleapis.com')
    output = 'output.html'

app = Flask(__name__)

@app.route('/', methods = ['GET', 'POST'])
def index():
    global glbls, local
    if request.method == 'GET':
        return render_template('index.html',
                                dataTypeSelect = glbls['dataTypeSelect'],
                                startdate = glbls['startdate'],
                                enddate = glbls['enddate'],
                                minLon = glbls['minLon'],
                                minLat = glbls['minLat'],
                                maxLat = glbls['maxLat'],
                                maxLon = glbls['maxLon'])
    else:
        try:
            minLat = float(request.form.get('minLat'))
            minLon = float(request.form['minLon'])
            maxLat = float(request.form['maxLat'])
            maxLon = float(request.form['maxLon'])
            startdate = request.form['startdate']
            enddate = request.form['enddate']
            start = ee.Date(startdate)
            end = ee.Date(enddate) 

            rectangle = ee.Geometry.Rectangle(minLon,minLat,maxLon,maxLat)
            collection = ee.ImageCollection('COPERNICUS/S2') \
                    .filterBounds(rectangle) \
                    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 70)) \
                    .filterDate(start,end) \
                    .map(maskS2clouds) \
                    .select('B.*')
            composite = collection.median()
            ndvi = composite.expression(
                '(NIR - RED)/(NIR + RED)', {
                'NIR': composite.select('B8'),
                'RED': composite.select('B4')})  

            count = collection.toList(100).length().getInfo() 
            if count==0:
                raise ValueError('No images found')        

            fimage = ee.Image(ndvi.clip(rectangle))
            downloadpath = fimage.getDownloadUrl({'scale':10,'crs':'EPSG:4326'})  
            
            image = ee.Image(collection.first()) 
            # systemid = image.get('system:id').getInfo()
            projection = image.select(0).projection().getInfo()['crs']
            
            glbls['minLat'] = minLat
            glbls['minLon'] = minLon
            glbls['maxLat'] = maxLat
            glbls['maxLon'] = maxLon

            return render_template('output.html',
                                downloadtext = 'Download image intersection',
                                downloadpathclip = downloadpath, 
                                projection = projection,
                                rect = [glbls['minLon'],glbls['minLat'],glbls['maxLon'],glbls['maxLat']],
                                count = count)
        except Exception as e:
            return '<br />An error occurred in visinfrared: %s<br /><a href="output.html" name="return"> Return</a>'%e  

if __name__ == '__main__':   
    app.run(debug=True, host='0.0.0.0') 