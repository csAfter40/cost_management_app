new Autocomplete('#autocomplete_expense', {
    search: input => {
        const url = `/autocomplete/expense_name?name=${input}`
        return new Promise(resolve => {
            fetch(url)
            .then(response => response.json())
            .then(data => {
                console.log(data)
                resolve(data.data)
            })
        })
    }
});

new Autocomplete('#autocomplete_income', {
    search: input => {
        const url = `/autocomplete/income_name?name=${input}`
        return new Promise(resolve => {
            fetch(url)
            .then(response => response.json())
            .then(data => {
                console.log(data)
                resolve(data.data)
            })
        })
    }
});

// datepickers for expense and income input forms
$( function() {
    $( "#expense-datepicker" ).datepicker();
  } );

$( function() {
    $( "#income-datepicker" ).datepicker();
  } );

$( function() {
    $( "#transfer-datepicker" ).datepicker();
  } );

// transfer form validation. from_account and to_account fields can't have the same value

const fromAccountField = document.querySelector('#from-account-field');
const toAccountField = document.querySelector('#to-account-field');

fromAccountField.addEventListener("change", function() {
    if (fromAccountField.value == toAccountField.value) {
        alert("'From account' and 'To account' can't have the same values.")
    }
});

toAccountField.addEventListener("change", function() {
    if (fromAccountField.value == toAccountField.value) {
        alert("'From account' and 'To account' can't have the same values.")
    }
});

function validateAccounts(e)
{
    // e.preventDefault();
    console.log('validation func called');
    if (fromAccountField.value == toAccountField.value) {
        alert("'From account' and 'To account' can't have the same values.");
        e.preventDefault();
        return false;
    }
    else {
        return true
    };
};

var transferForm = document.querySelector('#form-transfer');
transferForm.addEventListener('submit', validateAccounts, true)