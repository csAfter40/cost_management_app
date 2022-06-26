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
// transfer form amount input manipulation. There will be single amount input if the currencies of accounts are same.

// get json file from script tag
var accountData = JSON.parse(document.querySelector('#account-data').textContent);
const toAmountField = document.querySelector('#div_id_to_amount');
const toAmountInput = document.querySelector('#id_to_amount');
const fromAmountInput = document.querySelector('#id_from_amount');
const fromAmountField = document.querySelector('#div_id_from_amount');
const fromAmountTitle = fromAmountField.querySelector('label');
const fromAmountPrepend = fromAmountField.querySelector('.input-group-text')
const toAmountPrepend = toAmountField.querySelector('.input-group-text')

const fromAccountField = document.querySelector('#from-account-field');
const toAccountField = document.querySelector('#to-account-field');

fromAccountField.addEventListener("change", function() {
    fromAmountPrepend.innerHTML = accountData[fromAccountField.value] || '-'
    if (fromAccountField.value == toAccountField.value && fromAccountField.value != '') {
        alert("'From account' and 'To account' can't have the same values.")
    } else if (accountData[fromAccountField.value] == accountData[toAccountField.value] && fromAccountField.value != '') {
        toAmountField.style.display = 'none';
        fromAmountTitle.innerHTML = 'Amount<span class="asteriskField">*</span>'
    } else {
        toAmountField.style.display = 'block';
        fromAmountTitle.innerHTML = 'From amount<span class="asteriskField">*</span>'
    };
});

toAccountField.addEventListener("change", function() {
    toAmountPrepend.innerHTML = accountData[toAccountField.value] || '-'
    if (fromAccountField.value == toAccountField.value && toAccountField.value != '') {
        alert("'From account' and 'To account' can't have the same values.")
    } else if (accountData[fromAccountField.value] == accountData[toAccountField.value] && fromAccountField.value != '') {
        toAmountField.style.display = 'none';
        fromAmountTitle.innerHTML = 'Amount<span class="asteriskField">*</span>'
    } else {
        toAmountField.style.display = 'block';
        fromAmountTitle.innerHTML = 'From amount<span class="asteriskField">*</span>'
    };
});

// sets to_amount input field value when it is not visible
fromAmountInput.addEventListener("change", function() {
    if (toAmountField.style.display == 'none') {
        toAmountInput.value = fromAmountInput.value
    };
});

function validateAccounts(e) {
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