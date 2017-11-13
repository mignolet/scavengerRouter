from json_responses import json_response, json_data, json_error
from flask import Flask, request
import json
import requests
import os

app = Flask(__name__)
app.debug = True

admin = os.environ.get("LOGINCOUCHDB")
pwd = os.environ.get("PWDCOUCHDB")


@app.route('/')
def hello():
    return json_response('Hello World, from router api !')

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
    r = requests.put("https://"+admin+":"+pwd+"@couchdb.mignolet.fr/teamdb/'team"+str(num)+"'", data=jsonTeam)
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
@app.route('/newListe' , methods=['GET'])
def newsListe():
    print("newsListe")
    r = requests.get('https://couchdb.mignolet.fr/objetdb/_design/_all_dbs/_view/random?limit=10&reduce=false')
    return json_response(r.json(), r.status_code)

#liste objet search
@app.route('/listObjet' , methods=['GET'])
def ListObjet():
    print("item liste")
    r = requests.get('')
    return json_response(r.json(), r.status_code)

#inscrption instance scale
@app.route('/inscriptionInstance')
def inscrptionInsrance():
    return 'Hello World!'

#link instance for team
@app.route('/linkInstance')
def linkInstance():
    return 'Hello World!'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

