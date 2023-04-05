
var expenseFormRadioBtns = document.querySelectorAll('input[name=expense_asset]');
var incomeFormRadioBtns = document.querySelectorAll('input[name=income_asset]');
 
function handleRadioButtonEvent(event) {
    let btn = event.target;
    let asset = btn.value;
    let form = btn.inputForm;
    btn.callback(asset, form)
};


let expenseForm = document.querySelector("#expense-input-form");
let incomeForm = document.querySelector("#income-input-form");

function setupFormRadioButtons(callback) {
    expenseFormRadioBtns.forEach(function(btn){
        btn.callback = callback;
        btn.inputForm = expenseForm;
        btn.addEventListener("click", handleRadioButtonEvent);
    });
    incomeFormRadioBtns.forEach(function(btn){
        btn.callback = callback;
        btn.inputForm = incomeForm;
        btn.addEventListener("click", handleRadioButtonEvent);
    });
};

export {setupFormRadioButtons}