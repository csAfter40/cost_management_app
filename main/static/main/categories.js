const deleteExpenseButtons = document.querySelectorAll(".delete-expense-button");
const deleteIncomeButtons = document.querySelectorAll(".delete-income-button");
const createExpenseSubcategoryButtons = document.querySelectorAll(".create-expense-subcategory-button");
const createIncomeSubcategoryButtons = document.querySelectorAll(".create-income-subcategory-button");
const expenseInput = document.querySelector("#expense-category-id");
const incomeInput = document.querySelector("#income-category-id");
const expenseParentInput = document.querySelector("#expense-parent-category-id");
const expenseParentNameSpan = document.querySelector("#modal-expense-category-name");
const incomeParentInput = document.querySelector("#income-parent-category-id");
const incomeParentNameSpan = document.querySelector("#modal-income-category-name");
// set events for delete expense category buttons
for (let i=0; i<deleteExpenseButtons.length; i++){
    deleteExpenseButtons[i].addEventListener('click', function(){
        var categoryId = deleteExpenseButtons[i].getAttribute('data-node-id');
        expenseInput.setAttribute('value', categoryId);
    });
};
// set events for delete income category buttons
for (let i=0; i<deleteIncomeButtons.length; i++){
    deleteIncomeButtons[i].addEventListener('click', function(){
        var categoryId = deleteIncomeButtons[i].getAttribute('data-node-id');
        incomeInput.setAttribute('value', categoryId);
    });
};
// set events for create expense subcategory buttons
for (let i=0; i<createExpenseSubcategoryButtons.length; i++){
    createExpenseSubcategoryButtons[i].addEventListener('click', function(){
        var categoryId = createExpenseSubcategoryButtons[i].getAttribute('data-node-id');
        var categoryName = createExpenseSubcategoryButtons[i].getAttribute('data-node-name');
        expenseParentInput.setAttribute('value', categoryId);
        expenseParentNameSpan.innerHTML = categoryName;
    });
};
// set events for create income subcategory buttons
for (let i=0; i<createIncomeSubcategoryButtons.length; i++){
    createIncomeSubcategoryButtons[i].addEventListener('click', function(){
        var incomeCategoryId = createIncomeSubcategoryButtons[i].getAttribute('data-node-id');
        var incomeCategoryName = createIncomeSubcategoryButtons[i].getAttribute('data-node-name');
        incomeParentInput.setAttribute('value', incomeCategoryId);
        incomeParentNameSpan.innerHTML = incomeCategoryName;
    });
};