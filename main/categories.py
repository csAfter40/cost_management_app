expense_categories = {
    'Automobile': {
        'slug': 'automobile',
        'children': {
            'Insurance': {
                'slug': 'insurance',
                'children': None
            },
            'Maintenance': {
                'slug': 'maintenance',
                'children': None
            },
            'Gas': {
                'slug': 'gas',
                'children': None
            },
        }
    },
    'Food': {
        'slug': 'food',
        'children': {
            'Groceries': {
                'slug': 'groceries',
                'children': None
            },
            'Restaurant': {
                'slug': 'restaurant',
                'children': None
            },
        }
    },
    'Uncategorized': {
        'slug': 'uncategorized-expense',
        'children': None
    },
}

income_categories = {
    'Salary': {
        'slug': 'salary',
        'children': None
    },
    'Rents': {
        'slug': 'rents',
        'children': None
    },
    'Bank': {
        'slug': 'bank',
        'children': None
    },
    'Uncategorized': {
        'slug': 'uncategorized-income',
        'children': None
    },
}

categories = {
    # Expense Categories
    'Automobile': {
        'type': 'E',
        'children': {
            'Insurance': {
                'type': 'E',
                'children': None
            },
            'Maintenance': {
                'type': 'E',
                'children': None
            },
            'Gas': {
                'type': 'E',
                'children': None
            },
        }
    },
    'Food': {
        'type': 'E',
        'children': {
            'Groceries': {
                'type': 'E',
                'children': None
            },
            'Restaurant': {
                'type': 'E',
                'children': None
            },
        }
    },
    'Uncategorized': {
        'type': 'E',
        'children': None
    },
    'Transfer Out': {
        'type': 'E',
        'children': None,
        'is_transfer': True
    },
    # Income Categories
    'Salary': {
        'type': 'I',
        'children': None
    },
    'Rents': {
        'type': 'I',
        'children': None
    },
    'Bank': {
        'type': 'I',
        'children': None
    },
    'Uncategorized': {
        'type': 'I',
        'children': None
    },
    'Transfer In': {
        'type': 'I',
        'children': None,
        'is_transfer': True
    },
}