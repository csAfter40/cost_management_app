const timeButtons = document.querySelectorAll('.select-time');
const pgButtons = document.querySelectorAll('.pg-btn');
const tableDiv = document.querySelector('#object-list-table');
const paginatorDiv = document.querySelector('#paginator-div');
const tablePaginatorGroup = document.querySelector('#table-paginator-group');
const timeButtonsDiv = document.querySelector('#time-buttons-div')

timeButtons.forEach(function (timeButton) {
    timeButton.addEventListener('click', handleTimeButtonEvent)
});

function handleTimeButtonEvent(event) {
    let currentButton = event.target;
    let path = currentButton.dataset.path;
    getData(path)
    setSelectedButton(currentButton);
    setupPgButtons();
};

function setSelectedButton(currentButton) {
    deselectAllButtons();
    currentButton.classList.remove("btn-outline-primary");
    currentButton.classList.add("btn-primary");
};

setupPgButtons();

function setupPgButtons() {
    const pgButtons = document.querySelectorAll('.pg-btn');
    pgButtons.forEach(function (pgButton) {
        pgButton.addEventListener('click', pgEventHandler);
    });
};

function pgEventHandler(event) {
    const currentButton = event.currentTarget;
    const page = currentButton.dataset.page;
    const path = timeButtonsDiv.dataset.path;
    getData(path, page);
};

function deselectAllButtons() {
    timeButtons.forEach(function (timeButton) {
        timeButton.classList.remove("btn-primary");
        timeButton.classList.add("btn-outline-primary");
    });
};

function getData(path, page = 1) {
    const url = window.location.pathname + path + `?page=${page}`

    fetch(url, {
        method: "GET",
        headers: {}
    }).then(response => {
        return response.text();
    }).then(data => {
        tablePaginatorGroup.innerHTML = data;
        timeButtonsDiv.dataset.path = path;
        setupPgButtons();
    });
};

// set transfer delete button events
const deleteTransferButtons = document.querySelectorAll('.delete-transfer-button');
const deleteTransferIdInput = document.querySelector('#modal-transfer-id');
const deleteTransferModalForm = document.querySelector('#deleteTransferModalForm');

deleteTransferButtons.forEach(function (deleteTransferButton) {
    deleteTransferButton.addEventListener('click', function () {
        let transferId = deleteTransferButton.dataset.id;
        deleteTransferIdInput.setAttribute('value', transferId);
        let url = deleteTransferButton.dataset.url;
        deleteTransferModalForm.setAttribute('action', url);
    });
    
});
