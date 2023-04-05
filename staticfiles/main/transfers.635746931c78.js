const timeButtons = document.querySelectorAll('.select-time');
const pgButtons = document.querySelectorAll('.pg-btn');
const csrf = document.getElementsByName("csrfmiddlewaretoken")[0].value;
const tableDiv = document.querySelector('#object-list-table');
const paginatorDiv = document.querySelector('#paginator-div');
const tablePaginatorGroup = document.querySelector('#table-paginator-group');
const timeButtonsDiv = document.querySelector('#time-buttons-div')

timeButtons.forEach(function (timeButton) {
    timeButton.addEventListener('click', setSelectedButton)
});

function handleTimeButtonEvent(event) {
    let currentButton = event.currentTarget;
    let url = currentButton.dataset.url;
    handleFetchData(url);
    setSelectedButton(currentButton);
    setupPgButtons();
}

function handleFetchData(url) {
    data = getData(url);
    const parser = new DOMParser();
    tablePaginatorGroup.innerHTML = parser.parseFromString(data, "text/html");
}

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
    const url = timeButtonsDiv.dataset.url;
    getData(url, page);
};

function deselectAllButtons() {
    timeButtons.forEach(function (timeButton) {
        timeButton.classList.remove("btn-primary");
        timeButton.classList.add("btn-outline-primary");
    });
};

function getData(url, page = 1) {
    const url = window.location.pathname + url + `?page=${page}`
    fetch(url, {
        method: "GET",
        headers: {}
    }).then(response => {
        return response.text();
    }).then(data => {
        return data
    });

};

// set transfer delete button events
const deleteTransferButtons = document.querySelectorAll('.delete-transfer-button');
const deleteTransferIdInput = document.querySelector('#modal-transfer-id');
const deleteTransferModalForm = document.querySelector('#deleteTransferModalForm');

deleteTransferButtons.forEach(function (deleteTransferButton) {
    deleteTransferButton.addEventListener('click', function () {
        console.log('clicked');
        let transferId = deleteTransferButton.dataset.id;
        deleteTransferIdInput.setAttribute('value', transferId);
        let url = deleteTransferButton.dataset.url;
        console.log(url);
        deleteTransferModalForm.setAttribute('action', url);
    });
    
});
