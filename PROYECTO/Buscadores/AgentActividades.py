# -*- coding: utf-8 -*-
"""
Created on Fri Dec 27 15:58:13 2013

Agente que responde a peticiones

Demo que hace una consulta a Google Places con las coordenadas que le asigna el
servicio de geolocalizacion a Barcelona en un area de 300m a la redonda buscando estaciones
de metro (categorizadas como 'bus_station')

Se ha de crear un fichero python APIKeys.py que contenga la información para el
acceso a las APIs de Google (GOOGLEAPI_KEY)

@author: javier
"""
__author__ = 'javier'

import pprint
from googleplaces import GooglePlaces
from flask import Flask, request
from rdflib import Graph, Namespace, Literal
from AgentUtil.APIKeys import GOOGLEAPI_KEY

# Nuestros namespaces que usaremos luego
myns = Namespace("http://my.namespace.org/")
myns_pet = Namespace("http://my.namespace.org/peticiones/")
myns_atr = Namespace("http://my.namespace.org/atributos/")
myns_act = Namespace("http://my.namespace.org/actividades/")
myns_lug = Namespace("http://my.namespace.org/lugares/")

LOG_TAG = "DEBUG: AgenteActividades => "

def buscar_actividades(destinationCity="Barcelona", destinationCountry="Spain", keyword="movie", radius=20000, types=[]):
    location= destinationCity+", "+destinationCountry
    gr = Graph()

    b = False
    
    print location

    if b == True:
        print "INFO AgenteActividades => Recibo peticion de actividades.\n"
        google_places = GooglePlaces(GOOGLEAPI_KEY)

        # You may prefer to use the text_search API, instead.
        query_result = google_places.nearby_search(
            location=location, keyword=keyword,
            radius=radius, types=types)

        print LOG_TAG + " => built query"

        if query_result.has_attributions:
            print query_result.html_attributions

        print LOG_TAG + " => about to build response Graph"

        # Grafo donde retornaremos el resultado
        gr = Graph()
        # Hago bind de las ontologias que usaremos en el grafo
        gr.bind('myns_pet', myns_pet)
        gr.bind('myns_atr', myns_atr)
        gr.bind('myns_act', myns_act)

        # TODO: ANADIR TIPO DE ACTIVIDAD PARA RECORRER EL GRAFO
        for place in query_result.places:
            # Identificador unico para cada actividad
            # Lo de -Found no se si hace falta en verdad...
            plc_obj = myns_act[place.place_id]
            # Ponemos el nombre y localizacion de la actividad
            gr.add((plc_obj, myns_atr.esUn, myns.actividad))
            gr.add((plc_obj, myns_atr.nombre, Literal(place.name)))
            gr.add((plc_obj, myns_atr.localizacion, Literal(place.geo_location)))
            # Otra llamada a la API para los otros datos
            place.get_details()
            gr.add((plc_obj, myns_atr.rating, Literal(place.rating)))
            gr.add((plc_obj, myns_atr.direccion, Literal(place.formatted_address)))
            gr.add((plc_obj, myns_atr.tel_int, Literal(place.international_phone_number)))
            
            # VERBOSE
            # Por si queremos mas detalles en el futuro
            #pprint.pprint(place.details)  # A dict matching the JSON response from Google.
            #print place.local_phone_number
        
        gr.serialize('a.rdf')
    else: 
        gr.parse('a.rdf' ,format='xml')
    print "retornar repuesta"
    return gr

