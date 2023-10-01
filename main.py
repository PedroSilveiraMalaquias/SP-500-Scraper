import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt

url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

response = requests.get(url, headers=headers)

soup = BeautifulSoup(response.text, 'html.parser')

table = soup.find('table', {'class': 'wikitable sortable'})

columns = []
for th in table.find('tr').find_all('th'):
    columns.append(th.get_text(strip=True))

data = []
for row in table.find_all('tr')[1:]:
    rowData = []
    for td in row.find_all('td'):
        rowData.append(td.get_text(strip=True))
    data.append(rowData)

SP_data = pd.DataFrame(data, columns=columns)

tickers = SP_data['Symbol'].to_list()[:50]

df = pd.DataFrame(columns=['Ticker', 'Previous Close', '200-Day Moving Average', 'is_cheap'])
print(tickers)
#df.to_csv('sp500_companies.csv', index=False)

for i,ticker in enumerate(tickers):

    print(f'🔵 {i} of {len(tickers)} tickers processed - {100 * i/float(len(tickers))}%')
    # Get Previous Close value
    url = f"https://finance.yahoo.com/quote/{ticker}?p={ticker}tsrc=fin-srch"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    try:
        prev_close_element = soup.find('fin-streamer', {'data-test': 'qsp-price'})
        prev_close = float(prev_close_element['value'])
    except (AttributeError, TypeError):
        prev_close = None
    
    
    # Get 200-Day Moving Average value
    url = f"https://finance.yahoo.com/quote/{ticker}/key-statistics?p={ticker}"
    
    response = requests.get(url, headers = headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    try:
        moving_avg_element = soup.find('span', string = '200-Day Moving Average').find_parent().find_next_sibling('td')
        moving_avg = float(moving_avg_element.get_text(strip=True))
    except AttributeError:
        moving_avg = None
    

    # Compute is_cheap
    is_cheap = prev_close < moving_avg if prev_close is not None and moving_avg is not None else None
    
    df.loc[len(df)] = [ticker, prev_close, moving_avg, is_cheap];


df = df[df['is_cheap'] == True]


# Plotting
plt.figure(figsize=(10,6))
plt.bar(df['Ticker'], df['Previous Close'], color='blue')
plt.xlabel('ticker')
plt.ylabel('Value')
plt.title('Previous Close Values')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('plot.png')

