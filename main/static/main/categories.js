const deleteExpenseButtons = document.querySelectorAll(".delete-expense-button");
const deleteIncomeButtons = document.querySelectorAll(".delete-income-button");
const expenseInput = document.querySelector("#expense-category-id");
const incomeInput = document.querySelector("#income-category-id");
for (let i=0; i<deleteExpenseButtons.length; i++){
    deleteExpenseButtons[i].addEventListener('click', function(){
        var categoryId = deleteExpenseButtons[i].getAttribute('data-node-id');
        expenseInput.setAttribute('value', categoryId);
    });
};
for (let i=0; i<deleteIncomeButtons.length; i++){
    deleteIncomeButtons[i].addEventListener('click', function(){
        var categoryId = deleteIncomeButtons[i].getAttribute('data-node-id');
        incomeInput.setAttribute('value', categoryId);
    });
};