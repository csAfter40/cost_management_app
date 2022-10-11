// set transfer delete button events
const deleteTransferButtons = document.querySelectorAll('.delete-transfer-button');
// const deleteTransactionMessageDiv = document.querySelector('#modal-transaction-delete-message');
const deleteTransferIdInput = document.querySelector('#modal-transfer-id');
const deleteTransferModalForm = document.querySelector('#deleteTransferModalForm');

deleteTransferButtons.forEach(function (deleteTransferButton) {
    deleteTransferButton.addEventListener('click', function () {
        console.log('clicked');
        let transferId = deleteTransferButton.dataset.id;
        deleteTransferIdInput.setAttribute('value', transferId);
        let url = deleteTransferButton.dataset.url;
        console.log(url);
        deleteTransferModalForm.setAttribute('action', url);
    });
    
});
