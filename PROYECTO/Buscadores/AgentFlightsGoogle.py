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
from AgentUtil.APIKeys import QPX_API_KEY

from flask import Flask, request
from rdflib import Graph, Namespace, Literal
from datetime import datetime

# Nuestros namespaces que usaremos luego
myns = Namespace("http://my.namespace.org/")
myns_pet = Namespace("http://my.namespace.org/peticiones/")
myns_atr = Namespace("http://my.namespace.org/atributos/")
myns_rndtrp = Namespace("http://my.namespace.org/roundtrips/")
myns_vlo = Namespace("http://my.namespace.org/vuelos/")

# COMMON QUERY PARAMS
#QPX_END_POINT = 'https://www.googleapis.com/qpxExpress/v1/trips/search'
QPX_END_POINT = 'https://www.googleapis.com/qpxExpress/v1/trips/search'
headers = {'content-type': 'application/json'}

#Ejemplo de una respuesta. No se usa ahora, borrar después
response = {
 "kind": "qpxExpress#tripsSearch",
 "trips": {
  "kind": "qpxexpress#tripOptions",
  "requestId": "O79cVUkkIH8sLtIF90M8WQ",
  "data": {
   "kind": "qpxexpress#data",
   "airport": [
    {
     "kind": "qpxexpress#airportData",
     "code": "BCN",
     "city": "BCN",
     "name": "Barcelona"
    },
    {
     "kind": "qpxexpress#airportData",
     "code": "PRG",
     "city": "PRG",
     "name": "Prague Ruzyne"
    }
   ],
   "city": [
    {
     "kind": "qpxexpress#cityData",
     "code": "BCN",
     "name": "Barcelona"
    },
    {
     "kind": "qpxexpress#cityData",
     "code": "PRG",
     "name": "Prague"
    }
   ],
   "aircraft": [
    {
     "kind": "qpxexpress#aircraftData",
     "code": "319",
     "name": "Airbus A319"
    }
   ],
   "tax": [
    {
     "kind": "qpxexpress#taxData",
     "id": "YQ_F",
     "name": "QS YQ surcharge"
    },
    {
     "kind": "qpxexpress#taxData",
     "id": "JD_001",
     "name": "Spain JD"
    },
    {
     "kind": "qpxexpress#taxData",
     "id": "QV_001",
     "name": "Spain QV"
    },
    {
     "kind": "qpxexpress#taxData",
     "id": "OG_001",
     "name": "Spain OG"
    }
   ],
   "carrier": [
    {
     "kind": "qpxexpress#carrierData",
     "code": "QS",
     "name": "Travel Service, A.S."
    }
   ]
  },
  "tripOption": [
   {
    "kind": "qpxexpress#tripOption",
    "saleTotal": "EUR71.68",
    "id": "4AJKi2wVp0SOyZauZNPjHB001",
    "slice": [
     {
      "kind": "qpxexpress#sliceInfo",
      "duration": 145,
      "segment": [
       {
        "kind": "qpxexpress#segmentInfo",
        "duration": 145,
        "flight": {
         "carrier": "QS",
         "number": "8689"
        },
        "id": "GwCYVfUqPLipD-AM",
        "cabin": "COACH",
        "bookingCode": "J",
        "bookingCodeCount": 9,
        "marriedSegmentGroup": "0",
        "leg": [
         {
          "kind": "qpxexpress#legInfo",
          "id": "LCVDhAKBbrCjGo2w",
          "aircraft": "319",
          "arrivalTime": "2015-06-02T17:00+02:00",
          "departureTime": "2015-06-02T14:35+02:00",
          "origin": "BCN",
          "destination": "PRG",
          "originTerminal": "1",
          "destinationTerminal": "2",
          "duration": 145,
          "operatingDisclosure": "OPERATED BY CZECH AIRLINES",
          "mileage": 843,
          "meal": "Snack or Brunch"
         }
        ]
       }
      ]
     }
    ],
    "pricing": [
     {
      "kind": "qpxexpress#pricingInfo",
      "fare": [
       {
        "kind": "qpxexpress#fareInfo",
        "id": "AmmLtTiQZH5jtHZv+jxRIwaSx0NxFiHka9NHNGpI",
        "carrier": "QS",
        "origin": "BCN",
        "destination": "PRG",
        "basisCode": "JQS"
       }
      ],
      "segmentPricing": [
       {
        "kind": "qpxexpress#segmentPricing",
        "fareId": "AmmLtTiQZH5jtHZv+jxRIwaSx0NxFiHka9NHNGpI",
        "segmentId": "GwCYVfUqPLipD-AM",
        "freeBaggageOption": [
         {
          "kind": "qpxexpress#freeBaggageAllowance",
          "bagDescriptor": [
           {
            "kind": "qpxexpress#bagDescriptor",
            "commercialName": "UPTO33LB 15KG BAGGAGE",
            "count": 1,
            "description": [
             "Up to 33 lb/15 kg"
            ],
            "subcode": "0C1"
           }
          ],
          "kilos": 15
         }
        ]
       }
      ],
      "baseFareTotal": "EUR9.00",
      "saleFareTotal": "EUR9.00",
      "saleTaxTotal": "EUR62.68",
      "saleTotal": "EUR71.68",
      "passengers": {
       "kind": "qpxexpress#passengerCounts",
       "adultCount": 1
      },
      "tax": [
       {
        "kind": "qpxexpress#taxInfo",
        "id": "JD_001",
        "chargeType": "GOVERNMENT",
        "code": "JD",
        "country": "ES",
        "salePrice": "EUR15.32"
       },
       {
        "kind": "qpxexpress#taxInfo",
        "id": "QV_001",
        "chargeType": "GOVERNMENT",
        "code": "QV",
        "country": "ES",
        "salePrice": "EUR3.78"
       },
       {
        "kind": "qpxexpress#taxInfo",
        "id": "OG_001",
        "chargeType": "GOVERNMENT",
        "code": "OG",
        "country": "ES",
        "salePrice": "EUR0.58"
       },
       {
        "kind": "qpxexpress#taxInfo",
        "id": "YQ_F",
        "chargeType": "CARRIER_SURCHARGE",
        "code": "YQ",
        "salePrice": "EUR43.00"
       }
      ],
      "fareCalculation": "BCN QS PRG 9.85JQS NUC 9.85 END ROE 0.913391 FARE EUR 9.00 XT 15.32JD 0.58OG 3.78QV 43.00YQ",
      "latestTicketingTime": "2015-05-18T02:58-04:00",
      "ptc": "ADT"
     }
    ]
   }
  ]
 }
}

# Formato Datetime
# defaultDepDate = datetime.strptime("2015-08-20", '%Y-%m-%d')
# defaultRetDate = datetime.strptime("2015-08-30", '%Y-%m-%d')

def buscar_vuelos(adultCount=1, childCount=0, origin="BCN", destination="PRG",
  departureDate="2015-08-20", returnDate="2015-08-30", solutions=50,
  maxPrice=500, earliestDepartureTime="06:00", latestDepartureTime="23:00",
  earliestReturnTime="06:00", latestReturnTime="23:00"):

  maxPriceStr = "EUR" + str(maxPrice)

  payload = {
    "request": {
      "slice": [
        {
          "origin": origin,
          "destination": destination,
          "date": departureDate,
          "permittedDepartureTime": {
            "earliestTime": earliestDepartureTime,
            "latestTime": latestDepartureTime
          }
        },
        {
          "origin": destination,
          "destination": origin,
          "date": returnDate,
          "permittedDepartureTime": {
            "earliestTime": earliestReturnTime,
            "latestTime": latestReturnTime
          }
        }
      ],
      "passengers": {
        "adultCount": adultCount,
        "infantInLapCount": 0,
        "infantInSeatCount": 0,
        "childCount": childCount,
        "seniorCount": 0
      },
      "solutions": solutions,
      "maxPrice": maxPriceStr,
      "refundable": False
    }
  }
  gresp = Graph()
  #print payload
  b = False
  if b == True:
    r = requests.post(QPX_END_POINT, params={'key': QPX_API_KEY}, data=json.dumps(payload), headers=headers)
    #print r.text

    dic = r.json()
    out_file = open("test.json","w")

# Save the dictionary into this file
# (the 'indent=4' is optional, but makes it more readable)
    json.dump(dic,out_file, indent=4) 
    #print json.dumps(dic, indent=4, sort_keys=True)

    # Si quiero imprimir la respuesta pretty
    # for trip in dic['trips']['tripOption']:
    #     print "=========================> Total price: " + trip['saleTotal']
    #     sliceCount = 0
    #     for _slice in trip['slice']:
    #         print "## In slice => ", sliceCount
    #         print "Duration: ", _slice['duration']
    #         segmentCount = 0
    #         for segment in _slice['segment']:
    #             print "###### In segment => ", segmentCount
    #             print ("Flight number: " + segment['flight']['number'] +
    #                 ", flignt carrier: " + segment['flight']['carrier'])
    #             legCount = 0
    #             for leg in segment['leg']:
    #                 print "########## In leg => ", legCount
    #                 print ("From " + leg['origin'] + " to " + leg['destination'])
    #                 print ("Dep. time: " + leg['departureTime'] +
    #                     " from terminal " + leg['originTerminal'])
    #                 print ("Arr. time: " + leg['arrivalTime'] +
    #                     " to terminal " + leg['destinationTerminal'])
    #                 legCount += 1
    #             segmentCount += 1
    #         sliceCount += 1


    # Hago bind de las ontologias que usaremos en el grafo
    gresp.bind('myns_pet', myns_pet)
    gresp.bind('myns_atr', myns_atr)
    gresp.bind('myns_rndtrp', myns_rndtrp)
    gresp.bind('myns_vlo', myns_vlo)
    gresp.bind('myns', myns)
    i = 0
    print len(dic['trips']['tripOption'])
    # TODO: ANADIR TIPO DE ACTIVIDAD PARA RECORRER EL GRAFO
    for trip in dic['trips']['tripOption']:
        # Identificador unico para cada roundtrip
        i+= 1

        print i  
        rndtrip_obj = myns_rndtrp[trip['id']]
        # Precio del roundtrip
        gresp.add((rndtrip_obj, myns_atr.esUn, myns.viaje))
        gresp.add((rndtrip_obj, myns_atr.cuesta, Literal(trip['saleTotal'])))
        # DATOS IDA
        # Id unico para la ida del roundtrip
        idGo = trip['slice'][0]['segment'][0]['flight']['number'] + " " + trip['slice'][0]['segment'][0]['flight']['carrier']
        vlo_obj_go = myns_vlo[idGo]
        # El roundtrip tiene esta ida
        gresp.add((rndtrip_obj, myns_atr.ida, vlo_obj_go))
        # La ida dura esto
        durationGo = trip['slice'][0]['duration']
        gresp.add((vlo_obj_go, myns_atr.dura, Literal(durationGo)))
        # Fecha y hora de salida y aterrizaje de la ida
        horaGoSale = trip['slice'][0]['segment'][0]['leg'][0]['departureTime']
        horaGoLlega = trip['slice'][0]['segment'][0]['leg'][0]['arrivalTime']
        gresp.add((vlo_obj_go, myns_atr.hora_sale, Literal(horaGoSale)))
        gresp.add((vlo_obj_go, myns_atr.hora_llega, Literal(horaGoLlega)))
        # Terminal y ciudad de salida de la ida

        terminalGoSale = "unknown"
        if 'originTerminal' in trip['slice'][0]['segment'][0]['leg'][0]:
          terminalGoSale = trip['slice'][0]['segment'][0]['leg'][0]['originTerminal']

        terminalGoLlega = "unknown"
        if 'destinationTerminal' in trip['slice'][0]['segment'][0]['leg'][0]:
          terminalGoLlega = trip['slice'][0]['segment'][0]['leg'][0]['destinationTerminal']
        
        gresp.add((vlo_obj_go, myns_atr.terminal_sale, Literal(terminalGoSale)))
        gresp.add((vlo_obj_go, myns_atr.terminal_llega, Literal(terminalGoLlega)))
        # Direccion de la ida (redundante)
        ciudadGoSale = trip['slice'][0]['segment'][0]['leg'][0]['origin']
        ciudadGoLlega = trip['slice'][0]['segment'][0]['leg'][0]['destination']
        gresp.add((vlo_obj_go, myns_atr.ciudad_sale, Literal(ciudadGoSale)))
        gresp.add((vlo_obj_go, myns_atr.ciudad_llega, Literal(ciudadGoLlega)))

        # DATOS VUELTA
        # Id unico para la vuelta del roundtrip
        idBack = trip['slice'][1]['segment'][0]['flight']['number'] + " " + trip['slice'][1]['segment'][0]['flight']['carrier']
        vlo_obj_back = myns_vlo[idBack]
        # El roundtrip tiene esta vuelta
        gresp.add((rndtrip_obj, myns_atr.vuelta, vlo_obj_back))
        # Cuanto dura esta vuelta
        durationBack = trip['slice'][1]['duration']
        gresp.add((vlo_obj_back, myns_atr.dura, Literal(durationBack)))
        # Fecha y hora de salida y aterrizaje de la vuelta
        horaBackSale = trip['slice'][1]['segment'][0]['leg'][0]['departureTime']
        horaBackLlega = trip['slice'][1]['segment'][0]['leg'][0]['arrivalTime']
        gresp.add((vlo_obj_back, myns_atr.hora_sale, Literal(horaBackSale)))
        gresp.add((vlo_obj_back, myns_atr.hora_llega, Literal(horaBackLlega)))
        # Terminal y ciudad de salida de la vuelt
        terminalBackSale = "unknown"
        if 'originTerminal' in trip['slice'][1]['segment'][0]['leg'][0]:
          terminalBackSale = trip['slice'][1]['segment'][0]['leg'][0]['originTerminal']

        terminalBackLlega = "unknown"
        if 'destinationTerminal' in trip['slice'][1]['segment'][0]['leg'][0]:
          terminalBackLlega = trip['slice'][1]['segment'][0]['leg'][0]['destinationTerminal']

        gresp.add((vlo_obj_back, myns_atr.terminal_sale, Literal(terminalBackSale)))
        gresp.add((vlo_obj_back, myns_atr.terminal_llega, Literal(terminalBackLlega)))
        # Direccion de la vuelta (redundante)
        ciudadBackSale = trip['slice'][1]['segment'][0]['leg'][0]['origin']
        ciudadBackLlega = trip['slice'][1]['segment'][0]['leg'][0]['destination']
        gresp.add((vlo_obj_back, myns_atr.ciudad_sale, Literal(ciudadBackSale)))
        gresp.add((vlo_obj_back, myns_atr.ciudad_llega, Literal(ciudadBackLlega)))
    
    gresp.serialize('f.rdf')
  else:
  # print "GRAFO DE RESPUESTA"
  # for s, p, o in gresp:
  #   print 's: ' + s
  #   print 'p: ' + p
  #   print 'o: ' + o
  #   print '\n'
    gresp.parse('f.rdf' ,format='xml')

  print "repuesta"
  return gresp


