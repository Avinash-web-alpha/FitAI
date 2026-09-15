const ctx = document.getElementById('fitnessChart');

new Chart(ctx, {
    type: 'bar',
    data: {
        labels: ['BMI', 'Fitness Score', 'Water ×10'],
        datasets: [{
            label: 'Health Metrics',
            data: [
                Number("{{ bmi }}"),
                Number("{{ score }}"),
                Number("{{ water }}") * 10
                 ],
            data: chartData,
            backgroundColor: [
                '#00ff99',
                '#00ccff',
                '#ffcc00'
            ]
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                display: false
            }
        }
    }
});