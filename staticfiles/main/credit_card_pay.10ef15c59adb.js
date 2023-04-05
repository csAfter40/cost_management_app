const amountField = document.querySelector('#div_id_amount');
const amountPrepend = amountField.querySelector('.input-group-text');
const accountInput = document.querySelector('#account-field');
const cardInput = document.querySelector('#card-field');
const accountData = JSON.parse(document.querySelector('#account-data').textContent);
const cardData = JSON.parse(document.querySelector('#card-data').textContent);
const accountFieldMessage = document.querySelector('#account-field-message');
const cardFieldMessage = document.querySelector('#card-field-message');

$(function () {
    $("#card-pay-datepicker").datepicker();
});

cardInput.addEventListener('change', (event) => {
    amountPrepend.innerHTML = cardData[cardInput.value] || '-';
    if (cardInput.value != '' 
        && accountInput.value != '' 
        && cardData[cardInput.value] != accountData[accountInput.value]
    ){
        cardFieldMessage.innerHTML = 'Account and credit card currencies must be same!'
    } else {
        cardFieldMessage.innerHTML = '';
        accountFieldMessage.innerHTML = '';
    };
});

accountInput.addEventListener('change', (event) => {
    amountPrepend.innerHTML = accountData[accountInput.value] || '-';
    if (cardInput.value != '' 
        && accountInput.value != '' 
        && cardData[cardInput.value] != accountData[accountInput.value]
    ){
        accountFieldMessage.innerHTML = 'Account and credit card currencies must be same!'
    } else {
        cardFieldMessage.innerHTML = '';
        accountFieldMessage.innerHTML = '';
    };
});

// handle pay credit card form submit button
let payCreditCardFormSubmit = document.querySelector("#pay-card-submit")
payCreditCardFormSubmit.addEventListener("click", validatePositiveCardBalance);

function validatePositiveCardBalance(event) {
    const cardBalanceData = JSON.parse(document.querySelector("#card-balance-data").textContent)
    const accountBalanceData = JSON.parse(document.querySelector("#account-balance-data").textContent)
    var card = document.querySelector("#card-field").value;
    var cardBalance = parseFloat(cardBalanceData[card]);
    var account = document.querySelector("#account-field").value;
    var accountBalance = parseFloat(accountBalanceData[account]);
    var amount = Math.abs(parseFloat(document.querySelector("#id_amount").value));
    if (accountBalance >= 0 && amount > accountBalance) {
        if (!confirm("Account balance will be negative. Do you really want to proceed?")) {
            event.preventDefault();
            return false;
        };
    };
    if (cardBalance <= 0 && amount > Math.abs(cardBalance)) {
        if (!confirm("Payment exceeds credit card balance. Do you really want to proceed?")) {
            event.preventDefault();
            return false;
        };
    };
    return true;
};