const amountField = document.querySelector('#div_id_amount');
const amountPrepend = amountField.querySelector('.input-group-text');
const accountInput = document.querySelector('#account-field');
const loanInput = document.querySelector('#loan-field');
const accountData = JSON.parse(document.querySelector('#account-data').textContent);
const loanData = JSON.parse(document.querySelector('#loan-data').textContent);
const accountFieldMessage = document.querySelector('#account-field-message');
const loanFieldMessage = document.querySelector('#loan-field-message');
console.log(loanFieldMessage);

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