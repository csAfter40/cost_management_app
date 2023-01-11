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

// handle not editable transfers. user may not be able to click on transfer edit or delete links that are not editable.
let editLinks = document.querySelectorAll(".edit-link");
editLinks.forEach(function(link) {
    link.addEventListener("click", function(event) {
        if (link.dataset.editable == "False") {
            alert("This transfer has deleted account(s) and is not editable.")
            event.preventDefault();
            return false;
        };
    });
});

// prevent modal toggle in case transfer is not editable
let modal = document.querySelector("#deleteTransferModal");
modal.addEventListener("show.bs.modal", function(event){
    var button = event.relatedTarget;
    if (button.dataset.editable == "False") {
        alert("This transfer has deleted account(s) and is not editable.")
        event.preventDefault();
        return false;
    };
});