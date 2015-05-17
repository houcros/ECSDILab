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
from AgentUtil.OntoNamespaces import AMO, ACL, DSO
from rdflib.namespace import FOAF
from AgentUtil.Logging import config_logger
from googleplaces import types
import json

# Configuration stuff
hostname = socket.gethostname()
port = 9010
bport = 9001

agn = Namespace("http://www.agentes.org#")

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
                       'http://%s:%d/comm' % (hostname, bport),
                       'http://%s:%d/Stop' % (hostname, bport))

# Directory agent address
DirectoryAgent = Agent('DirectoryAgent',
                       agn.Directory,
                       'http://%s:9000/Register' % hostname,
                       'http://%s:9000/Stop' % hostname)


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
            if 'content' in msgdic:
                content = msgdic['content']
                accion = gm.value(subject=content, predicate=RDF.type)

            # Aqui realizariamos lo que pide la accion
            # Por ahora simplemente retornamos un Inform-done
            gr = build_message(Graph(),
                ACL['inform-done'],
                sender=AgentePlanificador.uri,
                msgcnt=mss_cnt,
                receiver=msgdic['sender'], )
    mss_cnt += 1

    print 'Respondemos a la peticion\n'

    return gr.serialize(format='xml')


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

def message_buscador():
    """

    """
    gmess = Graph()

    # Construimos el mensaje de registro
    gmess.bind('amo', AMO)
    bus_obj = agn[AgentePlanificador.name + '-Request']
    gmess.add((bus_obj, AMO.requestType, Literal('Actividad')))

    # Lo metemos en un envoltorio FIPA-ACL y lo enviamos
    gr = send_message(
        build_message(gmess, perf=ACL.request,
                      sender=AgentePlanificador.uri,
                      receiver=AgenteBuscador.uri,
                      content=bus_obj,
                      msgcnt=mss_cnt),
        AgenteBuscador.address)

    return gr


if __name__ == '__main__':
    # Ponemos en marcha los behaviors
    ab1 = Process(target=agentbehavior1, args=(cola1,))
    ab1.start()

    # Peticion de actividades a AgentBuscador
    # Hacen falta todos estos binds? Comprobarlo
    gmess = Graph()
    gmess.bind('amo', AMO)
    gmess.bind('foaf', FOAF)
    gmess.bind('dso', DSO)
    nm = Namespace("http://www.agentes.org/actividades/")
    myns = Namespace("http://my.namespace.org/lugares/")
    gmess.bind('myns', myns)

    res_obj= agn['Planificador-pide-actividades']
    # TESTING gmess. Cambiar por los parametros de busqueda

    location = 'Barcelona, Spain'
    activity = 'movie'
    radius = 20000
    #types = [types.TYPE_MOVIE_THEATER]
    #types = list()

    plc = nm.place
    gmess.add((plc, myns.lugar, Literal(location)))
    gmess.add((plc, myns.actividad, Literal(activity)))
    gmess.add((plc, myns.radio, Literal(radius)))
    gmess.add((plc, myns.tipos, Literal(types)))

    gr = send_message(build_message(gmess, 
                       perf=ACL.request, 
                       sender=AgentePlanificador.uri, 
                       receiver=AgenteBuscador.uri,
                       content=res_obj,
                       msgcnt=mss_cnt 
                       ),
        AgenteBuscador.address)

    print "Sent request to AgenteBuscador\n"
    print "Response: \n"
    for s, p, o in gr:
        print 's: ' + s
        print 'p: ' + p
        print 'o: ' + o
        print '\n'
    #print json.dumps(gr.json(), indent=4, sort_keys=True)

    # Ponemos en marcha el servidor
    app.run(host=hostname, port=port)

    # Esperamos a que acaben los behaviors
    #   ab1.join()

    #gr = message_buscador()
    #for a, b, c in gr:
    #  print a, c

    print 'The End'


