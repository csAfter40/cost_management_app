// set autocomplete for expense and income name input fields
autocomplete_fields = document.querySelectorAll('.autocomplete');
for (let i=0; i<autocomplete_fields.length; i++) {
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
transferForm.addEventListener('submit', validateAccounts, true);

// set account delete button events
const deleteAccountButtons = document.querySelectorAll('.delete-account-button');
const deleteAccountMessageDiv = document.querySelector('#modal-account-delete-message');
const deleteAccountIdInput = document.querySelector('#modal-account-id');

deleteAccountButtons.forEach(function(deleteAccountButton){
    deleteAccountButton.addEventListener('click', function(){
        let accountId = deleteAccountButton.dataset.id;
        deleteAccountIdInput.setAttribute('value', accountId);
        let balance = parseFloat(deleteAccountButton.dataset.balance).toFixed(2);
        
        let currency = deleteAccountButton.dataset.currency;
        if (balance > 0) {
            deleteAccountMessageDiv.innerHTML = `You have ${balance} ${currency} in your account. Do you really want to delete this account anyway?`;
        } else {
            deleteAccountMessageDiv.innerHTML = 'Do you really want to delete this account?';
        };
    });
});

// set loan delete button events
const deleteLoanButtons = document.querySelectorAll('.delete-loan-button');
const deleteLoanMessageDiv = document.querySelector('#modal-loan-delete-message');
const deleteLoanIdInput = document.querySelector('#modal-loan-id');
console.log(deleteLoanIdInput);

deleteLoanButtons.forEach(function(deleteLoanButton){
    deleteLoanButton.addEventListener('click', function(){
        let loanId = deleteLoanButton.dataset.id;
        deleteLoanIdInput.setAttribute('value', loanId);
        console.log(deleteLoanIdInput);

        let balance = parseFloat(deleteLoanButton.dataset.balance).toFixed(2);
        
        let currency = deleteLoanButton.dataset.currency;
        if (balance < 0) {
            deleteAccountMessageDiv.innerHTML = `You have ${balance} ${currency} loan to pay. Do you really want to delete this loan anyway?`;
        } else if(balance > 0){
            deleteAccountMessageDiv.innerHTML = `You have ${balance} ${currency}. Do you really want to delete this loan anyway?`;
        } else {
            deleteAccountMessageDiv.innerHTML = 'Do you really want to delete this loan?';
        };
    });
});