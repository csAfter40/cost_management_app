const data = {
    labels: [
      'Red',
      'Blue',
      'Yellow'
    ],
    datasets: [{
      label: 'My First Dataset',
      data: [300, 50, 100],
      backgroundColor: [
        'rgb(255, 99, 132)',
        'rgb(54, 162, 235)',
        'rgb(255, 205, 86)'
      ],
      hoverOffset: 4
    }]
  };

const config = {
    type: 'pie',
    data: data,
};

const expensesCtx = document.querySelector('#expencesChart');
const incomesCtx = document.querySelector('#incomesChart');
const expensesChart = new Chart(expensesCtx, config);
const incomesChart = new Chart(incomesCtx, config);