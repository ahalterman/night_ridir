from petrarch2 import petrarch2, PETRglobals, PETRreader, PETRtree, utilities
from ConfigParser import ConfigParser
from flask import jsonify, make_response
from flask.ext.httpauth import HTTPBasicAuth
from flask.ext.restful import Resource, reqparse
from flask.ext.restful.representations.json import output_json
import os

config = "/app/resources/PETR_config.ini"
PETRreader.parse_Config(config)
petrarch2.read_dictionaries()

class PhraseExtractAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('text', type=unicode, location='json')
        self.reqparse.add_argument('parse', type=unicode, location='json')
        super(PhraseExtractAPI, self).__init__()

    def get(self):
        return """ This service expects a POST in the form '{"text":""Airstrikes 
    and artillery...", "parse" : "(ROOT (S (S (NP (NP (NNP Airstrikes)) 
    (CC and) (NP (NN artillery)))..."}' It will return a list of nouns and verbs...TBD"""

    def post(self):
        args = self.reqparse.parse_args()
        print args
        text = args['text']
        parse = args['parse']
        output = self.get_phrases(text, parse)
        return output

    def get_phrases(self, text, parse):
        parsed = utilities._format_parsed_str(parse)

        ddict = {u'test123':
                {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
                 u'meta': {u'date': u'20010101'}}}
        return_dict = petrarch2.do_coding(ddict, None)
        
        n = return_dict['test123']['meta']['verbs']['nouns']
        nouns = [i[0] for i in n]
        noun_coding = [i[1] for i in n]
        try:
            verbs = return_dict['test123']['meta']['verbs']['eventtext'].values()[0]
        except KeyError:
            print "No eventtext"
            verbs = ""
        try:
            verb_coding = return_dict['test123']['meta']['verbs']['eventtext'].keys()[0][2]
        except KeyError as e:
            print e
            verb_coding = ""
        phrase_dict = {"nouns" : nouns,
                       "noun_coding" : noun_coding,
                      "verbs" : verbs,
                      "verb_coding" : verb_coding}
        return(phrase_dict)
