const pgButtons = document.querySelectorAll('.pg-btn');
const transactionsDiv = document.querySelector('#transactions-table');
const paginatorDiv = document.querySelector('#paginator-div');

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
    getData(page);
};

function getData(page = 1) {
    const url = window.location.pathname + '/ajax' + `?page=${page}`
    fetch(url, {
        method: "GET",
        headers: {}
    }).then(response => {
        return response.text();
    }).then(obj => {
        const parser = new DOMParser();
        const htmlDocument = parser.parseFromString(obj, "text/html");
        let transactionHtml = htmlDocument.documentElement.querySelector('#transaction-table').innerHTML;
        const paginatorHtml = htmlDocument.documentElement.querySelector('#pagination-buttons').innerHTML;
        transactionsDiv.innerHTML = transactionHtml;
        paginatorDiv.innerHTML = paginatorHtml;
        setupPgButtons();
    });

};