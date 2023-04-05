const deleteExpenseButtons = document.querySelectorAll(".delete-expense-button");
const deleteIncomeButtons = document.querySelectorAll(".delete-income-button");
const createExpenseSubcategoryButtons = document.querySelectorAll(".create-expense-subcategory-button");
const createIncomeSubcategoryButtons = document.querySelectorAll(".create-income-subcategory-button");
const editExpenseButtons = document.querySelectorAll(".edit-expense-button");
const editIncomeButtons = document.querySelectorAll(".edit-income-button");
const expenseInput = document.querySelector("#expense-category-id");
const incomeInput = document.querySelector("#income-category-id");
const editExpenseNameInput = document.querySelector("#expenseCategoryNameInput");
const editIncomeNameInput = document.querySelector("#incomeCategoryNameInput");
const editExpenseIdInput = document.querySelector("#edit-expense-category-id");
const editIncomeIdInput = document.querySelector("#edit-income-category-id");
const expenseParentInput = document.querySelector("#expense-parent-category-id");
const expenseParentNameSpan = document.querySelector("#modal-expense-category-name");
const incomeParentInput = document.querySelector("#income-parent-category-id");
const incomeParentNameSpan = document.querySelector("#modal-income-category-name");
const deleteExpenseCategoryModalForm = document.querySelector('#deleteExpenseCategoryModalForm');
const deleteIncomeCategoryModalForm = document.querySelector('#deleteIncomeCategoryModalForm');


// set events for delete expense category buttons
deleteExpenseButtons.forEach(button => {
    button.addEventListener('click', function() {
        deleteExpenseCategoryModalForm.setAttribute('action', button.dataset.url);
    });
});

// set events for delete income category buttons
deleteIncomeButtons.forEach(button => {
    console.log(button.dataset.url);
    button.addEventListener('click', function() {
        deleteIncomeCategoryModalForm.setAttribute('action', button.dataset.url);
    });
});


// set events for create expense subcategory buttons
for (let i = 0; i < createExpenseSubcategoryButtons.length; i++) {
    createExpenseSubcategoryButtons[i].addEventListener('click', function () {
        var categoryId = createExpenseSubcategoryButtons[i].getAttribute('data-node-id');
        var categoryName = createExpenseSubcategoryButtons[i].getAttribute('data-node-name');
        expenseParentInput.setAttribute('value', categoryId);
        expenseParentNameSpan.innerHTML = categoryName;
    });
};
// set events for create income subcategory buttons
for (let i = 0; i < createIncomeSubcategoryButtons.length; i++) {
    createIncomeSubcategoryButtons[i].addEventListener('click', function () {
        var incomeCategoryId = createIncomeSubcategoryButtons[i].getAttribute('data-node-id');
        var incomeCategoryName = createIncomeSubcategoryButtons[i].getAttribute('data-node-name');
        incomeParentInput.setAttribute('value', incomeCategoryId);
        incomeParentNameSpan.innerHTML = incomeCategoryName;
    });
};
// set events for edit expense category buttons
for (let i = 0; i < editExpenseButtons.length; i++) {
    editExpenseButtons[i].addEventListener('click', function () {
        var categoryId = editExpenseButtons[i].getAttribute('data-node-id');
        var categoryName = editExpenseButtons[i].getAttribute('data-node-name');
        editExpenseIdInput.setAttribute('value', categoryId);
        editExpenseNameInput.setAttribute('value', categoryName);
    });
};
// set events for edit income category buttons
for (let i = 0; i < editIncomeButtons.length; i++) {
    editIncomeButtons[i].addEventListener('click', function () {
        var categoryId = editIncomeButtons[i].getAttribute('data-node-id');
        var categoryName = editIncomeButtons[i].getAttribute('data-node-name');
        editIncomeIdInput.setAttribute('value', categoryId);
        editIncomeNameInput.setAttribute('value', categoryName);
    });
};