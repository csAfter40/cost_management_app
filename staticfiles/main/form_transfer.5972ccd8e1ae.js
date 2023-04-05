// date field datepicker
$(function () {
    $("#transfer-datepicker").datepicker();
});

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

// callback functions for account field change event
// transfer form amount input manipulation. There will be single amount input if the currencies of accounts are same.
function fromAccountChange(){
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
};

function toAccountChange(){
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
};

// setup account field events
fromAccountField.addEventListener("change", fromAccountChange);
toAccountField.addEventListener("change", toAccountChange);

//setup fields with existing values(edit view)
fromAccountChange();
toAccountChange();

// sets to_amount input field value when it is not visible
fromAmountInput.addEventListener("change", function () {
    if (toAmountField.style.display == 'none') {
        toAmountInput.value = fromAmountInput.value
    };
});

// transfer form validation. from_account and to_account fields can't have the same value
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

