#!/usr/local/bin/python3

import time
import requests as req
import json
import telegram
from datetime import datetime

# No warning
req.packages.urllib3.disable_warnings()

before_date = 20210701
after_date = 20210616
wait_seconds = 20
null = None

email = 'your-email'
mobile = 'your-mobile'
codice_fiscale = 'NNNN'
tessera_sanitaria = '8038000'+'0000000000000'

user_agent = 'peek-a-user-agent'
host = 'www.sanita.puglia.it'
today = datetime.today().strftime('%Y-%m-%d')
cupDate = today[0:8] + str(int(today[8:])+1)

proto = 'https://'
get_base_url =  proto + host + '/sanita-api/covid19/appointments/patient/'
get_url = get_base_url + codice_fiscale
post_url = proto + host + '/sanita-api/covid19/reservation/register'

post_url_params = {
    'platform': 'WEB',
    'accessMode': 'ANONIMO',
    'functionality': 'PRENOTAZIONE_VACCINO'
}
get_url_params = {
    'healthServicesRegCodes': '994A', 
    'deliveryType': 'SSN',
    'companyCodes': 'C160116',
    'facilityCode': '400200',
    'cupDate': cupDate,
    'isFragile': 'false',
    'healthInsuranceCard': tessera_sanitaria,
    'platform': 'WEB',
    'accessMode': 'ANONIMO',
    'functionality': 'PRENOTAZIONE_VACCINO'
}

get_headers = {
    'Host': host,
    'User-Agent': user_agent,
    'Accept': 'application/json',
    'Accept-Language': 'en,it-IT;q=0.8,it;q=0.5,en-US;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://www.sanita.puglia.it/prenotazione-vaccino-covid19/',
    'Content-Type': 'application/json; charset=utf-8',
    'Connection': 'keep-alive'
}

# From https://medium.com/@mycodingblog/get-telegram-notification-when-python-script-finishes-running-a54f12822cdc

def notify_ending(message):
    token = 'token'
    chat_id = 'id'
    bot = telegram.Bot(token=token)
    bot.sendMessage(chat_id=chat_id, text=message)

def send_prenotazione(target):

    post_data = {
        "appointments":[
            target
        ],
        "demandingNumberE":null,
        "demandingNumberR":null,
        "demandingDate":null,
        "userInfo":{
            "email":email,
            "phone":mobile,
            "fiscalCode":codice_fiscale,
            "healthInsuranceCard":tessera_sanitaria
        }
    }

    post_headers = {
        'Host': host,
        'User-Agent': user_agent,
        'Accept': 'application/json',
        'Accept-Language': 'en,it-IT;q=0.8,it;q=0.5,en-US;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.sanita.puglia.it/prenotazione-vaccino-covid19/',
        'Content-Type': 'application/json; charset=utf-8',
        'Origin': 'https://www.sanita.puglia.it',
        'Connection': 'keep-alive'
    }

    r = req.post(post_url, headers=post_headers, params=post_url_params, verify=False, json=post_data) 

    if (r.status_code == 200):
        resp_json = r.json()
        outcome = resp_json['outcome']

        if (outcome['code'] == 'OK'):
            notify_ending('Numero prenotazione: ' + resp_json['number'])
            return True
        else :
            print('[-] Err: ' + outcome['descr'])
            return False

while True:
    r = req.get(get_url, headers=get_headers, params=get_url_params, verify=False)

    if (r.status_code == 200):
        resp_json = r.json()
        appointments = resp_json['appointmentsList']
        for a in appointments:
            date = a['date']
            if (int(date) <= before_date and int(date) >= after_date):
                # Found
                if (send_prenotazione(appointments[0])):
                    print('Vaccino il '+ date)
                    exit() 
                else:
                    break
            else:
                print('[i] Last date: ' + date)
                break
    
    time.sleep(wait_seconds)