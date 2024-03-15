// Wait for the document to be fully loaded
$(document).ready(function () {
  // Function to display dependents in a table
  function displayDependents(dependentsData) {
    // Clear the existing dependents table
    $("#dependentsTableBody").empty();

    // Check if there are dependents to display
    if (dependentsData.length > 0) {
      // Iterate over the array of dependents
      dependentsData.forEach(function (dependent) {
        // Create a new table row
        var row = $("<tr>");

        // Create table data cells for each dependent's information
        var nameCell = $("<td>").text(dependent.name);
        var phoneNumberCell = $("<td>").text(dependent.phone_number);
        var relationshipCell = $("<td>").text(dependent.relationship);
        var dateCell = $("<td>").text(dependent.created_at);

        // Append the table data cells to the table row
        row.append(nameCell, phoneNumberCell, relationshipCell, dateCell);

        // Append the table row to the dependents table body
        $("#dependentsTableBody").append(row);
      });
    } else {
      // If there are no dependents, display a message indicating so
      $("#dependentsTableBody").append($("<tr>").append($("<td colspan='3'>").text("No dependents added yet.")));
    }
  }

  // Function to handle form submission for adding a dependent
  $("#addDependentForm").submit(function (event) {
    // Prevent the default form submission
    event.preventDefault();

    // Get the form data
    var formData = {
      name: $("#dependentName").val(),
      phone_number: $("#dependentPhoneNumber").val(),
      relationship: $("#dependentRelationship").val(),
      date: $("#dependentDate").val(),
    };

    // Make an AJAX POST request to add the dependent
    $.ajax({
      type: "POST",
      url: "/dependents/add",
      data: JSON.stringify(formData),
      contentType: "application/json",
      success: function (data) {
        // Handle success by adding the new dependent to the list
        console.log(data);

        fetchAndDisplayDependents();
        //displayDependents([data]);
        $("#successMessage").text("Dependent added successfully!");
        // Optionally display a success message
        $("#successMessage").text("Dependent added successfully!");
      },
      error: function (xhr, status, error) {
        // Handle error by displaying an error message
        console.error(error);
        $("#errorMessage").text("Failed to add dependent: " + error);
      },
    });
  });

  // Function to fetch and display the dependents when the page loads
  function fetchAndDisplayDependents() {
    // Make an AJAX GET request to fetch dependents data
    $.ajax({
      type: "GET",
      url: "/dependents",
      success: function (data) {
        // Display the fetched dependents
        displayDependents(data);
      },
      error: function (xhr, status, error) {
        // Handle error by displaying an error message
        console.error(error);
        $("#errorMessage").text("Failed to fetch dependents: " + error);
      },
    });
  }

  if (window.location.pathname === "/profile") {
    fetchAndDisplayDependents();
  }
  // Call the fetchAndDisplayDependents function when the page loads
  //fetchAndDisplayDependents();
});
