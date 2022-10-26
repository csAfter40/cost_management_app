function setFormActions(url) {
    const deleteModalForms = document.querySelectorAll('.deleteModalForm');
    deleteModalForms.forEach(function (deleteModalForm){
        deleteModalForm.setAttribute('action', url);
    });
};

function setFormInputs(id) {
    console.log('called')
    const modalIdInputs = document.querySelectorAll('.modal-input-id');
    modalIdInputs.forEach(function (modalIdInput){
        modalIdInput.setAttribute('value', id);
    });
};

function setupDeleteButtons(){
    const deleteButtons = document.querySelectorAll('.delete-button');
    deleteButtons.forEach(function (deleteButton) {
        deleteButton.addEventListener('click', function () {
            setFormInputs(deleteButton.dataset.id);
            setFormActions(deleteButton.dataset.url);
        });
    });
}

setupDeleteButtons();

export {setupDeleteButtons};