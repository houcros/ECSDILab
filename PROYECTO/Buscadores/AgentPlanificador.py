# -*- coding: utf-8 -*-
"""
Created on Fri Dec 27 15:58:13 2013

Esqueleto de agente usando los servicios web de Flask

/comm es la entrada para la recepcion de mensajes del agente
/Stop es la entrada que para el agente

Tiene una funcion AgentBehavior1 que se lanza como un thread concurrente

Asume que el agente de registro esta en el puerto 9000

@author: javier
"""

__author__ = 'javier'

from multiprocessing import Process, Queue
import socket

from rdflib import Graph, Namespace, Literal
from flask import Flask, request

from AgentUtil.FlaskServer import shutdown_server
from AgentUtil.Agent import Agent
from AgentUtil.ACLMessages import build_message, send_message, get_message_properties
from AgentUtil.OntoNamespaces import ACL, DSO
from rdflib.namespace import FOAF
from AgentUtil.Logging import config_logger
from googleplaces import types
import json
import logging
import datetime
# Configuration stuff
hostname = socket.gethostname()
port = 9002
bus_port = 9003


agn = Namespace("http://www.agentes.org#")
myns = Namespace("http://my.namespace.org/")
myns_data = Namespace("http://my.namespace.org/fechas/")
myns_pet = Namespace("http://my.namespace.org/peticiones/")
myns_atr = Namespace("http://my.namespace.org/atributos/")
myns_act = Namespace("http://my.namespace.org/actividades/")


# Contador de mensajes
mss_cnt = 0

# Datos del Agente
AgentePlanificador = Agent('AgentePlanificador',
                       agn.AgentePlanificador,
                       'http://%s:%d/comm' % (hostname, port),
                       'http://%s:%d/Stop' % (hostname, port))

# Datos del AgenteBuscador
AgenteBuscador = Agent('AgenteBuscador',
                       agn.AgenteBuscador,
                       'http://%s:%d/comm' % (hostname, bus_port),
                       'http://%s:%d/Stop' % (hostname, bus_port))

# Directory agent address
DirectoryAgent = Agent('DirectoryAgent',
                       agn.Directory,
                       'http://%s:9000/Register' % hostname,
                       'http://%s:9000/Stop' % hostname)


#logging.basicConfig()

# Global triplestore graph
dsgraph = Graph()

cola1 = Queue()

# Flask stuff
app = Flask(__name__)


@app.route("/comm")
def comunicacion():
    """
    Entrypoint de comunicacion
    """
    global dsgraph
    global mss_cnt

    print 'Peticion de informacion recibida\n'

    # Extraemos el mensaje y creamos un grafo con el
    message = request.args['content']
    print "Mensaje extraído\n"
    # VERBOSE
    print message
    print "\n\n"
    gm = Graph()
    gm.parse(data=message)
    print 'Grafo creado con el mensaje'

    msgdic = get_message_properties(gm)
    
    # Comprobamos que sea un mensaje FIPA ACL
    if msgdic is None:
        # Si no es, respondemos que no hemos entendido el mensaje
        gr = build_message(Graph(), ACL['not-understood'], sender=AgentePlanificador.uri, msgcnt=mss_cnt)
        print 'El mensaje no era un FIPA ACL'
    else:
        # Obtenemos la performativa
        perf = msgdic['performative']

        if perf != ACL.request:
            # Si no es un request, respondemos que no hemos entendido el mensaje
            gr = build_message(Graph(), ACL['not-understood'], sender=AgentePlanificador.uri, msgcnt=mss_cnt)
        else:
            # Extraemos el objeto del contenido que ha de ser una accion de la ontologia de acciones del agente
            # de registro
            # Averiguamos el tipo de la accion
            # if 'content' in msgdic:
            #     content = msgdic['content']
            #     accion = gm.value(subject=content, predicate=RDF.type)

            # Apartir de aqui tenemos que obtener parametro desde dialog y luego comunicar con buscador
            ########################################################### 
            # Parsear los parametros de Dialog
            print "Parsear los parametros de Dialog"
            #############################################################
            peticion = myns_pet["Dialogador-pide-paquete"]
            parametros = gm.triples((peticion, None, None))
            # VERBOSE
            print "Parametros: "
            print parametros
            
            actv = myns_pet.actividad

            ########################################################### 
            # Comunicar con buscador
            print "Los parametros de actividad"
            #############################################################

            destination = gm.value(subject= peticion, predicate= myns_atr.destination)
            gmess.add((actv, myns_atr.lugar, destination))
            # VERBOSE
            print "destination: "
            print destination

            origin = gm.value(subject= peticion, predicate= myns_atr.origin)
            #gmess.add((actv, myns_atr.lugar, origin))
            # VERBOSE
            print "origin: "
            print origin

            departureDate = gm.value(subject= peticion, predicate= myns_atr.departureDate)
            #gmess.add((actv, myns_atr.lugar, departureDate))
            # VERBOSE
            print "departureDate: "
            print departureDate

            returnDate = gm.value(subject= peticion, predicate= myns_atr.returnDate)
            #gmess.add((actv, myns_atr.lugar, returnDate))
            # VERBOSE
            print "returnDate: "
            print returnDate

            maxPrice = gm.value(subject= peticion, predicate= myns_atr.maxPrice)
            #gmess.add((actv, myns_atr.lugar, maxPrice))
            # VERBOSE
            print "maxPrice: "
            print maxPrice

            numberOfStars = gm.value(subject= peticion, predicate= myns_atr.numberOfStars)
            #gmess.add((actv, myns_atr.lugar, numberOfStars))
            # VERBOSE
            print "numberOfStars: "
            print numberOfStars

            activity= gm.value(subject= peticion, predicate= myns_atr.activities)
            gmess.add((actv, myns_atr.actividad, activity))
            # VERBOSE
            print "activity: "
            print activity

            radius = 20000
            # De momento solo permitimos pasar un tipo. Ampliar a mas de uno luego quizas
            tipo = types.TYPE_MOVIE_THEATER # Equivalente a: tipo = ['movie_theater']

            ########################################################### 
            # Comunicar con buscador
            print "Los parametros de vuelo"
            #############################################################
            originVuelo=gm.value(subject= peticion, predicate= myns_atr.originVuelo)

            destinationVuelo=gm.value(subject= peticion, predicate= myns_atr.destinationVuelo)

            departureDate=gm.value(subject= peticion, predicate= myns_atr.departureDate)

            returnDate=gm.value(subject= peticion, predicate= myns_atr.returnDate)

            maxPrice=gm.value(subject= peticion, predicate= myns_atr.maxPrice)

            grep = comu()

    print 'Respondemos a la peticion\n'
    ########################################################### 
    # Construir mensage de repuesta
    print "Retornar repuesta"
    #############################################################
    return grep.serialize(format='xml')


@app.route("/Stop")
def stop():
    """
    Entrypoint que para el agente

    :return:
    """
    tidyup()
    shutdown_server()
    return "Parando Servidor"


def tidyup():
    """
    Acciones previas a parar el agente

    """
    pass


def agentbehavior1(cola):
    """
    Un comportamiento del agente

    :return:
    """
    pass

#def message_buscador():
#    """
#
#    """
#    gmess = Graph()
#
    # Construimos el mensaje de registro
#    gmess.bind('amo', AMO)
#    bus_obj = agn[AgentePlanificador.name + '-Request']
#    gmess.add((bus_obj, AMO.requestType, Literal('Actividad')))

    # Lo metemos en un envoltorio FIPA-ACL y lo enviamos
#    gr = send_message(
#        build_message(gmess, perf=ACL.request,
#                      sender=AgentePlanificador.uri,
#                      receiver=AgenteBuscador.uri,
#                      content=bus_obj,
#                      msgcnt=mss_cnt),
#        AgenteBuscador.address)

#    return gr

def comu():

    global mss_cnt 
    # Graph para buscador
    gmess = Graph()
    gmess.bind('myns_pet', myns_pet)
    gmess.bind('myns_atr', myns_atr)

    ########################################################### 
    # Comunicar con buscador
    print "Los parametros hardcoreado"
    #############################################################

    
    destination = "Madrid, Spain"
    activity="Movie"
    radius = 20000
    departureDate = datetime.date(2015, 9, 8)
    returnDate = datetime.date(2015, 9, 20)
    tipo = types.TYPE_MOVIE_THEATER 

    originVuelo="BCN"
    destinationVuelo="PRG"
    departureDate="2015-06-02"
    returnDate="2015-06-08"
    maxPrice='EUR500'
    ########################################################### 
    # Mejorar preferencia de busqueda
    print "Mejorar preferencia de busqueda"
    #############################################################

    ########################################################### 
    # Comunicar con buscador
    print "Iniciar la comunicaion con buscador"
    #############################################################
    
    # Hago bind de las ontologias que voy a usar en el grafo
    # Estas ontologias estan definidas arriba (abajo de los imports)
    # Son las de peticiones y atributos (para los predicados de la tripleta)

    # Sujeto de la tripleta: http://my.namespace.org/peticiones/actividad
    # O sea, el mensaje sera una peticion de actividad
    # El buscador tendra que ver que tipo de peticion es
    ########################################################### 
    # Comunicar con buscador
    print "Añadir parametros de actividad"
    #############################################################
    # Paso los parametros de busqueda de actividad en el grafo
    actv = myns_pet.actividad
    gmess.add((actv, myns_atr.lugar, Literal(destination)))
    gmess.add((actv, myns_atr.actividad, Literal(activity)))
    gmess.add((actv, myns_atr.radio, Literal(radius)))
    gmess.add((actv, myns_atr.tipo, Literal(tipo)))
    
    ########################################################### 
    # Comunicar con buscador
    print "Añadir parametros de actividad"
    #############################################################
    vuelo = myns_pet.vuelo
    gmess.add((vuelo, myns_atr.originVuelo, Literal(originVuelo)))
    gmess.add((vuelo, myns_atr.destinationVuelo, Literal(destinationVuelo)))
    gmess.add((vuelo, myns_atr.departureDate, Literal(departureDate)))
    gmess.add((vuelo, myns_atr.returnDate, Literal(returnDate)))          
    gmess.add((vuelo, myns_atr.maxPrice, Literal(maxPrice))) 



    # Uri asociada al mensaje sera: http://www.agentes.org#Planificador-pide-actividades
    res_obj= agn['Planificador-pide-datos']

    # Construyo el grafo y lo mando (ver los metodos send_message y build_message
    # en ACLMessages para entender mejor los parametros)
    print "INFO AgentePlanificador=> Sending request to AgenteBuscador\n"
    gr = send_message(build_message(gmess, 
                       perf=ACL.request, 
                       sender=AgentePlanificador.uri, 
                       receiver=AgenteBuscador.uri,
                       content=res_obj,
                       msgcnt=mss_cnt 
                       ),
        AgenteBuscador.address)
    print "Respuesta de busqueda recibida\n"
    
    
    
    for s, p, o in gr:
        print 's: ' + s
        print 'p: ' + p
        print 'o: ' + o
        print '\n'

    ########################################################### 
    # Calcular paquete
    print "Calcular paquete"
    #############################################################   

    grep = Graph()

    ########################################################### 
    # Calcular paquete
    print "Calcular Vuelos"
    #############################################################    

    gvueloid = gr.query("""
                PREFIX myns_atr: <http://my.namespace.org/atributos/>
                SELECT DISTINCT ?a ?cuesta
                WHERE{
                    ?a myns_atr:cuesta ?cuesta .
                    FILTER(str(?cuesta) != "")
                }
                ORDER BY (?cuesta)
                LIMIT 1
        """)
    Aid = []
    for s in gvueloid
        Aid.append(s)

    grep += gr.triples((Aid[0], None, None))


    #Actividades 
    ########################################################### 
    # Calcular paquete
    print "Calcular Actividades"
    #############################################################           

    gact = gr.query("""
                PREFIX myns_atr: <http://my.namespace.org/atributos/>
                SELECT DISTINCT ?a ?ratin
                WHERE{
                    ?a myns_atr:rating ?ratin .
                    FILTER(str(?ratin) != "")
                }
                ORDER BY DESC(?ratin)
        """)

    Acs = []
    for s, s1 in gact:
        Acs.append(s)

    ########################################################### 
    # Escoger Actividades
    print "Escoger Actividades"
    #############################################################   
    day = departureDate
    contadorActividad = 0
    while day <= returnDate:
       # cada dia
        grfdata = myns_data.day
    
    if contadorActividad > (len(Acs)-3) :
        contadorActividad = 0
    ########################################################### 
    # Escoger Actividades
    print "Escoger Actividades1" 
    print Acs[contadorActividad]
    #############################################################
    # manana
    grep.add((grfdata, myns_data.actividades, Acs[contadorActividad]))
    ########################################################### 
    # Escoger Actividades
    print "Actividades1 Anadido"
    #############################################################                
    grep.add((Acs[contadorActividad], myns_atr.momento, myns_atr.manana))

    grep += gr.triples((Acs[contadorActividad], None, None))
    
    ########################################################### 
    # Escoger Actividades
    print "Actividades1 por manana"
    #############################################################
    contadorActividad += 1;
    ########################################################### 
    # Escoger Actividades
    print "Escoger Actividades2"
    #############################################################
    # tarde
    grep.add((grfdata,myns_data.actividades, Acs[contadorActividad]))
    grep.add((Acs[contadorActividad], myns_atr.momento, myns_atr.tarde))
    grep += gr.triples((Acs[contadorActividad], None, None))
    contadorActividad += 1;
    ########################################################### 
    # Escoger Actividades
    print "Escoger Actividades3"
    #############################################################
    # noche
    grep.add((grfdata,myns_data.actividades, Acs[contadorActividad]))
    grep.add((Acs[contadorActividad], myns_atr.momento, myns_atr.noche))
    grep += gr.triples((Acs[contadorActividad], None, None))
    contadorActividad += 1;

    day = day + datetime.timedelta(days=1)

    print departureDate

    ########################################################### 
    # Construir mensage de repuesta
    print "Construir mensage de repuesta"
    #############################################################
    for s, p, o in grep:
        print 's: ' + s
        print 'p: ' + p
        print 'o: ' + o
        print '\n'
        mss_cnt += 1

    return grep


if __name__ == '__main__':

    # Ponemos en marcha los behaviors
    ab1 = Process(target=agentbehavior1, args=(cola1,))
    ab1.start()
    ###################################################
    # Inicio de peticion de ACTIVIDADES a AgentBuscador
    ###################################################

    # # Creo el grafo sobre el que mando los parametros de busqueda
    # gmess = Graph()
    # # Hago bind de las ontologias que voy a usar en el grafo
    # # Estas ontologias estan definidas arriba (abajo de los imports)
    # # Son las de peticiones y atributos (para los predicados de la tripleta)
    # gmess.bind('myns_pet', myns_pet)
    # gmess.bind('myns_atr', myns_atr)

    # # Parametros de la peticion de actividades
    # # Luego habra que sustituirlos por los que obtengo del planificador
    # location = 'Barcelona, Spain'
    # activity = 'movie'
    # radius = 20000
    # # De momento solo permitimos pasar un tipo. Ampliar a mas de uno luego quizas
    # tipo = types.TYPE_MOVIE_THEATER # Equivalente a: tipo = ['movie_theater']

    # # Sujeto de la tripleta: http://my.namespace.org/peticiones/actividad
    # # O sea, el mensaje sera una peticion de actividad
    # # El buscador tendra que ver que tipo de peticion es
    # actv = myns_pet.actividad

    # # Paso los parametros de busqueda de actividad en el grafo
    # gmess.add((actv, myns_atr.lugar, Literal(location)))
    # gmess.add((actv, myns_atr.actividad, Literal(activity)))
    # gmess.add((actv, myns_atr.radio, Literal(radius)))
    # gmess.add((actv, myns_atr.tipo, Literal(tipo)))

    # # Uri asociada al mensaje sera: http://www.agentes.org#Planificador-pide-actividades
    # res_obj= agn['Planificador-pide-actividades']

    # # Construyo el grafo y lo mando (ver los metodos send_message y build_message
    # # en ACLMessages para entender mejor los parametros)
    # print "INFO AgentePlanificador=> Sending request to AgenteBuscador\n"
    # gr = send_message(build_message(gmess, 
    #                    perf=ACL.request, 
    #                    sender=AgentePlanificador.uri, 
    #                    receiver=AgenteBuscador.uri,
    #                    content=res_obj,
    #                    msgcnt=mss_cnt 
    #                    ),
    #     AgenteBuscador.address)

    # # Ahora en gr tengo la respuesta de la busqueda con las actividades

    # # VERBOSE
    # # Con esto podemos coger todos los nombres de lasa actividades del grafo
    # # para poder coger los atributos de cada actividad
    # nombres = list()
    # for s, p, o in gr:
    #     if p == myns_atr.nombre:
    #         nombres.append(s)
    # print nombres

    # # VERBOSE
    # # Imprimo la respuesta por pantalla para ver lo que devuelve
    # # Luego en verdad esto se pasa al algoritmo del planificador
    # print "INFO AgentePlanificador => Response: \n"
    # for s, p, o in gr:
    #     print 's: ' + s
    #     print 'p: ' + p
    #     print 'o: ' + o
    #     print '\n'

    # VERBOSE
    # Descomentar para un print "pretty" del grafo de respuesta
    # print json.dumps(gr.json(), indent=4, sort_keys=True)
    grep = comu()

    # Ponemos en marcha el servidor
    app.run(host=hostname, port=port)

    # Esperamos a que acaben los behaviors
    #   ab1.join()

    print 'INFO AgentePlanificador => The End'


