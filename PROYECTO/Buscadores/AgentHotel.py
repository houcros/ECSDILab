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

from AgentUtil.Agent import Agent
import socket
from rdflib import Graph, Namespace, Literal

# Nuestros namespaces que usaremos luego
agn = Namespace("http://www.agentes.org#")
myns = Namespace("http://my.namespace.org/")
myns_pet = Namespace("http://my.namespace.org/peticiones/")
myns_atr = Namespace("http://my.namespace.org/atributos/")
myns_hot = Namespace("http://my.namespace.org/hoteles/")

# Configuration stuff
port = 9004
hostname = socket.gethostname()

# Datos del Agente
AgenteHotel = Agent('AgentHotel',
                  agn.AgentHotel,
                  'http://%s:%d/comm' % (hostname, port),
                  'http://%s:%d/Stop' % (hostname, port))

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

def buscar_hoteles(destinationCity="Barcelona", destinationCountry="Spain", 
  searchRadius=2, arrivalDate="06/02/2015", departureDate="06/08/2015", 
  numberOfAdults=2, numberOfChildren=0, propertyCategory=1):
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
                          'searchRadiusUnit': "KM",
                          'arrivalDate': arrivalDate,
                          'departureDate': departureDate,
                          'numberOfAdults': numberOfAdults,
                          'numberOfChildren': numberOfChildren,
                          'propertyCategory': propertyCategory  
                      	})

  #print r.text
  dic = r.json()
  #print json.dumps(dic, indent=4, sort_keys=True)

  gresp = Graph()
  # Hago bind de las ontologias que usaremos en el grafo
  gresp.bind('myns_pet', myns_pet)
  gresp.bind('myns_atr', myns_atr)
  gresp.bind('myns_hot', myns_hot)

  if 'EanWsError' in dic['HotelListResponse']:
  	print ('Error de tipo ' + dic['HotelListResponse']['EanWsError']['category'], 
      ' => ' + dic['HotelListResponse']['EanWsError']['verboseMessage'])
    #gresp = build_message(Graph(), ACL['not-understood'], sender=AgentHotel.uri)
  else:
    for hot in dic['HotelListResponse']['HotelList']['HotelSummary']:
  	 # print ("Hotel " + hot['name'],
  	 # 	", distancia del centro: " + '{:.2f}'.format(hot['proximityDistance']),
  	 # 	' ' + hot['proximityUnit'] + ', precio total: ',
  	 # 	hot['RoomRateDetailsList']['RoomRateDetails']['RateInfos']['RateInfo']['ChargeableRateInfo']['@total'],
  	 # 	', rating: ' + '{:.1f}'.format(hot['hotelRating']),
  	 # 	', tripAdvisorRating: ' + '{:.1f}'.format(hot['tripAdvisorRating']),
  	 # 	' tripAdvisorReviewCount: ' + '{:.0f}'.format(hot['tripAdvisorReviewCount'])
  	 # 	)
      hot_obj = myns_hot[hot['hotelId']]
      gresp.add((hot_obj, myns_atr.esUn, myns.hotel))
      gresp.add((hot_obj, myns_atr.distancia, Literal(hot['proximityDistance'])))
      gresp.add((hot_obj, myns_atr.distancia_unidad, Literal(hot['proximityUnit'])))
      gresp.add((hot_obj, myns_atr.cuesta, Literal(hot['RoomRateDetailsList']['RoomRateDetails']['RateInfos']['RateInfo']['ChargeableRateInfo']['@total'])))
      gresp.add((hot_obj, myns_atr.rating, Literal(hot['hotelRating'])))
      gresp.add((hot_obj, myns_atr.tripAdvisorRating, Literal(hot['tripAdvisorRating'])))
      gresp.add((hot_obj, myns_atr.tripAdvisorReviewCount, Literal(hot['tripAdvisorReviewCount'])))

  return gresp




