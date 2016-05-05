from petrarch2 import petrarch2, PETRglobals, PETRreader, PETRtree, utilities
from ConfigParser import ConfigParser
from flask import jsonify, make_response
from flask.ext.httpauth import HTTPBasicAuth
from flask.ext.restful import Resource, reqparse
from flask.ext.restful.representations.json import output_json

config = utilities._get_data('data/config', 'PETR_config.ini')
PETRreader.parse_Config(config)
petrarch2.read_dictionaries()

class PhraseExtractAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('text', type=unicode, location='json')
        super(CountryAPI, self).__init__()

    def get(self):
        return """ This service expects a POST in the form '{"text":""Airstrikes 
    and artillery...", "parse" : "(ROOT (S (S (NP (NP (NNP Airstrikes)) 
    (CC and) (NP (NN artillery)))..."}' It will return a list of nouns and verbs...TBD"""

    def post(self):
        args = self.reqparse.parse_args()
        text = args['text']
        parse = args['parse']
        output = self.get_phrases(text, parse)
        return output

    def get_phrases(text, parse):
        parsed = utilities._format_parsed_str(parse)

        ddict = {u'test123': 
                {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
                 u'meta': {u'date': u'20010101'}}}

        return_dict = petrarch2.do_coding(ddict, None)
        nouns = return_dict['test123'][u'meta'][u'verbs'][u'nouns']
        k = return_dict['test123'][u'meta'][u'verbs'].keys()
        t = [i for i in k if i != 'nouns']
        if t:
            verbs = [return_dict['test123'][u'meta'][u'verbs'][i][0] for i in t]
        else:
            verbs = ""
        return {"nouns": nouns,
               "verbs" : verbs}


