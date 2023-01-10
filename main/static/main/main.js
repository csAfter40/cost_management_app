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