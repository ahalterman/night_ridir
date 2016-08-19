# night_ridir
Containerized tools for event data dictionary development, including:

- noun and verb extraction, using the `/get_phrases` endpoint
- automated word2vec "synonym" discovery with the `/get_synonyms` endpoint
- checking OEDA actor dictionaries for near-matches

Docker Setup
-------

From inside this directory, you can build the image by running

```
sudo docker build -t nr_tools .
```
(Note the trailing period).

Then run it on port 5000 with
```
docker run -d -p 5000:5000 nr_tools
```

Endpoints
-------

A GET request to each synonym returns usage information.

- `/get_phrases` : Given text and CoreNLP parses, return noun and verb phrases that are candidate dictionary entries
- `/get_synonyms` : Given an English word or words, find possible synonyms using word2vec
- `/get_synonyms_ar` : Same as above, but using an Arabic word2vec model trained on Wikipedia
- `/lookup_dictionary` : Given a list of synonyms, check if any match existing entries in the actor dictionaries.

Examples
-------

### Phrase extraction

Pass a sentence and its CoreNLP parse to get back phrases and codings (if applicable):

```
curl -XPOST -H "Content-Type: application/json" --data '{"text" : "Hundreds of Egyptian journalists rallied in Cairo on Wednesday in an escalating standoff with police, threatening a possible strike by media workers if demands including the dismissal of the interior minister are not met.", "parse" : "(ROOT (S (NP (NP (NNS Hundreds)) (PP (IN of) (NP (JJ Egyptian) (NNS journalists)))) (VP (VBD rallied) (PP (IN in) (NP (NNP Cairo))) (PP (IN on) (NP (NNP Wednesday))) (PP (IN in) (NP (NP (DT an) (VBG escalating) (NN standoff)) (PP (IN with) (NP (NN police))))) (, ,) (S (VP (VBG threatening) (NP (DT a) (JJ possible) (NN strike)) (PP (IN by) (NP (NNS media) (NNS workers))) (SBAR (IN if) (S (NP (NP (NNS demands)) (PP (VBG including) (NP (NP (DT the) (NN dismissal)) (PP (IN of) (NP (DT the) (JJ interior) (NN minister)))))) (VP (VBP are) (RB not) (VP (VBN met)))))))) (. .)))"}' 'http://localhost:5000/get_phrases'
```

should return

```
{"verbs": "rallied", 
"noun_coding": [["EGYMED"], ["EGY"], ["~COP"], ["~COP"], ["~MEDLAB"], ["~GOV"], ["~GOV"], ["~GOV"]], 
"nouns": [[" EGYPTIAN", " JOURNALISTS"], [" CAIRO"], [" POLICE"], [" POLICE"], [" MEDIA", " WORKERS"], [" INTERIOR MINISTER"], [" INTERIOR MINISTER"], [" INTERIOR MINISTER"]], 
"verb_coding": "150"}
```

### Synonyms

Pass a list of word(s) to get their word2vec synonyms:

```
curl -XPOST -H "Content-Type: application/json" --data '{"text" : ["artillery"]}' 'http://localhost:5000/get_synonyms'
```

Expect a list of "synonyms" back:

``` 
["BRITISH_TROOPS", "FORCES_IN", "WAR_WITH", "ANTIAIRCRAFT",
"ARTILLERY_BOMBARDMENT", "MACHINEGUN_FIRE", "MORTAR_PLATOON",
"CARPATHIAN_FOREST", "TARGETED_BY", "AIR_STRIKES", "WARPLANES", "ANTITANK",
"DRAGOON_GUARDS", "ARTILLERY_BARRAGES", "LEGION_OF", "ORDNANCE", "IN_KASHMIR",
"SPECIAL_OPERATIONS", "MM_HOWITZER", "SHELLFIRE", "ARTILLERY",
"ARTILLERY_SHELLS", "CANNONEERS", "BLAST_KILLS", "ARMY_AND", "HOWITZERS",
"##MM_CANNON", "ARTILLERY_REGIMENT", "FIELD_ARTILLERY", "CAVALRY",
"SWEDISH_METALLERS", "INFANTRY", "ARTILLERY_MORTARS", "ARTILLERIES",
"FRONTMAN", "REGIMENT", "ARTILLERY_BARRAGE", "PARACHUTE_REGIMENT",
"ARMOURED_REGIMENT", "RIFLES", "MORTARS", "ARMY_ORDNANCE",
"ARTILLERY_SHELLING", "ARTILLERY_BRIGADE", "MISSILES", "###MM_HOWITZERS",
"BC_AS_GEN", "MORTAR", "TANKS_ARTILLERY", "ARTILLERY_BATTALION", "KHYBER",
"CAR_BOMB", "DRONE", "BOMBARDMENT"]
```

### Dictionary duplicate finder

When updating dictionaries, coders will often come across an alternative
version of an actor that's already in the dictionaries (e.g., "Obama" instead
of "Barack Obama"). `night_rider` can help match the new form of a name to an
existing dictionary entry. First, get possible synonyms of the new term using
`/get_synonyms`. Then, pass that list of synonyms to `/lookup_dictionary` to
see if any of them have matches in the existing dictionaries and return the
corresponding entries. Example usage:

```
curl -XPOST -H "Content-Type: application/json" --data '{"syns": ["BARACK_OBAMA", "OBAMA"]}' 'http://localhost:5000/lookup_dictionary'
```

returns

```
[[["USAELI", ["780101", "000101"]], ["USAGOV", [">090120"]], ["BARACK", "OBAMA"]], [["USAELI", ["780101", "000101"]], ["USAGOV", [">090120"]], ["BARACK", "OBAMA"]]]
```

The response is a list of lists, where each sub-list contains one role entries
for the matched actor, with the canonical name form being the final element.
