from __future__ import division
from django import forms
from math import *
from decimal import Decimal


safe_list = ['math','acos', 'asin', 'atan', 'atan2', 'ceil', 'cos', 'cosh',
        'de grees', 'e', 'exp', 'fabs', 'floor', 'fmod', 'frexp', 'hypot',
        'ldexp', 'log', 'log10', 'modf', 'pi', 'pow', 'radians', 'sin', 'sinh',
        'sqrt', 'tan', 'tanh'] 

safe_dict = dict([ (k, locals().get(k, None)) for k in safe_list ]) 
safe_dict['abs'] = abs 

class MathDecimalField(forms.DecimalField):
    "DecimalField which allows math expressions"

    def clean(self, value):
        try:
            return Decimal(str(round(eval(value, {"__builtins__":None}, safe_dict), 2)))
        except:
            raise forms.ValidationError("Enter a valid number or math expression")