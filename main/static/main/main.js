import {setupDeleteButtons} from "./delete_button_handler.js";

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
    $("#expense-datepicker").datepicker();
});

$(function () {
    $("#income-datepicker").datepicker();
});

// handle expense input form submit button
let expenseFormSubmit = document.querySelector("#expense-submit")
expenseFormSubmit.addEventListener("click", validateNegativeAccountBalance);

function validateNegativeAccountBalance(event) {
    console.log("function called")
    const balanceData = JSON.parse(document.querySelector("#account-balance-data").textContent)
    var account = document.querySelector("#id_content_object").value;
    console.log(account)
    var balance = parseFloat(balanceData[account]);
    console.log(balance)
    var amount = Math.abs(parseFloat(document.querySelector("#id_amount").value));
    console.log(amount)
    if (balance > 0 && amount > balance) {
        if (!confirm("Account balance will be negative. Do you really want to proceed?")) {
            event.preventDefault();
            return false;
        };
    };
    return true;
};