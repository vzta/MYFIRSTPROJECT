import gspread
import streamlit as st
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from google.oauth2 import service_account
import yfinance as yf
import plotly.graph_objs as go

credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
    ],
)


SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

creds = None

creds = service_account.Credentials.from_service_account_file(
    st.secrets["gcp_service_account"], scopes=SCOPES)

SAMPLE_SPREADSHEET_ID = '1lnw5LKsE8z7LqqzABfnE0xpHardHwP27016BPbKIegY'

service = build('sheets', 'v4', credentials=creds, cache_discovery=False)

# Call the Sheets API
sheet1 = service.spreadsheets()

# ___________________________________________________________________________________
scope = ["https://spreadsheets.google.com/feeds",
         'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file",
         "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(st.secrets["gcp_service_account"], scope)
client = gspread.authorize(credentials)

sheet = client.open("ads").sheet1

data = sheet.get_all_records()

df = pd.DataFrame(sheet.get_all_records())

# _______________________________________________________________________________

# These are strings to make the needed function in GoogleSheet. (It was the easiest way to me even if it's look complicated.)
my_string = "=GOOGLEFINANCE({},{},{})"
my_string2 = "=GOOGLEFINANCE({},{})"
my_string3 = "=GOOGLEFINANCE({},{},{},{})"
t = '""'
st.title("Welcome to ADS EASY TRACKER!")


# ____________________________________________________________________

# These variables will be used later. (Historical price, Date, and a list to fill with both values.)
fecha_precio = 0
fecha_compra = 0
lista_historial = []


# this function is for filling the next available rows automatically
def next_available_row(sheet):
    str_list = list(filter(None, sheet.col_values(1)))
    return str(len(str_list) + 1)


next_row = next_available_row(sheet)

next_available_row(sheet)


# ___________________________________________________________________
# FUNCTION TO CLEAN VALUES OF GOOGLE SHEET AFTER REACHING CELL D50
def clear_v(*args, range):
    request = sheet1.values().clear(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="ads!C1:H200").execute()


# This is basically a function to make a watchlist of stocks(redundant I know)
# These tickers are for CEDEARS (ARGENTINIAN ADS)

import streamlit as st


def watchlist(*args):
    options = st.multiselect(
        'What stocks do you want to see?',
        ['NVDA', 'AAPL', 'TSLA', 'KO', 'X', 'GOOG', 'MSFT', 'MMM', 'BIDU', 'BABA', 'PEP', 'C', 'PBR', 'VALE', 'ERJ', 'JD', 'AMD', 'ETSY'
         , 'DOCU', 'SNAP', 'VZ', 'VIST', 'CSCO', 'INTC', 'FB', 'JNJ', 'PFE', 'MELI', 'AMZN', 'DIS', 'XOM', 'GOLD', 'HMY', 'AUY'],
    )
    button1=st.button("SEE RESULTS!")
    if button1:

        for i in range(len(options)):
            if options[i] in df.values:
                df2 = df.astype(str)
                df2 = df.loc[df['ticker'] == options[i]]  # LOOPING THROUGH LIST TO PRINT THE REQUIRED SYMBOLS AND IT'S PRICES

                st.dataframe(df2)
    val = sheet.acell("D51")
    if val.value == 'FALSE':
        clear_v()


def rendimiento_compra():  # function to watch your performance in the stocks.
    global ticker
    ticker = st.text_input("Enter the ticker symbol  you want (example: 'BCBA:AAPL'): ")
    ticker_final = t[:1] + ticker + t[1:]  # This is to make the ticker symbol being between Quotation marks
    fecha = st.text_input("Enter the Date of the purchase in the format 'YYYY/MM/DD' : ")
    fecha_final = t[:1] + fecha + t[1:]
    n = float(st.number_input("Enter how many shares do you bought ", step=1))


    try:  #I did this because until you fill all the values in the streamlit boxes it prints a error message

        # __GF_FUNCTION STANDS FOR 'GOOGLE FINANCE FUNCTION'____________________________________________________________
        GF_FUNCTION2 = my_string2.format(ticker_final, '"price"')
        GF_FUNCTION1 = my_string.format(ticker_final, '"price"', fecha_final)
        gf_list2 = [[GF_FUNCTION1]]
        gf_list3 = [[GF_FUNCTION2]]

        #request to google sheet api

        request = sheet1.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                         range="ren!A1:B243", valueInputOption="USER_ENTERED",
                                         body={"values": gf_list2}).execute()
        request = sheet1.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                         range="ren!C2", valueInputOption="USER_ENTERED",
                                         body={"values": gf_list3}).execute()
        result = sheet1.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                     range="ren!B2:C2").execute()
        values = result.get('values', [])
        columnas = ['Fecha1', 'Fecha2']
        dfp = pd.DataFrame(values, columns=columnas, index=None)

        data = dfp['Fecha2'].astype(float).subtract(dfp['Fecha1'].astype(float))
        performance = data.loc[0] * n
        porcentage = ((float(data * 100)) / float(dfp['Fecha1'].values))
        st.write("Your loss / profit is: \n$", round(performance), "<->", round(porcentage), "%")
    except BaseException:
        pass


def plot_performance(*args):
    try: #Same thing mentioned before!

        ticker1 = st.text_input("Enter the ticker symbol: ")
        data = yf.download(tickers=f"{ticker1}", period='1y', interval='1d', index_col="Adj Close", parse_dates=True)
        data.to_csv("CACA")
        df = pd.read_csv("CACA")
        fig = go.Figure([go.Scatter(x=df['Date'], y=df['Adj Close'])])
        st.plotly_chart(fig, use_container_width=True)

    except BaseException:
        pass


add_selectbox = st.sidebar.selectbox(
    "What do you want to do?",
    ("","Create a Watchlist", "Plot stock performance", "Calculate your purchase performance")
)
def call_function(*args):
    if add_selectbox == 'Create a Watchlist':
        watchlist()
    if add_selectbox == 'Plot stock performance':
        plot_performance()
    if add_selectbox == 'Calculate your purchase performance':
        rendimiento_compra()

call_function()
