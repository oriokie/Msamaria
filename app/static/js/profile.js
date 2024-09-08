$(document).ready(function () {
  // Function to display dependents in a table
  function displayDependents(dependentsData) {
    const $tableBody = $("#dependentsTableBody");
    $tableBody.empty();

    if (dependentsData.length > 0) {
      dependentsData.forEach(function (dependent) {
        const row = $("<tr>").append(
          $("<td>").text(dependent.name),
          $("<td>").text(dependent.phone_number || "N/A"),
          $("<td>").text(dependent.relationship || "N/A"),
          $("<td>").text(new Date(dependent.created_at).toLocaleDateString()),
          $("<td>").text(dependent.is_deceased ? "Deceased" : "Alive")
        );
        $tableBody.append(row);
      });
    } else {
      $tableBody.append($("<tr>").append($("<td colspan='5'>").text("No dependents added yet.")));
    }
  }

  // Function to handle form submission for adding a dependent
  $("#addDependentForm").submit(function (event) {
    event.preventDefault();

    const formData = {
      name: $("#dependentName").val().trim(),
      phone_number: $("#dependentPhoneNumber").val().trim(),
      relationship: $("#dependentRelationship").val(),
    };

    // Basic form validation
    if (!formData.name) {
      showMessage("Please enter a name for the dependent.", "error");
      return;
    }

    $.ajax({
      type: "POST",
      url: "/dependents/add",
      data: JSON.stringify(formData),
      contentType: "application/json",
      success: function (data) {
        console.log("Dependents data received:", data);
        displayDependents(data);
        $("#addDependentForm")[0].reset();
        showMessage("Dependent added successfully!", "success");
      },
      error: function (xhr, status, error) {
        console.error("Error adding dependent:", error);
        console.error("Server response:", xhr.responseText);
        showMessage("Failed to add dependent: " + (xhr.responseJSON?.error || error), "error");
      },
    });
  });

  // Function to fetch and display the dependents
  function fetchAndDisplayDependents() {
    $.ajax({
      type: "GET",
      url: "/dependents/",
      success: function (data) {
        console.log("Dependents data received:", data);
        displayDependents(data);
      },
      error: function (xhr, status, error) {
        console.error("Error fetching dependents:", error);
        console.error("Server response:", xhr.responseText);
        showMessage("Failed to fetch dependents: " + (xhr.responseJSON?.error || error), "error");
      },
    });
  }

  // Function to show messages (success or error)
  function showMessage(message, type) {
    const $messageElement = type === "success" ? $("#successMessage") : $("#errorMessage");
    $messageElement.text(message).show().delay(5000).fadeOut();
  }

  // Initialize dependents tab
  function initDependentsTab() {
    const $dependentsTab = $("#dependents-tab");
    if ($dependentsTab.length) {
      $dependentsTab.on("shown.bs.tab", fetchAndDisplayDependents);
    }
  }

  // Check if we're on the profile page and initialize
  if (window.location.pathname === "/profile") {
    initDependentsTab();
    // Fetch dependents immediately if we're on the profile page
    fetchAndDisplayDependents();
  }
});
