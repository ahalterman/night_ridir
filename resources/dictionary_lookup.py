from gensim.models import Word2Vec
import re
from flask import jsonify, make_response
from flask.ext.httpauth import HTTPBasicAuth
from flask.ext.restful import Resource, reqparse
from flask.ext.restful.representations.json import output_json
import json
import ast # de-string incoming list
import itertools
import io
import sys

PETRglobals_WriteActorRoot = True
PETRglobals_ActorDict = {}

class DictionaryLookupAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('syns', type=unicode, location='json')
        self.ActorDict = self.read_actor_dictionary("/app/resources/Phoenix.Countries.actors.txt")
        super(DictionaryLookupAPI, self).__init__()

    def get(self):
        return """This service takes in the output of /get_synonyms as input and returns possible matches from the OEDA event data dictionaries."""

    def post(self):
        args = self.reqparse.parse_args()
        print args
        x = args['syns']
        syns = ast.literal_eval(x)
        matches = self.syns_to_dict(syns)
        return matches
    
    def syns_to_dict(self, syns):
        matches = []
        for s in syns[0:10]:
            syn_split = s.split("_")
            o = self.recurse(PETRglobals_ActorDict, syn_split)
            if o:
                matches.append(o)
        return matches
 
    # This is done in a different endpoint. word2vec is so big that I don't want to load it twice.
    # Instead, for now, users will have to pass in the output of self.get_syns
    #def syns_to_dict(self, word):
    #    if not isinstance(word, list):
    #    word = [word]
    #    syns = self.get_syns(word)
    #    print syns
    #    matches = []
    #    for s in syns[0:10]:
    #        syn_split = s.split("_")
    #        o = self.recurse(PETRglobals_ActorDict, syn_split)
    #        if o:
    #            matches.append(o)
    #    # what happens if there are no matches?
    #    # we try the last word alone
    #    if not matches and len(word) == 1:
    #        split_word = word[0].split("_")
    #        if len(split_word) > 1:
    #            sw = [split_word[-1]]
    #            syns = self.get_syns(sw)
    #            print syns
    #            for s in syns[0:10]:
    #                syn_split = s.split("_")
    #                o = recurse(PETRglobals_ActorDict, syn_split)
    #                if o:
    #                    matches.append(o)
    #    return matches

    def recurse(self, actor_dict, terms):
        try:
            new_dict = actor_dict[terms[0]]
            terms = terms[1:]
            nd = []
            try:
                nd = new_dict["#"]
                return nd
            except KeyError:
                nd = self.recurse(new_dict, terms)
            return nd
        except KeyError:
            pass
        except IndexError:
            pass # IndexError: list index out of range: new_dict = actor_dict[terms[0]]
    
    # all code below is (lightly modified and) taken from https://github.com/openeventdata/petrarch2/
    def open_FIN(self, filename, descrstr):
        # opens the global input stream fin using filename;
        # descrstr provides information about the file in the event it isn't found
        global FIN
        global FINline, FINnline, CurrentFINname
        try:
            FIN = io.open(filename, 'r', encoding='utf-8')
            CurrentFINname = filename
            FINnline = 0
        except IOError:
            print("\aError: Could not find the", descrstr, "file:", filename)
            print("Terminating program")
            sys.exit()
    
    
    def close_FIN(self):
        # closes the global input stream fin.
        # IOError should only happen during debugging or if something has seriously gone wrong
        # with the system, so exit if this occurs.
        global FIN
        try:
            FIN.close()
        except IOError:
            print("\aError: Could not close the input file")
            print("Terminating program")
            sys.exit()
    
    
    def read_FIN_line(self):
        global FIN
        global FINline, FINnline
    
        line = FIN.readline()
        FINnline += 1
        while True:
            #		print '==',line,
            if len(line) == 0:
                break  # calling function needs to handle EOF
            # deal with simple lines we need to skip
            if line[0] == '#' or line[0] == '\n' or line[
                    0:2] == '<!' or len(line.strip()) == 0:
                line = FIN.readline()
                FINnline += 1
                continue
            if not line:  # handle EOF
                print("EOF hit in read_FIN_line()")
                raise EOFError
                return line
            if ('#' in line):
                line = line[:line.find('#')]
            if ('<!--' in line):
                if ('-->' in line):  # just remove the substring
                    pline = line.partition('<!--')
                    line = pline[0] + pline[2][pline[2].find('-->') + 3:]
                else:
                    while ('-->' not in line):
                        line = FIN.readline()
                        FINnline += 1
                    line = FIN.readline()
                    FINnline += 1
            if len(line.strip()) > 0:
                break
            line = FIN.readline()
            FINnline += 1
    #	print "++",line
        FINline = line
        return line

    def read_actor_dictionary(self, actorfile):
        """ This is a simple dictionary of dictionaries indexed on the words in the actor string. The final node has the
            key '#' and contains codes with their date restrictions and, optionally, the root phrase in the case
            of synonyms. 
            Example: 
            UFFE_ELLEMANN_JENSEN_  [IGOEUREEC 820701-821231][IGOEUREEC 870701-871231] # president of the CoEU from DENMARK# IGOrulers.txt
            
            the actor above is stored as:
            {u'UFFE': {u'ELLEMANN': {u'JENSEN': {u'#': [(u'IGOEUREEC', [u'820701', u'821231']), (u'IGOEUREEC', [u'870701', u'871231'])]}}}}
            """
    
        self.open_FIN(actorfile, "actor")
    
        line = self.read_FIN_line().strip()
        current_acts = []
        datelist = []
        while len(line) > 0:
            if line[0] == '[':  # Date
                data = line[1:-1].split()
                code = data[0]
                try:
                    if '-' in data[1]:
                        dates = data[1].split('-')
                    else:
                        dates = [data[1]]
                except:
                    dates = []
                datelist.append((code, dates))
            else:
                if line[0] == '+':  # Synonym
                    actor = line[1:].replace("_", ' ').split()
                else:  # Base actor
                    # add previous actor entry to dictionary:
                    if PETRglobals_WriteActorRoot and len(
                            current_acts) > 0:  # store the root phrase if we're only to use it
                        datelist.append(current_acts[0])
                    for targ in current_acts:
                        list = PETRglobals_ActorDict
                        while targ != []:
                            if targ[0] in [' ', '']:
                                targ = targ[1:]
                                continue
                            if not isinstance(list, dict):
                                print("BADNESS", list)
                                exit()
                            list = list.setdefault(targ[0], {})
                            targ = targ[1:]
                        list["#"] = datelist
    
                    datelist = []  # reset for the new actor
                    current_acts = []
                    temp = line.split('\t')
                    if len(temp)==1:
                        temp = line.split("  ")
                    if len(temp)>1:
                        datestring = temp[1].strip().replace("\n","").split(']')
                        for i in range(len(datestring)):
                            if len(datestring[i])==0:
                                continue
    
                            data = datestring[i][datestring[i].find('[')+1:].split()
                            code = data[0].replace(']','')
    
                            try:
                                date = data[1].replace(']','')
                                if '-' in date:
                                    dates = date.split('-')
                                else:
                                    dates = [date]
                            except:
                                dates = []
    
                            datelist.append((code, dates))
    
                    #print(datelist) 
                    actor = temp[0].replace("_", ' ').split()
                current_acts.append(actor)
    
            line = self.read_FIN_line().strip()
    
