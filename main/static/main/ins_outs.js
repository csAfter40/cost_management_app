import {setupDeleteButtons} from "./delete_button_handler.js";
import { setupTimeButtons } from "./time_button_handler.js";
import {setupPgButtons} from "./paginator_buttons_handler.js";

const reportTableDiv = document.querySelector('#report-table');
const tablePaginatorGroup = document.querySelector('#table-paginator-group');
const timeButtonsDiv = document.querySelector('#time-buttons-div')

setupDeleteButtons();
setupTimeButtons(getData);
setupPgButtons(getData);

function getData(page=1) {
    const path = timeButtonsDiv.dataset.path;
    const url = window.location.pathname + path + `?page=${page}`
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
        const tablePaginatorHtml = htmlDocument.documentElement.querySelector('#table-paginator-group').innerHTML;
        tablePaginatorGroup.innerHTML = tablePaginatorHtml
        setupDeleteButtons();
        setupPgButtons(getData);
        eval(chartScriptHtml);
    });
};
