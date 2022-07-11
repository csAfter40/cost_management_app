const timeButtons = document.querySelectorAll('.select-time');
const pgButtons = document.querySelectorAll('.pg-btn');
const csrf = document.getElementsByName("csrfmiddlewaretoken")[0].value;
const transactionsDiv = document.querySelector('#transactions-table');
const accountStats = document.querySelector('#account-stats-div');
const paginatorDiv = document.querySelector('#paginator-div');

timeButtons.forEach(function (timeButton) {
    timeButton.addEventListener('click', setSelectedButton)
});

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
    const time = transactionsDiv.dataset.time;
    getData(time, page);
};

function setSelectedButton(event) {
    let currentButton = event.currentTarget;
    let time = currentButton.dataset.time;
    getData(time);
    disableAllButtons();
    currentButton.classList.remove("btn-outline-primary");
    currentButton.classList.add("btn-primary");
};

function disableAllButtons() {
    timeButtons.forEach(function (timeButton) {
        timeButton.classList.remove("btn-primary");
        timeButton.classList.add("btn-outline-primary");
    });
}

function getData(time, page = 1) {
    const url = window.location.pathname + '/ajax' + `?time=${time}` + `&page=${page}`
    fetch(url, {
        method: "GET",
        headers: {}
    }).then(response => {
        return response.text()
    }).then(obj => {
        const parser = new DOMParser();
        const htmlDocument = parser.parseFromString(obj, "text/html");
        let transactionHtml = htmlDocument.documentElement.querySelector('#transaction-table').innerHTML;
        let statHtml = htmlDocument.documentElement.querySelector('#account-stats').innerHTML;
        const paginatorHtml = htmlDocument.documentElement.querySelector('#pagination-buttons').innerHTML;
        const chartScriptHtml = htmlDocument.documentElement.querySelector('#chart-script').innerHTML;
        transactionsDiv.innerHTML = transactionHtml;
        transactionsDiv.dataset.time = time;
        accountStats.innerHTML = statHtml;
        paginatorDiv.innerHTML = paginatorHtml;
        setupPgButtons();
        eval(chartScriptHtml);
    });

};