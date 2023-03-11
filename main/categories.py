categories = {
    # Expense categories
    "Housing": {
        "type": "E",
        "children": {
            "Mortgage/Rent": {"type": "E", "children": None},
            "Taxes": {"type": "E", "children": None},
            "Insurance": {"type": "E", "children": None},
            "Repairs": {"type": "E", "children": None},
            "Utilities": {"type": "E", "children": None}
        }
    },
    "Transportation": {
        "type": "E",
        "children": {
            "Car Payments": {"type": "E", "children": None},
            "Gas/Fuel": {"type": "E", "children": None},
            "Insurance": {"type": "E", "children": None},
            "Repairs": {"type": "E", "children": None},
            "Public Transit": {"type": "E", "children": None}
        }
    },
    "Food": {
        "type": "E",
        "children": {
            "Groceries": {"type": "E", "children": None},
            "Dining Out": {"type": "E", "children": None},
            "Alcohol": {"type": "E", "children": None},
            "Snacks": {"type": "E", "children": None}
        }
    },
    "Personal Care": {
        "type": "E",
        "children": {
            "Haircuts": {"type": "E", "children": None},
            "Toiletries": {"type": "E", "children": None},
            "Clothing": {"type": "E", "children": None},
            "Gym Memberships": {"type": "E", "children": None}
        }
    },
    "Health": {
        "type": "E",
        "children": {
            "Insurance": {"type": "E", "children": None},
            "Medicine": {"type": "E", "children": None},
            "Medical Supplies": {"type": "E", "children": None}
        }
    },
    "Education": {
        "type": "E",
        "children": {
            "Tuition": {"type": "E", "children": None},
            "Books": {"type": "E", "children": None},
            "Activities": {"type": "E", "children": None},
        }
    },
    "Entertainment": {
        "type": "E",
        "children": {
            "Movies": {"type": "E", "children": None},
            "TV": {"type": "E", "children": None},
            "Streaming Services": {"type": "E", "children": None},
            "Hobbies": {"type": "E", "children": None}
        }
    },
    "Gifts/Donations": {
        "type": "E",
        "children": {
            "Gifts": {"type": "E", "children": None},
            "Donations": {"type": "E", "children": None},
            "Celebrations": {"type": "E", "children": None}
        }
    },
    "Miscellaneous": {
        "type": "E",
        "children": {
            "Bank Fees": {"type": "E", "children": None},
            "Taxes": {"type": "E", "children": None},
            "Legal Fees": {"type": "E", "children": None}
        }
    },
    # Income categories
    "Salary": {"type": "I", "children": None},
    "Investments": {"type": "I", "children": None},
    "Rental Income": {"type": "I", "children": None},
    "Child Support": {"type": "I", "children": None},
    "Other Income": {"type": "I", "children": None},
    "Bank Interests": {"type": "I", "children": None},
    "Scholarship": {"type": "I", "children": None},
    "Gifts": {"type": "I", "children": None},
    # Protected categories
    "Transfer Out": {"type": "E", "children": None, "is_transfer": True, 'is_protected': True},
    "Pay Loan": {"type": "E", 'children': None, 'is_protected': True},
    "Pay Card": {"type": "E", 'children': None, 'is_protected': True},
    "Asset Delete": {"type": "E", "children":None, "is_protected": True},
    "Transfer In": {"type": "I", "children": None, "is_transfer": True, 'is_protected': True},
    "Loan In": {"type": 'I', 'children': None, 'is_protected': True},
    "Pay Loan": {"type": "I", 'children': None, 'is_protected': True},
    "Pay Card": {"type": "I", 'children': None, 'is_protected': True},
    "Asset Delete": {"type": "I", "children":None, "is_protected": True},
}