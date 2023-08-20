const renderChart = (data, categories) => {
  var ctx = document.getElementById("myChart");

  var myChart = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: categories,
      datasets: [
        {
          label: "Last 6 month's",
          data: data,
          borderWidth: 1,
          backgroundColor: [
            "#FF6384", // Red
            "#36A2EB", // Blue
            "#FFCE56", // Yellow
            "#4CAF50", // Green
            "#9C27B0", // Purple
            "#FF9800", // Orange
          ],
          borderColor: [
            "#FF6384", // Red
            "#36A2EB", // Blue
            "#FFCE56", // Yellow
            "#4CAF50", // Green
            "#9C27B0", // Purple
            "#FF9800", // Orange
          ],
        },
      ],
    },
    options: {
      title: {
        display: true,
        text: `${transaction_type}s per Category`,
      },
    },
  });
};

const getChartData = () => {
  if (transaction_type == "Expense") {
    var fetch_type = "expense";
  }
  if (transaction_type == "Income") {
    var fetch_type = "income";
  }

  console.log(`${fetch_type}`);
  fetch(`/summary/${fetch_type}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((res) => res.json())
    .then((results) => {
      const category_data = results.categories_amount_summary;

      const [categories, data] = [
            Object.keys(results.categories_amount_summary),
            Object.values(results.categories_amount_summary)
          ]

      renderChart(data, categories);
    });
};

// const getChartData = () => {
//   const [categories, data] = [
//     Object.keys(summary),
//     Object.values(summary)
//   ]
//   renderChart([...data], [...categories])
// }

document.onload = getChartData();
