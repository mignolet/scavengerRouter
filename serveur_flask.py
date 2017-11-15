from json_responses import json_response, json_data, json_error
from flask import Flask, request
import json
import requests
import os, urlparse
import paho.mqtt.client as mqtt
from time import sleep


app = Flask(__name__)
app.debug = True

admin = os.environ.get("LOGINCOUCHDB")
pwd = os.environ.get("PWDCOUCHDB")


def on_connect(client, userdata, flags, rc):
    print("rc: " + str(rc))

def on_message(client, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

def on_publish(client, obj, mid):
    print("mid: " + str(mid))

def on_log(client, obj, level, string):
    print(string)

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

    jsonTeam = '{"name": "team'+str(num)+'" ,"idDevice":"'+jsonData+'", "ipInstance" : "none"}'
    print(jsonTeam)

    #write in couchdb news team
    r = requests.put("https://"+admin+":"+pwd+"@couchdb.mignolet.fr/teamdb/"+str(jsonData), data=jsonTeam)
    print(r.json())

    #creation de l'instance for team
        #rancher webhook


    return json_response(r.json(), r.status_code)



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
@app.route('/linkInstance', methods=['POST'])
def linkInstance():
    ipInstance = request.get_json(force=True)
    print(ipInstance["ip"])
    teamNotIp = requests.get("https://couchdb.mignolet.fr/teamdb/_design/_all_not_ip/_view/team")
    print(teamNotIp.json())
    data = json.loads(teamNotIp.content)
    print(data["rows"][0]["value"])
    jsonDataTem = '{"name": "' + str(data["rows"][0]["value"]["name"]) + '" ,"idDevice":"' + str(data["rows"][0]["value"]["idDevice"]) + '", "ipInstance" : "'+str(ipInstance["ip"])+'", "_rev":"'+str(data["rows"][0]["value"]["_rev"])+'"}'
    print(jsonDataTem)
    sendIp = requests.put("https://couchdb.mignolet.fr/teamdb/"+str(data["rows"][0]["value"]["_id"])+"",data=jsonDataTem)
    return json_response(sendIp.json())

#team inscript
@app.route('/team',methods=['POST'])
def team():
    jsonData = request.get_json(force=True)
    print(jsonData)
    data = requests.get("https://couchdb.mignolet.fr/teamdb/" + str(jsonData["id"]))
    print(data.json())
    return json_response(data.json(),data.status_code)


#redirecte instance for team
@app.route('/picture', methods=['POST'])
def picture():
    screenRasp("3")
    # get picture
    #imagefile = request.files['file']
    #print(imagefile)
    # get data json
    jsonData = request.get_json(force=True)
    print(jsonData)
    data = jsonData["longitude"]
    print(data)

    dataTeam = requests.get("https://couchdb.mignolet.fr/teamdb/"+str(jsonData["id_Equipe"]))
    Hote = json.loads(dataTeam.content)
    urlInstance = Hote["ipInstance"]+":5000"+ "/Classifier"
    print(urlInstance)

    try:
        reponseVisio = requests.put(urlInstance, data=jsonData)
        if reponseVisio:
            screenRasp("1")
        else:
            screenRasp("2")
        return reponseVisio
    except:
        screenRasp("2")
        return json_error("serveur en maintemance")

#get point equioe
@app.route('/teamPicture', methods=['POST'])
def teampicture():
    jsonData = request.get_json(force=True)
    dataTeam = requests.get("https://couchdb.mignolet.fr/teamdb/" + str(jsonData["id_Equipe"]))
    Hote = json.loads(dataTeam.content)
    urlInstance = Hote["ipInstance"] + ":5000" + "/getImage"
    jsonEquipe = '{"id_equipe":"'+jsonData["id_Equipe"]+'"}'
    imageEquipe = requests.put(urlInstance, data=jsonEquipe)
    return json_response(imageEquipe.json())

#get equipe game
@app.route('/equipeGame', methods=['GET'])
def allequipeGame():
    dataTeam = requests.get("https://couchdb.mignolet.fr/teamdb/_design/_all_team/_view/num?limit=20&reduce=false")
    print(dataTeam.json())
    return dataTeam.json()

#get imaga equipe
@app.route('/teamPoints', methods=['POST'])
def teampoints():
    jsonData = request.get_json(force=True)
    dataTeam = requests.get("https://couchdb.mignolet.fr/objetfinddb/_all_docs?key="+jsonData["id_Equipe"])
    return dataTeam.json()

#publish status Mqtt
def screenRasp(status):
    mqttc = connectMqtt()
    mqttc.publish("picture/test", status)
    print(status)

#connection mqtt
def connectMqtt():
    mqttc = mqtt.Client()
    # Uncomment to enable debug messages
    # mqttc.on_log = on_log

    # Parse CLOUDMQTT_URL (or fallback to localhost)
    url_str = os.environ.get('CLOUDMQTT_URL', "mqtt://hrrgcrqx:af3wqGskmMfY@m20.cloudmqtt.com:12771")
    url = urlparse.urlparse(url_str)

    # Connect
    mqttc.username_pw_set(url.username, url.password)
    mqttc.connect(url.hostname, url.port)
    print("mqttc connecte")
    return mqttc


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

