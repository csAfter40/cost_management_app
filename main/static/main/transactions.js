import {setupDeleteButtons} from "./delete_button_handler.js";
import { setupTimeButtons } from "./time_button_handler.js";
import {setupPgButtons} from "./paginator_buttons_handler.js";

const tablePaginatorGroup = document.querySelector('#table-paginator-group');
const timeButtonsDiv = document.querySelector('#time-buttons-div')

setupTimeButtons(getData);
setupPgButtons(getData);
setupDeleteButtons();

function getData(page = 1) {
    const path = timeButtonsDiv.dataset.path;
    const url = window.location.pathname + path + `?page=${page}`

    fetch(url, {
        method: "GET",
        headers: {}
    }).then(response => {
        return response.text();
    }).then(data => {
        tablePaginatorGroup.innerHTML = data;
        setupPgButtons(getData);
        setupDeleteButtons();
    });
};
