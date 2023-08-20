console.log(transaction_type)

const searchField = document.querySelector("#searchField");
const table = document.querySelector(".table");
const tableOutput = document.querySelector("#table-output");
const tableApp = document.querySelector("#table-app");
const paginationContainer = document.querySelector(".pagination-container");

searchField.addEventListener("keyup", (e) => {
  const searchValue = e.target.value;

  if (searchValue.trim().length > 0) {
    fetch("/search-expenses", {
      body: JSON.stringify({ searchText: searchValue, type: transaction_type }),
      method: "POST",
    })
      .then((res) => res.json())
      .then((data) => {
        tableApp.style.display = "none";
        tableOutput.style.display = "table-row-group";
        paginationContainer.style.display = "none";

        console.log(data);
        if (data.length === 0) {
          tableOutput.innerHTML = "<br><h5><b>No any results found</b></h5>";
        } else {
          tableOutput.innerHTML = "";
          data.forEach((expense) => {
            tableOutput.innerHTML += `
          <tr>
          <td>${expense.amount}</td>
          <td>${expense.category}</td>
          <td>${expense.description}</td>
          <td>${expense.date}</td>

          <td>
            <a
              href="/edit-expense/${expense.id}"
              class="btn btn-secondary btn-sm"
              >Edit</a
            >
          </td>
        </tr>
          `;
          });
        }
      });
  } else {
    tableApp.style.display = "table-row-group";
    tableOutput.style.display = "none";
    paginationContainer.style.display = "block";
  }
});
