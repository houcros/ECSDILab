# -*- coding: utf-8 -*-
"""
filename: AgentBuscador

Agente que se registra como agente buscador de informacion

@author: javier
"""
__author__ = 'javier'

from multiprocessing import Process, Queue
import socket
import gzip
import argparse

from flask import Flask, request
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import FOAF, RDF

from AgentUtil.OntoNamespaces import ACL, DSO , TIO
from AgentUtil.FlaskServer import shutdown_server
from AgentUtil.ACLMessages import build_message, send_message, get_message_properties
from AgentUtil.Agent import Agent
from AgentUtil.Logging import config_logger

import pprint
from googleplaces import GooglePlaces
from AgentUtil.APIKeys import GOOGLEAPI_KEY

# Definimos los parametros de la linea de comandos
parser = argparse.ArgumentParser()
parser.add_argument('--open', help="Define si el servidor esta abierto al exterior o no", action='store_true',
                    default=False)
parser.add_argument('--port', type=int, help="Puerto de comunicacion del agente")
parser.add_argument('--dhost', default='localhost', help="Host del agente de directorio")
parser.add_argument('--dport', type=int, help="Puerto de comunicacion del agente de directorio")

# Logging
logger = config_logger(level=1)

# parsing de los parametros de la linea de comandos
args = parser.parse_args()

# Configuration stuff
if args.port is None:
    port = 9001
else:
    port = args.port

if args.open is None:
    hostname = '0.0.0.0'
else:
    hostname = socket.gethostname()

if args.dport is None:
    dport = 9000
else:
    dport = args.dport

if args.dhost is None:
    dhostname = socket.gethostname()
else:
    dhostname = args.dhost

# Flask stuff
app = Flask(__name__)

# Configuration constants and variables
agn = Namespace("http://www.agentes.org#")

# Contador de mensajes
mss_cnt = 0

# Datos del Agente
AgentBuscador = Agent('AgentBuscador',
                  agn.AgentBuscador,
                  'http://%s:%d/comm' % (hostname, port),
                  'http://%s:%d/Stop' % (hostname, port))

# Directory agent address
DirectoryAgent = Agent('DirectoryAgent',
                       agn.Directory,
                       'http://%s:%d/Register' % (dhostname, dport),
                       'http://%s:%d/Stop' % (dhostname, dport))

# Global dsgraph triplestore
dsgraph = Graph()

# Cola de comunicacion entre procesos
cola1 = Queue()


# def register_message():
#     """
#     Envia un mensaje de registro al servicio de registro
#     usando una performativa Request y una accion Register del
#     servicio de directorio

#     :param gmess:
#     :return:
#     """

#     logger.info('Nos registramos')

#     global mss_cnt

#     gmess = Graph()

#     # Construimos el mensaje de registro
#     gmess.bind('foaf', FOAF)
#     gmess.bind('dso', DSO)
#     reg_obj = agn[InfoAgent.name + '-Register']
#     gmess.add((reg_obj, RDF.type, DSO.Register))
#     gmess.add((reg_obj, DSO.Uri, InfoAgent.uri))
#     gmess.add((reg_obj, FOAF.Name, Literal(InfoAgent.name)))
#     gmess.add((reg_obj, DSO.Address, Literal(InfoAgent.address)))
#     gmess.add((reg_obj, DSO.AgentType, DSO.HotelsAgent))

#     # Lo metemos en un envoltorio FIPA-ACL y lo enviamos
#     gr = send_message(
#         build_message(gmess, perf=ACL.request,
#                       sender=InfoAgent.uri,
#                       receiver=DirectoryAgent.uri,
#                       content=reg_obj,
#                       msgcnt=mss_cnt),
#         DirectoryAgent.address)
#     mss_cnt += 1

#     return gr


@app.route("/iface", methods=['GET', 'POST'])
def browser_iface():
    """
    Permite la comunicacion con el agente via un navegador
    via un formulario
    """
    return 'Nothing to see here'


@app.route("/Stop")
def stop():
    """
    Entrypoint que para el agente

    :return:
    """
    tidyup()
    shutdown_server()
    return "Parando Servidor"


@app.route("/comm")
def comunicacion():
    """
    Entrypoint de comunicacion del agente
    Simplementet retorna un objeto fijo que representa una
    respuesta a una busqueda de hotel

    Asumimos que se reciben siempre acciones que se refieren a lo que puede hacer
    el agente (buscar con ciertas restricciones, reservar)
    Las acciones se mandan siempre con un Request
    Prodriamos resolver las busquedas usando una performativa de Query-ref
    """
    #global dsgraph
    #global mss_cnt

    #logger.info('Peticion de informacion recibida')

    ## Extraemos el mensaje y creamos un grafo con el
    #message = request.args['content']
    #gm = Graph()
    #gm.parse(data=message)

    #msgdic = get_message_properties(gm)

    ## Comprobamos que sea un mensaje FIPA ACL
    #if msgdic is None:
        ## Si no es, respondemos que no hemos entendido el mensaje
        #gr = build_message(Graph(), ACL['not-understood'], sender=InfoAgent.uri, msgcnt=mss_cnt)
    #else:
        ## Obtenemos la performativa
        #perf = msgdic['performative']

        #if perf != ACL.request:
            ## Si no es un request, respondemos que no hemos entendido el mensaje
            #gr = build_message(Graph(), ACL['not-understood'], sender=InfoAgent.uri, msgcnt=mss_cnt)
        #else:
            ## Extraemos el objeto del contenido que ha de ser una accion de la ontologia de acciones del agente
            ## de registro

            ## Averiguamos el tipo de la accion
            #if 'content' in msgdic:
                #content = msgdic['content']
                #accion = gm.value(subject=content, predicate=RDF.type)

            ## Aqui realizariamos lo que pide la accion
            ## Por ahora simplemente retornamos un Inform-done
            #gr = build_message(Graph(),
                #ACL['inform-done'],
                #sender=InfoAgent.uri,
                #msgcnt=mss_cnt,
                #receiver=msgdic['sender'], )
    #mss_cnt += 1

    #logger.info('Respondemos a la peticion')
    gr = build_message(Graph(), ACL['not-understood'], sender=AgentBuscador.uri)
    # resp = gr.serialize(format='xml')
    # print "####################"
    # print resp
    # print "####################"
    return resp


def tidyup():
    """
    Acciones previas a parar el agente

    """
    global cola1
    cola1.put(0)


def agentbehavior1(cola):
    """
    Un comportamiento del agente    port = 9001

    :return:
    """
    # Registramos el agente
    # gr = register_message()

    # Escuchando la cola hasta que llegue un 0
    fin = False
    while not fin:
        while cola.empty():
            pass
        v = cola.get()
        if v == 0:
            fin = True
        else:
            print v

            # Selfdestruct
            # requests.get(InfoAgent.stop)

def buscar_vuelos():

    g = Graph()

    # Carga el grafo RDF desde el fichero
    ontofile = gzip.open('../../FlightData/FlightRoutes.ttl.gz')
    g.parse(ontofile, format='turtle')

    # Consulta al grafo los aeropuertos dentro de la caja definida por las coordenadas
    qres = g.query(
        """
        prefix tio:<http://purl.org/tio/ns#>
        prefix geo:<http://www.w3.org/2003/01/geo/wgs84_pos#>
        prefix dbp:<http://dbpedia.org/ontology/>

        Select ?f
        where {
            ?f rdf:type dbp:Airport .
            ?f geo:lat ?lat .
            ?f geo:long ?lon .
            Filter ( ?lat < "41.7"^^xsd:float &&
                     ?lat > "41.0"^^xsd:float &&
                     ?lon < "2.3"^^xsd:float &&
                     ?lon > "2.0"^^xsd:float)
            }
        LIMIT 30
        """,
        initNs=dict(tio=TIO))

    # Recorre los resultados y se queda con el ultimo
    for r in qres:
        ap = r['f']

    print 'Aeropuerto:', ap
    print


    # Consulta todos los vuelos que conectan con ese aeropuerto
    airquery = """
        prefix tio:<http://purl.org/tio/ns#>
        Select *
        where {
            ?f rdf:type tio:Flight.
            ?f tio:to <%s>.
            ?f tio:from ?t.
            ?f tio:operatedBy ?o.
            }
        """ % ap

    qres = g.query(airquery, initNs=dict(tio=TIO))

    print 'Num Vuelos:', len(qres.result)
    print


    # Imprime los resultados
    for row in qres.result:
        print row

def buscar_transportes():
    g = Graph()

    # Carga el grafo RDF desde el fichero
    # Cambiar por RDF transportes
    # El fichero actual no esta en el mismo formato y no lo lee
    ontofile = gzip.open('../../TransportData/TransportRoutes.ttl.gz')
    g.parse(ontofile, format='turtle')

    # Consulta al grafo los aeropuertos dentro de la caja definida por las coordenadas
    qres = g.query(
        """
        prefix tio:<http://purl.org/tio/ns#>
        prefix geo:<http://www.w3.org/2003/01/geo/wgs84_pos#>
        prefix dbp:<http://dbpedia.org/ontology/>

        Select ?f
        where {
            ?f rdf:type dbp:Airport .
            ?f geo:lat ?lat .
            ?f geo:long ?lon .
            Filter ( ?lat < "41.7"^^xsd:float &&
                     ?lat > "41.0"^^xsd:float &&
                     ?lon < "2.3"^^xsd:float &&
                     ?lon > "2.0"^^xsd:float)
            }
        LIMIT 30
        """,
        initNs=dict(tio=TIO))

    # Recorre los resultados y se queda con el ultimo
    for r in qres:
        ap = r['f']

    print 'Aeropuerto:', ap
    print


    # Consulta todos los vuelos que conectan con ese aeropuerto
    airquery = """
        prefix tio:<http://purl.org/tio/ns#>
        Select *
        where {
            ?f rdf:type tio:Flight.
            ?f tio:to <%s>.
            ?f tio:from ?t.
            ?f tio:operatedBy ?o.
            }
        """ % ap

    qres = g.query(airquery, initNs=dict(tio=TIO))

    print 'Num Vuelos:', len(qres.result)
    print


    # Imprime los resultados
    for row in qres.result:
        print row    

def buscar_actividades(nombreActividad, radio):
    print nombreActividad

    google_places = GooglePlaces(GOOGLEAPI_KEY)

    query_result = google_places.nearby_search(
        location=u'Barcelona, España', keyword='', #Podemos poner nombres de museos para filtrar mas la busqueda, etc.. (ej: Basilica Galeria)
        radius=radio, types=[nombreActividad]) #Tipos de lugares, vease listado de types en https://developers.google.com/places/documentation/supported_types?hl=es

    #query_result_night_club = google_places.nearby_search(
       # location=u'Barcelona, España', keyword='', 
        #radius=300, types=['night_club']) 

    # Imprimimos informacion de los resultados
    print query_result
    if query_result.has_attributions:
        print query_result.html_attributions

    for place in query_result.places:
        # Returned places from a query are place summaries.
        print place.name
        print place.geo_location
        print place.reference

        # The following method has to make a further API call.
        place.get_details()
        # Referencing any of the attributes below, prior to making a call to
        # get_details() will raise a googleplaces.GooglePlacesAttributeError.
        pprint.pprint(place.details)  # A dict matching the JSON response from Google.
        print place.local_phone_number

if __name__ == '__main__':
    #buscar_vuelos() #Funciona
    #buscar_transportes() #Funciona pero con vuelos, con transportes peta

    #Llamadas a la API de Google Places para las diferentes actividades

    #buscar_actividades('museum', 300) # museum, zoo, night_club, amusement_park
    #buscar_actividades('zoo', 5000) 
    #buscar_actividades('night_club', 300) 
    #buscar_actividades('amusement_park', 600) 

    # Ponemos en marcha los behaviors
    #ab1 = Process(target=agentbehavior1, args=(cola1,))
    #ab1.start()

    # Ponemos en marcha el servidor
    app.run(host=hostname, port=port)

    # Esperamos a que acaben los behaviors
    #ab1.join()
    logger.info('The End')
