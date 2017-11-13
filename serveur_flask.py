from json_responses import json_response, json_data, json_error
from flask import Flask, request
import json
import requests
import os


app = Flask(__name__)
app.debug = True

admin = os.environ.get("LOGINCOUCHDB")
pwd = os.environ.get("PWDCOUCHDB")


def countparty():
    # get number party
    r = requests.get("https://couchdb.mignolet.fr/partydb/_design/all_party/_view/all")
    numberParty = json.loads(r.content)
    print(numberParty)
    if not numberParty["rows"]:
        num = 1
    else:
        num = numberParty["rows"][0]["value"] + 1
    print(num)
    return num

def getliste(num):
    rObjet = requests.get('https://couchdb.mignolet.fr/listesearchdb/liste'+str(num))
    print(rObjet.json())
    return rObjet.json()

@app.route('/')
def hello():
    return json_response('Hello World, from router api !')


@app.route('/initGame', methods=['GET'])
def initGame():
    num = countparty()
    jsonParty = '{"etat":"0"}'
    print(jsonParty)
    # write in couchdb news team
    r = requests.put("https://" + admin + ":" + pwd + "@couchdb.mignolet.fr/partydb/party" + str(num) + "", data=jsonParty)
    print(r.json())
    return json_response('start game')


#id inscription beacon
@app.route('/beaconInscript', methods=['GET'])
def beaconInscript():
    print("beaconInscript")
    r = requests.get('https://couchdb.mignolet.fr/beacondb/_design/type/_view/join?reduce=false')
    data = json.loads(r.content)
    print(data["rows"][0]["value"])
    dataValue = data["rows"][0]["value"]
    return json_response(dataValue,r.status_code)

#inscription team
@app.route('/inscript', methods=['POST'])
def inscript():
    print("inscription team")
    id = request.get_json(force=True)
    print(id)
    jsonData = id["id"]
    print("device_id: "+jsonData)
    #get number team
    teamrequest = requests.get("https://couchdb.mignolet.fr/teamdb/_design/_all_team/_view/num")
    print(teamrequest.json())

    #json parse
    numTeam = json.loads(teamrequest.content)
    if not numTeam["rows"]:
        num = 1
    else:
        num = numTeam["rows"][0]["value"] + 1
    print("News team: "+ str(num))

    jsonTeam = '{"name": "team'+str(num)+'" ,"idDevice":"'+jsonData+'"}'
    print(jsonTeam)

    #write in couchdb news team
    r = requests.put("https://"+admin+":"+pwd+"@couchdb.mignolet.fr/teamdb/team"+str(num)+"", data=jsonTeam)
    print(r.json())

    #creation de l'instance for team

    return json_response("", r.status_code)



#id beacon send picture
@app.route('/beaconSendPicture', methods=['GET'])
def beaconSendPicture():
    print("beaconInscript")
    r = requests.get('https://couchdb.mignolet.fr/beacondb/_design/type/_view/depot?reduce=false')
    data = json.loads(r.content)
    print(data["rows"][0]["value"])
    dataValue = data["rows"][0]["value"]
    return json_response(dataValue, r.status_code)




#liste objet search
@app.route('/liste' , methods=['GET'])
def newsListe():

    print("Liste objet")

    # get nomber liste search
    numberListe = requests.get("https://couchdb.mignolet.fr/listesearchdb/_design/_all/_view/all")
    print(numberListe.json())
    # json parse
    numL = json.loads(numberListe.content)
    print("number list:"+ str(numL["rows"]))
    if not numL["rows"]:
        num = 1
    else:
        num = numL["rows"][0]["value"]

    #get number party
    numberParty = countparty()-1
    numberListe = requests.get("https://couchdb.mignolet.fr/partydb/party"+str(numberParty)+"")
    etat = json.loads(numberListe.content)

    print("etat: "+str(etat["etat"]))
    #check creation news liste or get liste existing
    if etat["etat"] == "0":
        rObjet = requests.get('https://couchdb.mignolet.fr/objetdb/_design/_all_dbs/_view/random')
        print(rObjet.json())

        #new json data liste objet
        dataObjet = json.loads(rObjet.content)
        objetListe = dataObjet["rows"]

        jsonListe = '{"liste": '+str(json.dumps(objetListe))+'}'
        print("liste: "+str(jsonListe))

        #send news liste in liste search in couchbd
        listeOb = requests.put("https://" + admin + ":" + pwd + "@couchdb.mignolet.fr/listesearchdb/liste"+str(num+1)+"",data=jsonListe)
        print("retour send couchdb: "+str(listeOb.json()))

        #update etat du jeu
        jsonLL = '{"_id":"'+etat["_id"]+'","_rev":"'+etat["_rev"]+'","etat":"1"}'
        t = requests.put("https://couchdb.mignolet.fr/partydb/party"+str(numberParty)+"",data=jsonLL)
        print(t.json())
        jsonretour = getliste(num+1)
    else:
        jsonretour = getliste(num)
    return json_response(jsonretour)



#link instance for team
@app.route('/linkInstance')
def linkInstance():
    return 'Hello World!'

#redirecte instance for team
@app.route('/redirecte')
def redirecte():
    return 'redirecte'



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

