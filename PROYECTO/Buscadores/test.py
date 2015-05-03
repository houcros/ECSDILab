
import socket
import argparse
import requests
from flask import Flask, request
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import FOAF, RDF

from AgentUtil.OntoNamespaces import ACL, DSO
from AgentUtil.FlaskServer import shutdown_server
from AgentUtil.ACLMessages import build_message, send_message, get_message_properties
from AgentUtil.Agent import Agent
from AgentUtil.Logging import config_logger
hostname = socket.gethostname()
port = 9001

address = 'http://%s:%d/comm' % (hostname, port)
r = requests.get(address, params={'content': "/iface"})


print r.content
