# -*- coding: utf-8 -*-
"""
Created on Fri Dec 27 15:58:13 2013

Demo de consulta del servicio de hoteles ean.com

Para poder usarlo hay que registrarse y obtener una clave de desarrollador en  la direccion

https://devsecure.ean.com/member/register

Se ha de crear un fichero python APIKeys.py que contenga la información para el
acceso a EAN (EANCID, EANKEY)


@author: javier
"""

__author__ = 'javier'

import json
import requests
import urllib2
import md5
import time
from geopy.geocoders import Nominatim
from AgentUtil.APIKeys import EAN_DEV_CID, EAN_KEY, EAN_SECRET

# COMMON QUERY PARAMS
service = 'http://api.ean.com/ean-services/rs/hotel/'
version = 'v3/'
method = 'list'
EAN_END_POINT = service + version + method
minorRev = 29

# GENERATE SECRET FOR QUERY
hash = md5.new()
# seconds since GMT Epoch
timestamp = str(int(time.time()))
# print timestamp
sig = md5.new(EAN_KEY + EAN_SECRET + timestamp).hexdigest()
# print "Sig has ", sig.__len__(), " charachters"

# SPECIFIC PARAMS FOR QUERY
destinationCity = "Barcelona"
destinationCountry = "Spain"
searchRadius = 2
searchRadiusUnit = "KM"
arrivalDate = "06/02/2015"
departureDate = "06/08/2015"
numberOfAdults = 2
numberOfChildren = 0
propertyCategory = 1
#Values: 1: hotel 2: suite 3: resort 4: vacation rental/condo 5: bed & breakfast 6: all-inclusive

# COORDINATES OF THE DESTINATION
geolocator = Nominatim()
location = geolocator.geocode(destinationCity + ", " + destinationCountry)
print ((location.latitude, location.longitude))
print

r = requests.get(EAN_END_POINT,
                 params={'cid': EAN_DEV_CID,
                 		'minorRev': minorRev,
                 		'apiKey': EAN_KEY,
                 		'sig': sig,
                 		'locale': 'es_ES',
                 		'currencyCode': 'EUR',
                 		'numberOfResults': 10,
                 		'latitude': location.latitude,
                 		'longitude': location.longitude,
                        'searchRadius': searchRadius,
                        'searchRadiusUnit': searchRadiusUnit,
                        'arrivalDate': arrivalDate,
                        'departureDate': departureDate,
                        'numberOfAdults': numberOfAdults,
                        'numberOfChildren': numberOfChildren,
                        'propertyCategory': propertyCategory
                    	})

#print r.text
dic = r.json()
#print json.dumps(dic, indent=4, sort_keys=True)

if 'EanWsError' in dic['HotelListResponse']:
	print ('Error de tipo ' + dic['HotelListResponse']['EanWsError']['category'],
		' => ' + dic['HotelListResponse']['EanWsError']['verboseMessage'])
else:
	for hot in dic['HotelListResponse']['HotelList']['HotelSummary']:
		print ("Hotel " + hot['name'],
			", distancia del centro: " + '{:.2f}'.format(hot['proximityDistance']),
			' ' + hot['proximityUnit'] + ', precio total: ',
			hot['RoomRateDetailsList']['RoomRateDetails']['RateInfos']['RateInfo']['ChargeableRateInfo']['@total'],
			', rating: ' + '{:.1f}'.format(hot['hotelRating']),
			', tripAdvisorRating: ' + '{:.1f}'.format(hot['tripAdvisorRating']),
			' tripAdvisorReviewCount: ' + '{:.0f}'.format(hot['tripAdvisorReviewCount'])
			)
		print




