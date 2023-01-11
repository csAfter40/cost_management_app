let currencySelect = document.querySelector("#currency-input");
let submitButton = document.querySelector("#submit-btn");
currencySelect.addEventListener("change", (event) => {
    submitButton.disabled = false;
});