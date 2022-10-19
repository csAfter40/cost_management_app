const timeButtons = document.querySelectorAll('.select-time');
const reportTableDiv = document.querySelector('#report-table');
const timeButtonsDiv = document.querySelector('#time-buttons-div')

timeButtons.forEach(function (timeButton) {
    timeButton.addEventListener('click', handleTimeButtonEvent)
});

function handleTimeButtonEvent(event) {
    let currentButton = event.target;
    let path = currentButton.dataset.path;
    getData(path)
    setSelectedButton(currentButton);
};

function setSelectedButton(currentButton) {
    deselectAllButtons();
    currentButton.classList.remove("btn-outline-primary");
    currentButton.classList.add("btn-primary");
};

function deselectAllButtons() {
    timeButtons.forEach(function (timeButton) {
        timeButton.classList.remove("btn-primary");
        timeButton.classList.add("btn-outline-primary");
    });
};

function getData(path) {
    const url = window.location.pathname + path
    fetch(url, {
        method: "GET",
        headers: {}
    }).then(response => {
        return response.text();
    }).then(obj => {
        const parser = new DOMParser();
        const htmlDocument = parser.parseFromString(obj, "text/html");
        let reportTableHtml = htmlDocument.documentElement.querySelector('#report-table').innerHTML;
        const chartScriptHtml = htmlDocument.documentElement.querySelector('#chart-script').innerHTML;
        reportTableDiv.innerHTML = reportTableHtml;
        timeButtonsDiv.dataset.path = path;
        eval(chartScriptHtml);
    });
};
