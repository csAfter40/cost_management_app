function setFormActions(url) {
    const deleteModalForms = document.querySelector('.deleteModalForm');
    deleteModalForms.forEach(function (deleteModalForm){
        deleteModalForm.setAttribute('action', url);
    });
};

function setFormInputs(id) {
    const modalIdInputs = document.querySelector('.modal-input-id');
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
};

setupDeleteButtons();