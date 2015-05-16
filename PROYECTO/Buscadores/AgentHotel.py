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

import requests
import urllib2
import md5
import time
from AgentUtil.APIKeys import EAN_DEV_CID, EAN_KEY, EAN_SECRET


service = 'http://api.ean.com/ean-services/rs/hotel/'
version = 'v3/'
method = 'list'
EAN_END_POINT = service + version + method

hash = md5.new()
# seconds since GMT Epoch
timestamp = str(int(time.time()))
# print timestamp
sig = md5.new(EAN_KEY + EAN_SECRET + timestamp).hexdigest()
# print "Sig has ", sig.__len__(), " charachters"



r = requests.get(EAN_END_POINT,
                 params={'cid': EAN_DEV_CID, 'minorRev': 29, 'apiKey': EAN_KEY, 'sig': sig,
                 		'locale': 'es_ES', 'currencyCode': 'EUR', 'numberOfResults': 10,            'latitude': '041.40000', 'longitude': '002.16000',
                         'searchRadius': 2, 'searchRadiusUnit': 'KM',
                         'arrivalDate': '06/02/2015', 'departureDate': '06/08/2015'
                       })

#print r.text
dic = r.json()

if 'EanWsError' in dic['HotelListResponse']:
	print 'Error de tipo ' + dic['HotelListResponse']['EanWsError']['category'] + ' => ' + dic['HotelListResponse']['EanWsError']['verboseMessage']
else:
	for hot in dic['HotelListResponse']['HotelList']['HotelSummary']:
		print hot['name']





