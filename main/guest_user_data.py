bank_account = {"name": 'My Bank Account', 'initial': 10000}
wallet = {"name": 'My Wallet', 'initial': 200}
credit_card = {'name': 'My Credit Card', 'payment_day': 15}

# loans = [
#     {'name': 'name', 'initial': 'initial'}
# ]


# transfers = [
#     {
#         'from_account': 'from_account',
#         'to_account': 'to_account',
#         'amount': 'amount',
#         'date': 'date'
#     },
# ]

# chatGPT prompt to generate monthly expences:
"""
    Consider an average American family's monthly expenses. Using the expense 
    categories above, generate 20 lines fake expense data for 1 month of period. 
    Total monthly expense should be between 6400usd and 7600usd.

    We have 3 accounts to pay from: 1. "bank_account", 2. "wallet", 3."credit_card". 
    
    Data should have the following keys: name, amount, category, date(day of the month), account. 
    Format must be a python list of dictionaries. 
    Example expense: {"name": fruits, "amount": 12.99, "category": "Groceries", "date": 23, "account": "wallet"}
     

    Results should represent expected expenses of an average American family.
"""

expenses = [
    #month #1    
    {"name": "Electricity Bill", "amount": 150.25, "category": "Utilities", "date": 5, "account": "bank_account"},    
    {"name": "Income Tax", "amount": 750.25, "category": "Other Taxes", "date": 4, "account": "bank_account"},    
    {"name": "Internet Bill", "amount": 70.00, "category": "Utilities", "date": 10, "account": "bank_account"},    
    {"name": "Water Bill", "amount": 45.50, "category": "Utilities", "date": 15, "account": "credit_card"},    
    {"name": "Groceries", "amount": 235.60, "category": "Groceries", "date": 8, "account": "wallet"},    
    {"name": "Groceries", "amount": 135.60, "category": "Groceries", "date": 18, "account": "wallet"},    
    {"name": "Groceries", "amount": 215.60, "category": "Groceries", "date": 28, "account": "wallet"},    
    {"name": "Gasoline", "amount": 182.90, "category": "Gas/Fuel", "date": 10, "account": "bank_account"},    
    {"name": "Gasoline", "amount": 149.90, "category": "Gas/Fuel", "date": 20, "account": "bank_account"},    
    {"name": "Gasoline", "amount": 152.90, "category": "Gas/Fuel", "date": 30, "account": "bank_account"},    
    {"name": "Car Payment", "amount": 320.00, "category": "Car Payments", "date": 25, "account": "credit_card"},    
    {"name": "Rent", "amount": 1200.00, "category": "Mortgage/Rent", "date": 1, "account": "bank_account"},    
    {"name": "Auto Insurance", "amount": 85.00, "category": "Car Insurance", "date": 7, "account": "wallet"},    
    {"name": "Health Insurance", "amount": 345.00, "category": "Health Insurance", "date": 13, "account": "bank_account"},    
    {"name": "Fast Food", "amount": 28.50, "category": "Dining Out", "date": 8, "account": "credit_card"},    
    {"name": "Movie Theater", "amount": 32.00, "category": "Movies", "date": 16, "account": "wallet"},    
    {"name": "Gym Membership", "amount": 75.00, "category": "Gym Memberships", "date": 22, "account": "bank_account"},    
    {"name": "Toiletries", "amount": 27.00, "category": "Toiletries", "date": 2, "account": "credit_card"},    
    {"name": "Haircut", "amount": 40.00, "category": "Haircuts", "date": 9, "account": "wallet"},    
    {"name": "Medicine", "amount": 75.50, "category": "Medicine", "date": 12, "account": "bank_account"},    
    {"name": "Books", "amount": 52.30, "category": "Books", "date": 19, "account": "wallet"},    
    {"name": "Donation", "amount": 100.00, "category": "Donations", "date": 26, "account": "credit_card"},    
    {"name": "Legal Fees", "amount": 400.00, "category": "Legal Fees", "date": 3, "account": "bank_account"},    
    {"name": "Clothing", "amount": 92.45, "category": "Clothing", "date": 11, "account": "wallet"},    
    {"name": "Streaming Services", "amount": 18.99, "category": "Streaming Services", "date": 28, "account": "credit_card"},
    #month #2    
    {"name": "Internet", "amount": 50.00, "category": "Utilities", "date": 36, "account": "bank_account"},
    {"name": "Income Tax", "amount": 750.25, "category": "Other Taxes", "date": 34, "account": "bank_account"},    
    {"name": "Gasoline", "amount": 160.00, "category": "Gas/Fuel", "date": 38, "account": "credit_card"},
    {"name": "Gasoline", "amount": 140.00, "category": "Gas/Fuel", "date": 48, "account": "credit_card"},
    {"name": "Gasoline", "amount": 150.00, "category": "Gas/Fuel", "date": 58, "account": "credit_card"},
    {"name": "Dental visit", "amount": 200.00, "category": "Medical Supplies", "date": 39, "account": "bank_account"},
    {"name": "Groceries", "amount": 150.00, "category": "Groceries", "date": 40, "account": "wallet"},
    {"name": "Groceries", "amount": 120.00, "category": "Groceries", "date": 50, "account": "wallet"},
    {"name": "Groceries", "amount": 110.00, "category": "Groceries", "date": 60, "account": "wallet"},
    {"name": "Health Insurance", "amount": 345.00, "category": "Health Insurance", "date": 43, "account": "bank_account"},    
    {"name": "Car insurance", "amount": 120.00, "category": "Car Insurance", "date": 42, "account": "credit_card"},
    {"name": "Phone bill", "amount": 80.00, "category": "Utilities", "date": 44, "account": "wallet"},
    {"name": "Movie tickets", "amount": 40.00, "category": "Movies", "date": 46, "account": "credit_card"},
    {"name": "Electricity bill", "amount": 90.00, "category": "Utilities", "date": 48, "account": "bank_account"},
    {"name": "Clothing", "amount": 70.00, "category": "Clothing", "date": 49, "account": "credit_card"},
    {"name": "Gift for friend's birthday", "amount": 30.00, "category": "Gifts", "date": 51, "account": "wallet"},
    {"name": "Hair salon", "amount": 60.00, "category": "Haircuts", "date": 52, "account": "credit_card"},
    {"name": "Rent", "amount": 1200.00, "category": "Mortgage/Rent", "date": 31, "account": "bank_account"},
    {"name": "Gym membership", "amount": 40.00, "category": "Gym Memberships", "date": 55, "account": "bank_account"},
    {"name": "Books", "amount": 60.00, "category": "Books", "date": 56, "account": "credit_card"},
    {"name": "Car payment", "amount": 375.00, "category": "Car Payments", "date": 52, "account": "credit_card"},
    {"name": "Toiletries", "amount": 25.00, "category": "Toiletries", "date": 58, "account": "wallet"},
    {"name": "Electric scooter rental", "amount": 15.00, "category": "Public Transit", "date": 59, "account": "credit_card"},
    {"name": "Pizza delivery", "amount": 30.00, "category": "Dining Out", "date": 60, "account": "bank_account"},
    {"name": "Clothing", "amount": 45.00, "category": "Clothing", "date": 61, "account": "wallet"},
    {"name": "Netflix subscription", "amount": 15.00, "category": "Streaming Services", "date": 32, "account": "credit_card"},
    {"name": "Donation to charity", "amount": 50.00, "category": "Donations", "date": 31, "account": "bank_account"},
    #month #3    
    {"name": "Electricity bill", "amount": 145.25, "category": "Utilities", "date": 64, "account": "bank_account"},
    {"name": "Income Tax", "amount": 750.25, "category": "Other Taxes", "date": 64, "account": "bank_account"},    
    {"name": "Car insurance", "amount": 210.00, "category": "Car Insurance", "date": 67, "account": "credit_card"},
    {"name": "Groceries", "amount": 348.75, "category": "Groceries", "date": 68, "account": "wallet"},
    {"name": "Groceries", "amount": 118.75, "category": "Groceries", "date": 88, "account": "wallet"},
    {"name": "Health Insurance", "amount": 345.00, "category": "Health Insurance", "date": 73, "account": "bank_account"},    
    {"name": "Gasoline", "amount": 150.00, "category": "Gas/Fuel", "date": 68, "account": "credit_card"},
    {"name": "Gasoline", "amount": 166.00, "category": "Gas/Fuel", "date": 78, "account": "credit_card"},
    {"name": "Gasoline", "amount": 140.00, "category": "Gas/Fuel", "date": 88, "account": "credit_card"},
    {"name": "Rent", "amount": 1200.00, "category": "Mortgage/Rent", "date": 61, "account": "bank_account"},
    {"name": "Internet bill", "amount": 85.99, "category": "Utilities", "date": 70, "account": "credit_card"},
    {"name": "Gym membership", "amount": 60.00, "category": "Gym Memberships", "date": 72, "account": "wallet"},
    {"name": "Home repairs", "amount": 285.00, "category": "House Repairs", "date": 74, "account": "bank_account"},
    {"name": "Eating out", "amount": 92.45, "category": "Dining Out", "date": 76, "account": "credit_card"},
    {"name": "Netflix subscription", "amount": 18.99, "category": "Streaming Services", "date": 78, "account": "wallet"},
    {"name": "Hair coloring", "amount": 95.00, "category": "Haircuts", "date": 80, "account": "bank_account"},
    {"name": "Car payment", "amount": 375.00, "category": "Car Payments", "date": 82, "account": "credit_card"},
    {"name": "Birthday gift", "amount": 50.00, "category": "Gifts", "date": 84, "account": "wallet"},
    {"name": "Clothes shopping", "amount": 220.50, "category": "Clothing", "date": 86, "account": "bank_account"},
    {"name": "Movie tickets", "amount": 32.00, "category": "Movies", "date": 87, "account": "credit_card"},
    {"name": "Phone bill", "amount": 75.00, "category": "Utilities", "date": 88, "account": "wallet"},
    {"name": "Tennis lessons", "amount": 140.00, "category": "Activities", "date": 62, "account": "bank_account"},
    {"name": "Groceries", "amount": 245.80, "category": "Groceries", "date": 65, "account": "credit_card"},
    {"name": "Donation to charity", "amount": 50.00, "category": "Donations", "date": 69, "account": "wallet"},
    {"name": "New tires", "amount": 600.00, "category": "Car Repairs", "date": 73, "account": "bank_account"},
    {"name": "Haircut", "amount": 50.00, "category": "Haircuts", "date": 77, "account": "credit_card"},
]


# chatGPT prompt to generate monthly incomes:
"""
Now lets create some incomes for an american family. Total monthly income must be 
between 7500 and 8500 USD. Using the income categories above, create a list of 
incomes for an average american family. each income must be a dictionary and has 
keys of "name", "amount", "date"(day of the month) and "category".
"""

incomes = [    
    # month #1
    {"name": "Salary", "amount": 4000, "date": 1, "category": "Salary", "account": "bank_account"},    
    {"name": "Bonus", "amount": 1000, "date": 15, "category": "Other Income", "account": "bank_account"},    
    {"name": "Investment Income", "amount": 300, "date": 10, "category": "Investments", "account": "bank_account"},    
    {"name": "Freelance Work", "amount": 500, "date": 20, "category": "Self-Employment", "account": "bank_account"},    
    {"name": "Child Support", "amount": 500, "date": 15, "category": "Child Support", "account": "bank_account"},   
    # month #2
    {"name": "Salary", "amount": 4000, "date": 31, "category": "Salary", "account": "bank_account"},
    {"name": "Freelance Work", "amount": 700, "date": 35, "category": "Self-Employment", "account": "bank_account"},
    {"name": "Investment Income", "amount": 600, "date": 40, "category": "Investments", "account": "bank_account"},
    {"name": "Lottery Winnings", "amount": 500, "date": 58, "category": "Other Income", "account": "bank_account"},
    {"name": "Bonus", "amount": 700, "date": 31, "category": "Salary", "account": "bank_account"},
    # month #3
    {"name": "Salary", "amount": 4000, "category": "Salary", "date": 61, "account": "bank_account"},
    {"name": "Investment Income", "amount": 700, "category": "Investments", "date": 68, "account": "bank_account"},
    {"name": "Freelance Project", "amount": 600, "category": "Self-Employment", "date": 72, "account": "bank_account"},
    {"name": "2nd Hand Sales", "amount": 250, "category": "Other Income", "date": 78, "account": "bank_account"},
    {"name": "Gift", "amount": 150, "category": "Other Income", "date": 81, "account": "bank_account"},
]