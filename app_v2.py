from __future__ import print_function
#from future.standard_library import install_aliases
#install_aliases()
from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os

from flask import Flask
from flask import request
from flask import make_response

import yweather
from datetime import datetime, time

woeid = yweather.Client()
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    res = processRequest(req)
    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    if req.get("queryResult").get("action") != "MobiaasWeatherEngine":
        print ("Please check your action name in DialogFlow...")
        return {}
    woeid = makeYqlQuery(req)
    print("id",woeid)
    if woeid is None:
        return {
    "fulfillmentText": "Hello! We are working on the Weather data of your location. We will get back to you shortly. Thank You.",
     "source": "Yahoo Weather"
    }
    api_key = "QnV7pOhKXpuOQVJjus5Y9OcD0A2OQUu2"
    baseurl =f"http://dataservice.accuweather.com/forecasts/v1/daily/1day/{woeid}?apikey={api_key}&language=en-us&details=false&metric=false"
    #yql_url = baseurl + urlencode({'q': woeid}) + "&format=json"
    try:
        result = urlopen(baseurl).read()
        data = json.loads(result)
        filename = "random.json"
        with open(filename, 'w') as outfile:
            json.dump(data, outfile, sort_keys = True, indent = 4,ensure_ascii = False)
        #for some reason the line above gives an error and hence decoding to utf-8 might help
        #data = json.loads(result.decode('utf-8'))
        res = makeWebhookResult(data)
        return res
    except Exception as e:
        print(">>>>>>>>>>>>>>",e)
        return {
    "fulfillmentText": "Hello!  We will get back to you shortly. Thank You.",
     "source": "Yahoo Weather"
    }
def makeYqlQuery(req):
    result = req.get("queryResult")
    print("results------->\n",result.get("queryText"))

    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    location = parameters.get("towns")
    if len(city)>1:
        thewoeid = woeid.fetch_woeid(city)
        print("The Query city is: ",city,"with woeid as: ",thewoeid)
    elif len(location)>1:
        thewoeid = woeid.fetch_woeid(location)
        print("The Query location is: ",location,"with woeid as: ",thewoeid)
    else:
        thewoeid = None
    return thewoeid
def makeWebhookResult(data):
    DailyForecasts = data.get('DailyForecasts')
    if DailyForecasts is None:
        return {}
    listelement = DailyForecasts[0]
    now = datetime.now()   
    if now.hour >19 and now.hour < 6:
        Night = listelement.get("Night")
        if Night is None:
            return {}
        IconPhrase = Night.get("IconPhrase")
        if IconPhrase is None:
            return {}
        print("DailyForecasts",IconPhrase)
    else:
        Day = listelement.get("Day")
        if Day is None:
            return {}
        IconPhrase = Day.get("IconPhrase")
        if IconPhrase is None:
            return {}
        print("DailyForecasts",IconPhrase)

    return {
    "fulfillmentText": IconPhrase,
     "source": "Yahoo Weather"
    }

@app.route('/test', methods=['GET'])
def test():
    return  "Hello there my friend !!"

@app.route('/static_reply', methods=['POST'])
def static_reply():
    speech = "Hello there, this reply is from the webhook !! "
    string = "You are awesome !!"
    Message ="this is the message"

    my_result =  {
    "fulfillmentText": string,
     "source": string
    }

    res = json.dumps(my_result, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

if __name__ == '__main__':
    port = int(5000)
    app.run(debug=True, port=port, host='0.0.0.0')


