new Autocomplete('#autocomplete_expense', {
    search: input => {
        const url = `/autocomplete/expense_name?name=${input}`
        return new Promise(resolve => {
            fetch(url)
            .then(response => response.json())
            .then(data => {
                console.log(data)
                resolve(data.data)
            })
        })
    }
});

new Autocomplete('#autocomplete_income', {
    search: input => {
        const url = `/autocomplete/income_name?name=${input}`
        return new Promise(resolve => {
            fetch(url)
            .then(response => response.json())
            .then(data => {
                console.log(data)
                resolve(data.data)
            })
        })
    }
});

// datepickers for expense and income input forms
$( function() {
    $( "#expense-datepicker" ).datepicker();
  } );

$( function() {
    $( "#income-datepicker" ).datepicker();
  } );