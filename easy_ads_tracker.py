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
import matplotlib.pyplot as plt
from datetime import *


SCOPES = ['https://www.googleapis.com/auth/sqlservice.admin']
SERVICE_ACCOUNT_FILE = '/content/creds.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

creds = None

creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

SAMPLE_SPREADSHEET_ID = '1lnw5LKsE8z7LqqzABfnE0xpHardHwP27016BPbKIegY'

service = build('sheets', 'v4', credentials=creds)

# Call the Sheets API
sheet1 = service.spreadsheets()


#___________________________________________________________________________________
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
my_string3="=GOOGLEFINANCE({},{},{},{})"
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
def clear_v(*args, range):
  request = sheet1.values().clear(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="ads!C1:H200").execute()
  

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

  #__GF_FUNCTION STANDS FOR 'GOOGLE FINANCE FUNCTION'____________________________________________________________
  GF_FUNCTION2=my_string2.format(ticker_final,'"price"')
  GF_FUNCTION1=my_string.format(ticker_final,'"price"',fecha_final)
  sheet.update_acell("C{}".format(next_row), GF_FUNCTION2)
  precio_actual=sheet.acell("C{}".format(next_row)).value
  sheet.update_acell("D1",GF_FUNCTION1)
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

def plot_performance(*args):
  ticker1=input("Ingrese Ticker: ")
  #__setting up the start and end date from a year ago till today.
  fecha_f=datetime.today().strftime('%Y/%m/%d')
  n_today = datetime.now() - timedelta(days=365)
  fecha_i=n_today.strftime("%Y/%m/%d")
  #______formating the strings to get the functions___
  ticker_f = t[:1]+ticker1+t[1:]
  fecha_i=t[:1]+fecha_i+t[1:]
  fecha_f=t[:1]+fecha_f+t[1:]
  GF_FUNCTION = my_string3.format(ticker_f.upper(),'"price"',fecha_i, fecha_f)
  gf_list=[[GF_FUNCTION]]
  #request to google sheet api________________________________
  request = sheet1.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                     range="hist!A1:B243", valueInputOption="USER_ENTERED",
                                     body={"values":gf_list}).execute()
                                     
  result = sheet1.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                            range="hist!A2:B243").execute()
  values = result.get('values', [])
  #_____ploting functions_________________________________
  col_names=['Date','Close']
  df4=pd.DataFrame(values, columns=col_names)
  df5=df4.head(240).set_index('Date')
  df6=df5['Close'].replace(',','.', regex=True).astype(float)
  df6.head(240).plot(x='Date',y='Close',color='Green',figsize=(20,10),title=ticker_f.upper())
  #I created all this dataframes from excel google sheet because for some reason the data wasn't considered as a numeric type.
rendimiento_compra()
watchlist()
plot_performance()
