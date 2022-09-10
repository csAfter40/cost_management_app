'''
This file fetches rates from API, updates rates.json and Rate objects.
'''
import json
from main.models import Currency, Rate

import requests
from django.conf import settings

url = "https://api.apilayer.com/fixer/latest?base=USD"

payload = {}
headers= {
  "apikey": settings.CURRENCY_RATES_API_KEY
}

response = requests.request("GET", url, headers=headers, data = payload)

status_code = response.status_code
print(status_code)
result = response.text

if status_code == 200:
    with open('rates.json', 'w') as f:
        f.write(result)

    with open('rates.json', 'r') as f:
        data = json.load(f)

    rates = data['rates']

    objects = Rate.objects.all()
    for object in objects:
        object.rate = rates[object.currency.code]
        object.save()
else:
    print(f'Data fetching failed. Status code: {status_code}')