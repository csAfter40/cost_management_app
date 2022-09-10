'''
This file reads data from rates.json and creates Rate objects.
'''
import json
from main.models import Currency, Rate

with open('rates.json', 'r') as f:
    data = json.load(f)

rates = data['rates']

currencies = Currency.objects.all()
for currency in currencies:
    rate = Rate(currency=currency, rate=rates[currency.code])
    rate.save()