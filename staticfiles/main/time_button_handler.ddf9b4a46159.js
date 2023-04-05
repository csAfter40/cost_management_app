const timeButtons = document.querySelectorAll('.select-time');
const timeButtonsDiv = document.querySelector('#time-buttons-div')

function handleTimeButtonEvent(event) {
    let currentButton = event.target;
    let path = currentButton.dataset.path;
    timeButtonsDiv.dataset.path = path;
    currentButton.callback()
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

function setupTimeButtons(callback) {
    timeButtons.forEach(function (timeButton) {
        timeButton.callback = callback
        timeButton.addEventListener('click', handleTimeButtonEvent)
    });
}

export {setupTimeButtons};