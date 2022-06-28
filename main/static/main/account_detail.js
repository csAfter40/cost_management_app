const timeButtons = document.querySelectorAll('.select-time')
const csrf = document.getElementsByName("csrfmiddlewaretoken")[0].value;
const transactionsDiv = document.querySelector('#transactions-table')

timeButtons.forEach(function(timeButton) {
    timeButton.addEventListener('click', setSelectedButton)
});

function setSelectedButton(event) {
    let currentButton = event.currentTarget;
    let time = currentButton.dataset.time
    getData(time);
    disableAllButtons();
    currentButton.classList.remove("btn-outline-primary");
    currentButton.classList.add("btn-primary");
};

function disableAllButtons() {
    timeButtons.forEach(function(timeButton) {
        timeButton.classList.remove("btn-primary");
        timeButton.classList.add("btn-outline-primary");
    });
}

function getData(time){
    fetch("", {
        method: "PUT",
        body: JSON.stringify({
            time: time
        }),
        headers: {'X-CSRFToken': csrf}
    }).then(response => {
        return response.text()
    }).then(obj => {
        transactionsDiv.innerHTML = obj;
    });

};