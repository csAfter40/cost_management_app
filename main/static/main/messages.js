function removeAlertBoxes() {
    let alerts = document.querySelectorAll(".auto-hide-alert");
    alerts.forEach(alert => {
        alert.style.animationPlayState = 'running';
        alert.addEventListener('animationend', () => {
            alert.remove()
        });
    });
};

document.addEventListener("DOMContentLoaded", (event) => {
    setTimeout(() => {
        removeAlertBoxes()     
    }, 5000);
});