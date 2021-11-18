import gspread
import pandas as pd
from pprint import pprint
from oauth2client.service_account import ServiceAccountCredentials
from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/sqlservice.admin']
SERVICE_ACCOUNT_FILE = 'creds.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

creds = None

creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)



SAMPLE_SPREADSHEET_ID = '1lnw5LKsE8z7LqqzABfnE0xpHardHwP27016BPbKIegY'

service = build('sheets', 'v4', credentials=creds)

# Call the Sheets API
sheet1 = service.spreadsheets()
result = sheet1.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                            range="ads!A1:D51").execute()
values = result.get('values', [])



scope = ["https://spreadsheets.google.com/feeds",
         'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file",
         "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("/content/creds.json", scope)
client = gspread.authorize(creds)

sheet=client.open("ads").sheet1

data=sheet.get_all_records()
df = pd.DataFrame(sheet.get_all_records())
#_______________________________________________________________________________

#These are strings to make the needed function in GoogleSheet. (It was the easiest way to me even if it's look complicated.)
my_string="=GOOGLEFINANCE({},{},{})"
my_string2="=GOOGLEFINANCE({},{})"
t='""'
#____________________________________________________________________

#These variables will be used later. (Historical price, Date, and a list to fill with both values.)
fecha_precio=0
fecha_compra=0
lista_historial=[]


#this function is for filling the next available rows automatically 
def next_available_row(sheet):
    str_list = list(filter(None, sheet.col_values(1)))
    return str(len(str_list)+1)

next_row = next_available_row(sheet)

next_available_row(sheet)


#___________________________________________________________________
#FUNCTION TO CLEAN VALUES OF GOOGLE SHEET AFTER REACHING CELL D50

def clear_v(*args):
  request = sheet1.values().clear(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="ads!C1:D50").execute()
#This is basically a function to make a watchlist of stocks(redundant I know)
#These tickers are for CEDEARS (ARGENTINIAN ADS)

def watchlist(*args):
  symbol_list=[]
  while True:
    symbol=input("Ingrese los tickers: ")
    if symbol=="salir":
      break 
    symbol_list.append(symbol.upper())
  for i in range(len(symbol_list)): 
    if symbol_list[i] in df.values:
      df2=df.loc[df['ticker'] == symbol_list[i]] #LOOPING THROUGH LIST TO PRINT THE REQUIRED SYMBOLS AND IT'S PRICES
      print(df2)
  val=sheet.acell("D51")
  if val.value=='FALSE':
    clear_v()  
  
  
def rendimiento_compra(): #function to watch your performance in the stocks. 
  global ticker
  ticker=input("Ingrese ticker en formato cedear (ejemplo 'BCBA:AAPL'): ")
  ticker_final=t[:1]+ticker+t[1:] #This is to make the ticker symbol being between Quotation marks
  fecha=input("Ingrese fecha de compra en formato AÑO/MES/DIA : ")
  fecha_final=t[:1]+fecha+t[1:]
  n=float(input("Ingrese la cantidad de acciones compradas: "))

  #___________________________________________________________________________________
  funcion2=my_string2.format(ticker_final,'"price"')
  funcion=my_string.format(ticker_final,'"price"',fecha_final)
  sheet.update_acell("C{}".format(next_row), funcion2)
  precio_actual=sheet.acell("C{}".format(next_row)).value
  sheet.update_acell("D1",funcion)
  #All of these formating functions above are to make the Spreadsheet functions work.
  
  #Accesing to the values.
  fecha_compra=sheet.acell('D2').value
  lista_historial.append(fecha_compra)
  fecha_precio=sheet.acell('E2').value
  lista_historial.append(fecha_precio)
  lista_historial.append(ticker)
  precio_actual2=precio_actual.strip("$")
  
  #Calculating the performances
  rendimiento=(float(precio_actual2)-float(fecha_precio))
  print("Su ganancia/pérdida es de: $", (float(rendimiento))*(n))
  print("porcentage de ganancia/pérdida es de", float(rendimiento*100)/float(fecha_precio), "%")

rendimiento_compra()
watchlist()
