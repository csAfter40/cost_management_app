'''
This file fetches currency rate data from API and writes on rates.json.
'''
import requests
from django.conf import settings

url = "https://api.apilayer.com/fixer/latest?base=USD"

payload = {}
headers= {
  "apikey": settings.CURRENCY_RATES_API_KEY
}

response = requests.request("GET", url, headers=headers, data = payload)

status_code = response.status_code
result = response.text

with open('rates.json', 'w') as f:
    f.write(result)