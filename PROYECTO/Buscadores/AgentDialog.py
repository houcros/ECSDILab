from multiprocessing import Process, Queue
import socket
import gzip
import argparse

from flask import Flask, request , redirect
from flask import render_template
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import FOAF, RDF

from AgentUtil.OntoNamespaces import ACL, DSO , TIO
from AgentUtil.FlaskServer import shutdown_server
from AgentUtil.ACLMessages import build_message, send_message, get_message_properties
from AgentUtil.Agent import Agent
from AgentUtil.Logging import config_logger

from flask.ext.wtf import Form
from wtforms import Form, BooleanField, TextField, PasswordField, StringField, DateField, IntegerField, validators
from wtforms.validators import DataRequired

class MyForm (Form):
    cityDestination = StringField ('City of Destination', validators=[DataRequired()])
    cityOrigin = StringField ('City of Origin', validators=[DataRequired()])

    departureDate = DateField ('Departure date', format='%y - %m - %d', validators=[DataRequired()])
    returnDate = DateField ('Return date', format='%y - %m - %d', validators=[DataRequired()])

    maxPrice = IntegerField ('Max. Price',validators=[DataRequired()])
    numberOfStars = IntegerField ('Number of Stars', validators=[DataRequired()])
    activities = StringField ('activities', validators=[DataRequired()])

#He tenido que copiar esta variable global porque sino me petaba
AMO = Namespace('http://www.semanticweb.org/houcros/ontologies/2015/4/agentsMessages')

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

plan_port = 9002

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
AgenteDialog = Agent('AgentDialog',
                  agn.AgentDialog,
                  'http://%s:%d/comm' % (hostname, port),
                  'http://%s:%d/Stop' % (hostname, port))

AgentePlanificador = Agent('AgentePlanificador',
                       agn.AgentePlanificador,
                       'http://%s:%d/comm' % (hostname, plan_port),
                       'http://%s:%d/Stop' % (hostname, plan_port))

# Directory agent address
DirectoryAgent = Agent('DirectoryAgent',
                       agn.Directory,
                       'http://%s:%d/Register' % (dhostname, dport),
                       'http://%s:%d/Stop' % (dhostname, dport))

# Global dsgraph triplestore
dsgraph = Graph()

# Cola de comunicacion entre procesos
cola1 = Queue()

agn = Namespace("http://www.agentes.org#")
nm = Namespace("http://www.agentes.org/actividades/")
myns = Namespace("http://my.namespace.org/")
myns_pet = Namespace("http://my.namespace.org/peticiones/")
myns_atr = Namespace("http://my.namespace.org/atributos/")
myns_act = Namespace("http://my.namespace.org/actividades/")
myns_lug = Namespace("http://my.namespace.org/lugares/")

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    return render_template('submit.html')


@app.route("/main", methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        return redirect('/submit')
    else:
        if request.args:
            return "Argsss"
        else:
            form = MyForm()
            return render_template('main.html', form=form)


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

    # gr = build_message(gmess, perf=ACL.request,
    #                   sender=AgentePlanificador.uri,
    #                   receiver=AgenteBuscador.uri,
    #                   content=bus_obj,
    #                   msgcnt=mss_cnt),
    #     AgenteBuscador.address)


    res_obj= agn['Planificador-responde']
    gr = Graph()
    gr.add((res_obj, DSO.AddressList,  Literal(cont)))
    gr = build_message(gr, 
					   ACL.inform, 
					   sender=AgentBuscador.uri, 
					   content=res_obj,
					   msgcnt=mss_cnt 
					   )
    resp = gr.serialize(format='xml')
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


def message_dialogador():
    #Preguntamos al usuario sus preferencias 
    print ('Welcome to Bestrip! The best trip search engine in the world!' + '\n')
    print ('Please, answer these questions to find your trip!' + '\n')

    # cityDestination = raw_input ('Where do you want to go?' + '\n')
    # cityOrigin = raw_input ('Where are you?' + '\n')
    # departureDate = raw_input ('When do you want to go? (Format : dd/mm/yyyy)' + '\n' )
    # returnDate = raw_input ('When do you want to return? (Format : dd/mm/yyyy)' + '\n' )
    # maxPrice = raw_input('Which is the maximum price that a trip must have?' + '\n')
    # numberOfStars = raw_input ('How many stars the hotel must have ?' + '\n')
    # activities = raw_input ('Tell us about the kind of activities you like! (Format:separate using commas for each preference)' + '\n')
    # transport = raw_input ('Would you like to use public transport during your trip? (Yes / No)' + '\n')

    ###############################################################
    cityOrigin = "Barcelona, Spain"
    cityDestination = "Madrid, Spain"
    departureDate = "08/09/2015"
    returnDate = "20/09/2015"
    maxPrice = 500
    numberOfStars = 3
    #activities = "Cinema, Teatro, Museo"
    activities = "Movie"
    transport = "True"
    ##############################################################################

    print ('Thank you very much, finding the best trip according to your preferences ... ' + '\n')

    #cont = city + "#" + departureDate + "#" + returnDate + "#" + maxPrice + "#" + numberOfStars + "#" + activities + "#" + transport 

    gmess = Graph()
    gmess.bind('myns_pet', myns_pet)
    gmess.bind('myns_atr', myns_atr)

    peticion = myns_pet["Dialogador-pide-paquete"]

    gmess.add((peticion, myns_atr.origin, Literal(cityOrigin)))
    gmess.add((peticion, myns_atr.destination, Literal(cityDestination)))
    gmess.add((peticion, myns_atr.departureDate, Literal(departureDate)))
    gmess.add((peticion, myns_atr.returnDate, Literal(returnDate)))
    gmess.add((peticion, myns_atr.maxPrice, Literal(maxPrice)))
    gmess.add((peticion, myns_atr.numberOfStars, Literal(numberOfStars)))
    #for a in activities
    gmess.add((peticion, myns_atr.activities, Literal(activities)))
    gmess.add((peticion, myns_atr.useTransportPublic, Literal(transport)))

    



    # # Construimos el mensaje de registro
    gmess.bind('amo', AMO)
    bus_obj = agn[AgenteDialog.name + '-Request']
    gmess.add((bus_obj, AMO.requestType, Literal('Actividad')))

    # Lo metemos en un envoltorio FIPA-ACL y lo enviamos
    gr = send_message(
        build_message(gmess, perf=ACL.request,
                      sender=AgenteDialog.uri,
                      receiver=AgentePlanificador.uri,
                      content=bus_obj,
                      msgcnt=mss_cnt),
        AgentePlanificador.address)

    return gr


if __name__ == '__main__':
    # Ponemos en marcha los behaviors
    #ab1 = Process(target=agentbehavior1, args=(cola1,))
    #ab1.start()
    cont = message_dialogador();
   
    # Ponemos en marcha el servidor
    app.run(host=hostname, port=port)

    # Esperamos a que acaben los behaviors
    #ab1.join()
    logger.info('The End')