function setupPgButtons(callback, htmlDocument=document) {
    const pgButtons = htmlDocument.querySelectorAll('.pg-btn');
    pgButtons.forEach(function (pgButton) {
        pgButton.callback = callback;
        pgButton.addEventListener('click', pgEventHandler);
    });
};

function pgEventHandler(event) {
    const currentButton = event.currentTarget;
    const page = currentButton.dataset.page;
    currentButton.callback(page);
};

export {setupPgButtons}