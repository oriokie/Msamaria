$(document).ready(function () {
  // Function to handle creating a new case
  $("#createCaseBtn").click(function () {
    var member_id = $("#memberSelect").val();
    var dependent_id = $("#dependentSelect").val();
    var member_deceased = $("#memberDeceasedCheckbox").prop("checked");
    var case_amount = $("#caseAmountInput").val();

    // If dependent_id is not null, fetch the respective member_id from the backend
    if (dependent_id) {
      $.ajax({
        type: "POST",
        url: "/cases/get-member-id",
        data: {
          dependent_id: dependent_id,
        },
        success: function (response) {
          member_id = response.member_id;
          console.log("Member ID:", member_id);
          console.log("Dependent ID:", dependent_id);
          console.log("Member Deceased:", member_deceased);
          console.log("Case Amount:", case_amount);
          // Make the AJAX call to create the case
          createCase(member_id, dependent_id, member_deceased, case_amount);
        },
        error: function (xhr, status, error) {
          console.error("Failed to retrieve member ID:", error);
          alert("Failed to create case. Please try again later.");
        },
      });
    } else {
      console.log("Member ID:", member_id);
      console.log("Dependent ID:", dependent_id);
      console.log("Member Deceased:", member_deceased);
      console.log("Case Amount:", case_amount);
      // Make the AJAX call to create the case
      createCase(member_id, dependent_id, member_deceased, case_amount);
    }
  });

  // Function to create the case
  function createCase(member_id, dependent_id, member_deceased, case_amount) {
    $.ajax({
      type: "POST",
      url: "/cases/create",
      data: {
        member_id: member_id,
        dependent_id: dependent_id,
        member_deceased: member_deceased,
        case_amount: case_amount,
      },
      success: function (response) {
        alert("Case created successfully.");
        location.reload(); // Reload the page to update case information
      },
      error: function (xhr, status, error) {
        console.error("Failed to create case:", error);
        alert("Failed to create case. Please try again later.");
      },
    });
  }

  // Function to update member select options based on selected dependent
  $("#dependentSelect").change(function () {
    var dependent_id = $(this).val();
    if (dependent_id) {
      $.ajax({
        type: "POST",
        url: "/cases/get-member-id",
        data: {
          dependent_id: dependent_id,
        },
        success: function (response) {
          var member_id = response.member_id;
          console.log("Selected Member ID:", member_id);
          // Set the selected member in the member select dropdown
          $("#memberSelect").val(member_id);
        },
        error: function (xhr, status, error) {
          console.error("Failed to retrieve member ID:", error);
          alert("Failed to retrieve member ID. Please try again later.");
        },
      });
    }
  });
});
