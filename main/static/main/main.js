// set autocomplete for expense and income name input fields
autocomplete_fields = document.querySelectorAll('.autocomplete');
for (let i = 0; i < autocomplete_fields.length; i++) {
    let obj = autocomplete_fields[i];
    let type = obj.dataset.type;
    let id = obj.id;
    new Autocomplete(`#${id}`, {
        search: input => {
            const url = `/autocomplete/transaction_name?type=${type}&name=${input}`
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
};

// datepickers for expense and income input forms
$(function () {
    $("#expense-datepicker").datepicker();
});

$(function () {
    $("#income-datepicker").datepicker();
});

$(function () {
    $("#transfer-datepicker").datepicker();
});

// transfer form validation. from_account and to_account fields can't have the same value
// transfer form amount input manipulation. There will be single amount input if the currencies of accounts are same.

// get json file from script tag
var accountData = JSON.parse(document.querySelector('#account-data').textContent);
const toAmountField = document.querySelector('#div_id_to_amount');
const toAmountInput = document.querySelector('#id_to_amount');
const fromAmountInput = document.querySelector('#id_from_amount');
const fromAmountField = document.querySelector('#div_id_from_amount');
const fromAmountTitle = fromAmountField.querySelector('label');
const fromAmountPrepend = fromAmountField.querySelector('.input-group-text');
const toAmountPrepend = toAmountField.querySelector('.input-group-text');
const fromAccountField = document.querySelector('#from-account-field');
const toAccountField = document.querySelector('#to-account-field');

fromAccountField.addEventListener("change", function () {
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

toAccountField.addEventListener("change", function () {
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
fromAmountInput.addEventListener("change", function () {
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
transferForm.addEventListener('submit', validateAccounts, true);

const accountTableDiv = document.querySelector('#account-table-div');
const loanTableDiv = document.querySelector('#loan-table-div');
const accountDeleteButtons = accountTableDiv.querySelectorAll('.delete-button');
const loanDeleteButtons = loanTableDiv.querySelectorAll('.delete-button');
const accountDeleteModal = document.querySelector('#deleteAccountModal');
const loanDeleteModal = document.querySelector('#deleteLoanModal');


// set account delete button events
accountDeleteButtons.forEach(function(button) {
    button.addEventListener('click', function(){
        const balance = parseFloat(button.parentElement.dataset.balance).toFixed(2);
        const currency = button.parentElement.dataset.currency;
        if (balance > 0) {
            const messageDiv = accountDeleteModal.querySelector('#modal-delete-message')
            messageDiv.innerHTML = `You have ${balance} ${currency} in your account. Do you really want to delete this account anyway?`;
        };
    })
});

// set loan delete button events
loanDeleteButtons.forEach(function(button) {
    button.addEventListener('click', function(){
        const balance = parseFloat(button.parentElement.dataset.balance).toFixed(2);
        const currency = button.parentElement.dataset.currency;
        if (balance < 0) {
            const messageDiv = loanDeleteModal.querySelector('#modal-delete-message')
            messageDiv.innerHTML = `You have ${balance} ${currency} loan to pay. Do you really want to delete this loan anyway?`;
        };
    })
});