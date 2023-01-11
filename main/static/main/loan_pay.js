const amountField = document.querySelector('#div_id_amount');
const amountPrepend = amountField.querySelector('.input-group-text');
const accountInput = document.querySelector('#account-field');
const loanInput = document.querySelector('#loan-field');
const accountData = JSON.parse(document.querySelector('#account-data').textContent);
const loanData = JSON.parse(document.querySelector('#loan-data').textContent);
const accountFieldMessage = document.querySelector('#account-field-message');
const loanFieldMessage = document.querySelector('#loan-field-message');

$(function () {
    $("#loan-pay-datepicker").datepicker();
});

loanInput.addEventListener('change', (event) => {
    amountPrepend.innerHTML = loanData[loanInput.value] || '-';
    if (loanInput.value != '' 
        && accountInput.value != '' 
        && loanData[loanInput.value] != accountData[accountInput.value]
    ){
        loanFieldMessage.innerHTML = 'Account and loan currencies must be same!'
    } else {
        loanFieldMessage.innerHTML = '';
        accountFieldMessage.innerHTML = '';
    };
});

accountInput.addEventListener('change', (event) => {
    amountPrepend.innerHTML = accountData[accountInput.value] || '-';
    if (loanInput.value != '' 
        && accountInput.value != '' 
        && loanData[loanInput.value] != accountData[accountInput.value]
    ){
        accountFieldMessage.innerHTML = 'Account and loan currencies must be same!'
    } else {
        loanFieldMessage.innerHTML = '';
        accountFieldMessage.innerHTML = '';
    };
});

// handle pay loan form submit button
let payLoanFormSubmit = document.querySelector("#pay-loan-submit")
payLoanFormSubmit.addEventListener("click", validatePositiveLoanBalance);

function validatePositiveLoanBalance(event) {
    const loanBalanceData = JSON.parse(document.querySelector("#loan-balance-data").textContent)
    const accountBalanceData = JSON.parse(document.querySelector("#account-balance-data").textContent)
    var loan = document.querySelector("#loan-field").value;
    var loanBalance = parseFloat(loanBalanceData[loan]);
    var account = document.querySelector("#account-field").value;
    var accountBalance = parseFloat(accountBalanceData[account]);
    var amount = Math.abs(parseFloat(document.querySelector("#id_amount").value));
    console.log(accountBalance)
    console.log(amount)
    if (accountBalance >= 0 && amount > accountBalance) {
        if (!confirm("Account balance will be negative. Do you really want to proceed?")) {
            event.preventDefault();
            return false;
        };
    };
    if (loanBalance <= 0 && amount > Math.abs(loanBalance)) {
        if (!confirm("Payment exceeds loan balance. Do you really want to proceed?")) {
            event.preventDefault();
            return false;
        };
    };
    return true;
};