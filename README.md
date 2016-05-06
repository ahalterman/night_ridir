# night_ridir
Containerized tools for event data dictionary development

Docker
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

Example
-------

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
