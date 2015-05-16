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

print ('Welcome to Bestrip! The best trip search engine in the world!' + '\n')
print ('Please, answer these questions to find your trip!' + '\n')

city = raw_input ('Where do you want to go?' + '\n')
departureDate = raw_input ('When do you want to go? (Format : dd/mm/yyyy)' + '\n' )
returnDate = raw_input ('When do you want to return? (Format : dd/mm/yyyy)' + '\n' )
maxPrice = raw_input('Which is the maximum price that a trip must have?' + '\n')
numberOfStars = raw_input ('How many stars the hotel must have ?' + '\n')
activities = raw_input ('Tell us about the kind of activities you like! (Format:separate using commas for each preference)' + '\n')
transport = raw_input ('Would you like to use public transport during your trip? (Yes / No)' + '\n')

print ('Thank you very much, finding the best trip according to your preferences ... ' + '\n')
