import requests
import csv
import pandas as pd
import datetime
from datetime import date
import sys


period = "DAY" # Day or Week

# Obtain today's date for calculating start and end dates
today = datetime.date.today()
ws = (today - datetime.timedelta(days=today.weekday(), weeks=2)).strftime('%Y-%m-%d') # Monday of previous week
we = (today - datetime.timedelta(days=(today.weekday() - 4), weeks=1)).strftime('%Y-%m-%d') # Friday of last week
de = (today - datetime.timedelta(1)).strftime('%Y-%m-%d') # Yesterday
ds = (today - datetime.timedelta(2)).strftime('%Y-%m-%d') # Day before yesterday

dst, dnd, start, end = "", "", "", ""

# If today is Monday then start day is Thurday and end day is Friday
if date.today().weekday() == 0:
    dst =  today - datetime.timedelta(days=(today.weekday() - 3), weeks=1).strftime('%Y-%m-%d') 
    dnd =  we
# If today is Tuesday then start day is Friday    
elif  date.today().weekday() == 1:
    dst = we
else:
    dst = ds
    dnd = de   

# Select whether to collect daily or weekly data
if period.casefold() == "day":
    start = dst
    end   = dnd
elif period.casefold() == "week":    
     start = ws
     end   = we
else:
    print("Enter day or week in 'period'")
    sys.exit() 
    
# The platform offers appx. 170 currencies and some currencies have missing 
# exchange rates. We filter and store only the symbols that have actual rates.

# Collect all symbols with exchange rates against USD (common currency)
url = 'https://api.exchangerate.host/fluctuation?start_date='+start+'&end_date='+end+'&base=USD'
res = requests.get(url)
data = res.json()
df = pd.json_normalize(data)
df.drop(df.iloc[:, 0:6], inplace = True, axis = 1)
res = df.transpose()
res = res.iloc[3:]
res = res.iloc[::4, :]
res = res.reset_index()
res.columns = ['curr', 'rates']
actual = list(res['curr'].str[6:9]) # Store symbols in list

# Collect all listed symbols
symbols = 'https://api.exchangerate.host/symbols'
response = requests.get(symbols)
symb_data = response.json()
symb = pd.DataFrame.from_dict(symb_data)
symb = symb.iloc[2:]
symb = symb.reset_index()
symb = symb.rename(columns={'index': 'symb'})
listed = list(symb['symb']) # Store symbols in list

# Declare list to store symbols
curr = []

# Compare actual and listed symbols and only store listed symbols with
# actual rates
for symbol in listed:
    if symbol in actual:
      curr.append(symbol)

# Declare list to store rates
rates = [] 

# Iterate through all symbols and store their corresponding rates relative 
# to all other currencies
for x in curr:
  url = 'https://api.exchangerate.host/fluctuation?start_date='+start+'&end_date='+end+'&base='+x
  req = requests.get(url)
  data = req.json()
  df = pd.json_normalize(data)
  df.drop(df.iloc[:, 0:6], inplace = True, axis = 1)
  res = df.transpose()
  res = res.iloc[3:]
  res = res.iloc[::4, :]
  res = res.reset_index()
  res.columns = ['curr', 'rates']
  rates.append(res['rates'])

# Export the rates to a csv file
filename = "rates.csv"
with open(filename, 'w') as csvfile: 
    csvwriter = csv.writer(csvfile) 
    csvwriter.writerow(curr) 
    csvwriter.writerows(rates)

print("Done for the "+period+"!")
