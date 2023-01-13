import {setupDeleteButtons} from "./delete_button_handler.js";
import {setupPgButtons} from "./paginator_buttons_handler.js";

setupDeleteButtons();

// set autocomplete for expense and income name input fields
var autocomplete_fields = document.querySelectorAll('.autocomplete');
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
    $("#expense-datepicker").datepicker({maxDate: '0'});
});

$(function () {
    $("#income-datepicker").datepicker({maxDate: '0'});
});

// handle expense input form submit button
let expenseFormSubmit = document.querySelector("#expense-submit")
expenseFormSubmit.account = document.querySelector("#id_content_object");
expenseFormSubmit.amount = document.querySelector("#id_amount");
expenseFormSubmit.addEventListener("click", validateNegativeAccountBalance);

// handle transfer form submit button
let transferFormSubmit = document.querySelector("#transfer-submit")
transferFormSubmit.account = document.querySelector("#from-account-field")
transferFormSubmit.amount = document.querySelector("#id_from_amount")
transferFormSubmit.addEventListener("click", validateNegativeAccountBalance);

function validateNegativeAccountBalance(event) {
    const balanceData = JSON.parse(document.querySelector("#account-balance-data").textContent)
    var account = event.currentTarget.account.value
    var balance = parseFloat(balanceData[account]);
    var amount = Math.abs(parseFloat(event.currentTarget.amount.value));
    if (balance >= 0 && amount > balance) {
        if (!confirm("Account balance will be negative. Do you really want to proceed?")) {
            event.preventDefault();
            return false;
        };
    };
    return true;
};

let accountsTableDiv = document.querySelector("#accounts-table");
let loansTableDiv = document.querySelector("#loans-table");

addEventListener("DOMContentLoaded", (event) => {
    getAccountData();
    getLoanData();
});

function getAccountData(page=1) {
    const url = accountsTableDiv.dataset.url + `?page=${page}`
    fetch(url, {
        method: "GET",
        headers: {}
    }).then(response => {
        return response.text();
    }).then(obj => {
        accountsTableDiv.innerHTML = obj;
        setupPgButtons(getAccountData, accountsTableDiv);
        setupDeleteButtons();
    });
};

function getLoanData(page=1) {
    const url = loansTableDiv.dataset.url + `?page=${page}`
    fetch(url, {
        method: "GET",
        headers: {}
    }).then(response => {
        return response.text();
    }).then(obj => {
        loansTableDiv.innerHTML = obj;
        setupPgButtons(getLoanData, loansTableDiv);
        setupDeleteButtons();
    });
};