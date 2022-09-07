import requests
import json
import os
import shelve
import sqlite3
import pickle
import random
from datetime import datetime, timedelta
from pathlib import Path
from os.path import join, dirname
from dotenv import load_dotenv
from apiclient.discovery import build


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
EMAIL = os.environ.get("EMAIL")
PASSWORD = os.environ.get("PASSWORD")
HOST = os.environ.get("HOST")
ENDPOINT = os.environ.get("ENDPOINT")
LOGIN = os.environ.get("LOGIN")
INVOICES = os.environ.get("INVOICES")
TMP_DB = os.environ.get("TMP_DB")
GOOGLE_CALENDAR_EMAIL = os.environ.get("GOOGLE_CALENDAR_EMAIL")
TIMEZONE = os.environ.get("TIMEZONE")


class IrenResponse():
  def __init__(self, code, description, status, response):
      self.code = code
      self.description = description
      self.status = status
      self.response = response

class IrenAuth():
  def __init__(self, id_token, username, is_locked):
      self.id_token     = id_token
      self.username     = username
      self.is_locked    = is_locked

class IrenContracts():
	def __init__(self, name, contract, expiry_date, issue_date, invoice_amount, amount_paid, residual_amount, state):
	  self.name     	        = name
	  self.contract     	    = contract
	  self.expiry_date        = expiry_date
	  self.issue_date         = issue_date
	  self.invoice_amount     = invoice_amount
	  self.amount_paid        = amount_paid
	  self.residual_amount    = residual_amount
	  self.state              = state

def check_temp_db_exists(): 
  fle = Path(TMP_DB)
  fle.touch(exist_ok=True)
  f = open(fle)
  f.close()

def create_empty_tables():
  check_temp_db_exists()
  try:
    sqliteConnection = sqlite3.connect(TMP_DB)
    cursor = sqliteConnection.cursor()

    sqlite_create_iren_auth = """ CREATE TABLE IF NOT EXISTS IrenAuth(
            id_token VARCHAR(255) NOT NULL,
            username VARCHAR(255) NOT NULL,
            is_locked INTEGER NOT NULL
        ); """

    cursor.execute(sqlite_create_iren_auth)

  except sqlite3.Error as error:
    print("Failed to create tables", error)
  finally:
    if sqliteConnection:
        sqliteConnection.close()

def save_login(iren_auth):
  try:
    sqliteConnection = sqlite3.connect(TMP_DB)


    cursor_delete = sqliteConnection.cursor()

    sqlite_delete_iren_auth_query = """DELETE FROM IrenAuth"""

    cursor_delete.execute(sqlite_delete_iren_auth_query)

    
    cursor = sqliteConnection.cursor()

    sqlite_insert_iren_auth_query = """INSERT INTO IrenAuth
                          (id_token, username, is_locked) 
                           VALUES 
                          (?, ?, ?)"""

    is_locked = 0
    if iren_auth.response.get('is_locked'):
        is_locked = 1

    data_iren_auth_tuple = (iren_auth.response.get('id_token'), 
                            iren_auth.response.get('username'),  
                            is_locked)

    cursor.execute(sqlite_insert_iren_auth_query, data_iren_auth_tuple)

    sqliteConnection.commit()
    cursor.close()
    cursor_delete.close()

  except sqlite3.Error as error:
    print("Failed to insert data into sqlite", error)
  finally:
    if sqliteConnection:
        sqliteConnection.close()

def get_auth_token():
  id_token = ''
  try:
    sqliteConnection = sqlite3.connect(TMP_DB)
    cursor = sqliteConnection.cursor()

    sqlite_select_query = """SELECT id_token from IrenAuth"""
    cursor.execute(sqlite_select_query)
    records = cursor.fetchall()

    for row in records:
      id_token = row[0]
      break

    cursor.close()
  except sqlite3.Error as error:
    print("Failed to read data from sqlite table", error)
  finally:
    if sqliteConnection:
      sqliteConnection.close()
  return id_token
  

def get_bollette():
    iren_response = IrenResponse(None, None, None, None)
    try:
        iren_token = get_auth_token()

        auth = 'Bearer ' + iren_token

        url = ENDPOINT+INVOICES

        r = requests.get(url,
            params={
                'flagHP': 'N',
            },
            headers={
                'Host': HOST,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'it-IT,it;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',                
                'Referer': ENDPOINT+'/spese',
                'Authorization': auth,
                'Connection': 'keep-alive',
                #'Cookie': '_gcl_au=1.1.1628190399.1662535402; _ga_6NHEWZX9FV=GS1.1.1662546681.3.1.1662546699.42.0.0; _ga=GA1.2.1834538257.1662535392; _gid=GA1.2.484135990.1662535395; G_ENABLED_IDPS=google; _hjSessionUser_1921754=eyJpZCI6IjBmNzEwMjU2LTgzNzQtNTc1Yi05ODBhLTY0ZWQwZTg0OWNiOCIsImNyZWF0ZWQiOjE2NjI1MzU0MTEzOTQsImV4aXN0aW5nIjp0cnVlfQ==; _hjIncludedInSessionSample=0; _iub_cs-43608930=%7B%22timestamp%22%3A%222022-09-07T07%3A23%3A30.972Z%22%2C%22version%22%3A%221.41.0%22%2C%22purposes%22%3A%7B%221%22%3Atrue%2C%222%22%3Atrue%2C%223%22%3Atrue%2C%224%22%3Atrue%2C%225%22%3Atrue%7D%2C%22id%22%3A%2243608930%22%2C%22cons%22%3A%7B%22rand%22%3A%22a9cdee%22%7D%7D; _gat_UA-101171608-6=1; _hjSession_1921754=eyJpZCI6IjZmMzlkYTk5LWExZjAtNGFlMy1iMDE2LWQzMzQwYjZhODc1ZiIsImNyZWF0ZWQiOjE2NjI1NDY2ODU2NTgsImluU2FtcGxlIjpmYWxzZX0=; _hjAbsoluteSessionInProgress=0',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'Pragma': 'no-cache',
                'Cache-Control': 'no-cache'
            }
        )
        iren_contracts = [IrenContracts(None, None, None, None, None, None, None, None).__dict__]
        if r.status_code != 200 or not r.content:
            iren_response = IrenResponse(str(r.status_code), "Iren API Error", "KO", iren_auth)
        else:
            code = r.json().get('status').get('codice')
            description = r.json().get('status').get('descrizione')
            status = r.json().get('status').get('esito')
            if(code == '000'):
                data = r.json().get('data')
                fatture = data.get('fatture')

                contracts_array = []

                for fattura in fatture:
                    state = 'unpaid'
                    if fattura.get('statoFatt') == 'pagata':
                        state = 'paid'
                    contracts_array.append(IrenContracts(fattura.get('nome'), fattura.get('numeroContratto'), fattura.get('scadenza'), fattura.get('dataEmissione'), fattura.get('importoFattura'), fattura.get('importoPagato'), fattura.get('importoResiduo'), state).__dict__)
                
            iren_response = IrenResponse(code, description, status, contracts_array)

    except Exception as e:
        iren_contracts = [IrenContracts(None, None, None, None, None, None, None, None).__dict__]
        iren_response = IrenResponse("401", str(e), "KO", iren_contracts)
    return iren_response.__dict__

def get_bollette_mock():
    iren_response = IrenResponse(None, None, None, None)
    code = "200"
    description = "OK"
    status = "OK"

    contracts_array = []

    for fattura in [0]:
      state = 'paid'
      #if random.randint(0, 1) == 0:
      #  state = 'unpaid'
      contracts_array.append(IrenContracts(str(fattura), str(fattura), '10.09.2022', '01.01.2021', '80', '80', '80', state).__dict__)
                
    iren_response = IrenResponse(code, description, status, contracts_array)

    return iren_response.__dict__


def login():
    iren_response = IrenResponse(None, None, None, None)
    try:
        if not EMAIL or not PASSWORD:
            iren_response = IrenResponse("KO","Please insert both email and password in .env file", None)
        else:
            url=ENDPOINT+LOGIN
            data={}
            data['email'] = EMAIL
            data['password'] = PASSWORD
            r = requests.post(url,
                data=json.dumps(data),
                headers={
                    'Host': HOST,
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0',
                    'Accept': 'application/json, text/plain, */*',
                    'Accept-Language': 'it-IT,it;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Referer': ENDPOINT,
                    'Content-Type': 'application/json',
                    'Content-Length': '64',
                    'Origin': ENDPOINT,
                    'Connection': 'keep-alive',
                    #'Cookie': '_gcl_au=1.1.1628190399.1662535402; _ga_6NHEWZX9FV=GS1.1.1662535402.1.1.1662535410.52.0.0; _ga=GA1.2.1834538257.1662535392; _gid=GA1.2.484135990.1662535395; G_ENABLED_IDPS=google; _hjSessionUser_1921754=eyJpZCI6IjBmNzEwMjU2LTgzNzQtNTc1Yi05ODBhLTY0ZWQwZTg0OWNiOCIsImNyZWF0ZWQiOjE2NjI1MzU0MTEzOTQsImV4aXN0aW5nIjpmYWxzZX0=; _hjFirstSeen=1; _hjIncludedInSessionSample=0; _hjSession_1921754=eyJpZCI6Ijk1MDQ4NTc5LWMwYjYtNDUzYS1hYjFlLWQ5YmVkYWVmN2YyOCIsImNyZWF0ZWQiOjE2NjI1MzU0MTE1OTksImluU2FtcGxlIjpmYWxzZX0=; _hjAbsoluteSessionInProgress=0; _iub_cs-43608930=%7B%22timestamp%22%3A%222022-09-07T07%3A23%3A30.972Z%22%2C%22version%22%3A%221.41.0%22%2C%22purposes%22%3A%7B%221%22%3Atrue%2C%222%22%3Atrue%2C%223%22%3Atrue%2C%224%22%3Atrue%2C%225%22%3Atrue%7D%2C%22id%22%3A%2243608930%22%2C%22cons%22%3A%7B%22rand%22%3A%22a9cdee%22%7D%7D',
                    'Sec-Fetch-Dest': 'empty',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'same-origin',
                    'Pragma': 'no-cache',
                    'Cache-Control': 'no-cache'
                    }
            )
            iren_auth = IrenAuth(None, None, None)
            if r.status_code != 200 or not r.content:
                iren_response = IrenResponse(str(r.status_code), "Iren API Error", "KO", iren_auth.__dict__)
            else:
                code = r.json().get('status').get('codice')
                description = r.json().get('status').get('descrizione')
                status = r.json().get('status').get('esito')
                if(code == '000'):
                    data = r.json().get('data')
                    id_token = data.get('id_token')
                    username = data.get('username')
                    is_locked = data.get('is_locked')
                    iren_auth = IrenAuth(id_token, username, is_locked)
                
                iren_response = IrenResponse(code, description, status, iren_auth.__dict__)
        
    except Exception as e:
        iren_auth = IrenAuth(None, None, None)
        iren_response = IrenResponse("401", str(e), "KO", iren_auth.__dict__)

    save_login(iren_response)

    return iren_response.__dict__ 

def fatture_to_calendar():
  credentials = pickle.load(open("config/token.pkl", "rb"))
  service = build("calendar", "v3", credentials=credentials)

  login()
  bollette_resp = get_bollette()
  #bollette_resp = get_bollette_mock()
  for fattura in bollette_resp.get('response'):
    data_fatt = fattura.get('expiry_date').split(".")
    start_time = datetime(int(data_fatt[2]), int(data_fatt[1]), int(data_fatt[0]), 9, 30, 0)
    end_time = start_time + timedelta(hours=12)
    summary = 'Pagare Bolletta Iren: ' + fattura.get('name')
    description = 'Contratto: ' + fattura.get('contract') + "\n"
    description = description + "Importo: " + fattura.get('invoice_amount') + "\n"
    description = description + "Pagato: " + fattura.get('amount_paid') + "\n"
    description = description + "Residuo: " + fattura.get('residual_amount')
    startTime = start_time.strftime("%Y-%m-%dT%H:%M:%S")
    endTime = end_time.strftime("%Y-%m-%dT%H:%M:%S")
    item_old = check_if_event_exists(summary, service)
    if item_old != None and fattura.get('state') == 'paid':
      service.events().delete(calendarId=GOOGLE_CALENDAR_EMAIL, eventId=item_old['id']).execute()
    elif fattura.get('state') == 'unpaid':
      event = {
        'summary': summary,
        'location': '',
        'description': description,
        'start': {
          'dateTime': startTime,
          'timeZone': TIMEZONE,
        },
        'end': {
          'dateTime': endTime,
          'timeZone': TIMEZONE,
        },
        'reminders': {
          'useDefault': False,
          'overrides': [
            {'method': 'email', 'minutes': 24 * 60},
            {'method': 'popup', 'minutes': 10},
          ],
        },
      }
      service.events().insert(calendarId=GOOGLE_CALENDAR_EMAIL, body=event).execute()

def check_if_event_exists(summary: str, service):
  result = service.events().list(calendarId=GOOGLE_CALENDAR_EMAIL, timeZone=TIMEZONE).execute()
  for item in result['items']:
    if 'summary' in item and item['summary'] == summary:
      return item
  return None


