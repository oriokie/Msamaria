$(document).ready(function () {
  // Function to display member details
  function displayMemberDetails(member) {
    var memberDetailsHtml = `
            <table class="table table-striped table-bordered">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>ID</th>
                        <th>ID Number</th>
                        <th>Phone Number</th>
                        <th>Registration Fee Paid</th>
                        <th>Admin Status</th>
                        <th>Active</th>
                        <th>Deceased</th>
                        <th>Created At</th>
                        <th>Updated At</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><input type="text" name="name" value="${member.name}" readonly></td>
                        <td>${member.id}</td>
                        <td><input type="text" name="id_number" value="${member.id_number}" readonly></td>
                        <td><input type="text" name="phone_number" value="${member.phone_number}" readonly></td>
                        <td><input type="checkbox" name="reg_fee_paid" ${member.reg_fee_paid ? "checked" : ""} disabled></td>
                        <td><input type="checkbox" name="is_admin" ${member.is_admin ? "checked" : ""} disabled></td>
                        <td><input type="checkbox" name="active" ${member.active ? "checked" : ""} disabled></td>
                        <td><input type="checkbox" name="is_deceased" ${member.is_deceased ? "checked" : ""} disabled></td>
                        <td>${member.created_at}</td>
                        <td>${member.updated_at}</td>
                    </tr>
                </tbody>
            </table>
            <button class="btn btn-primary" id="editMember">Edit</button>
            <button class="btn btn-success" id="submitEdit">Submit</button>
        `;
    $("#memberDetails").html(memberDetailsHtml);

    // Handle click on edit button
    $(document).on("click", "#editMember", function () {
      // Enable input fields for editing
      $("table input").prop("readonly", false).prop("disabled", false);
      showAlert("You are now editing the member details.", "info");
    });

    // Handle click on submit button
    $("#submitEdit").click(function () {
      // Get updated values
      var updatedMember = {
        id: member.id,
        name: $("table input[name='name']").val(),
        id_number: $("table input[name='id_number']").val(),
        phone_number: $("table input[name='phone_number']").val(),
        reg_fee_paid: $("table input[name='reg_fee_paid']").prop("checked"),
        is_admin: $("table input[name='is_admin']").prop("checked"),
        active: $("table input[name='active']").prop("checked"),
        is_deceased: $("table input[name='is_deceased']").prop("checked"),
        created_at: member.created_at,
        updated_at: member.updated_at,
      };

      // Fetch updated dependents data from the HTML
      var updatedDependents = [];
      $("table tbody tr").each(function () {
        var dependentId = $(this).find("input[name='dependent_ids[]']").val();
        var dependentName = $(this).find("input[name='dependent_names[]']").val();
        var dependentRelationship = $(this).find("input[name='dependent_relationships[]']").val();
        if (dependentId) {
          // Skip empty rows
          console.log("Dependent ID:", dependentId);
          console.log("Dependent Name:", dependentName);
          console.log("Dependent Relationship:", dependentRelationship);

          // Include updated dependents data in the member object
          updatedDependents.push({
            id: dependentId,
            name: dependentName,
            relationship: dependentRelationship,
          });
        }
      });

      // Include updated dependents data in the member object
      updatedMember.dependents = updatedDependents;

      // Send updated member details to the server for updating in the database
      $.ajax({
        type: "POST",
        url: `/admin/update_member/${member.id}`,
        contentType: "application/json", // Set the content type to JSON
        data: JSON.stringify(updatedMember), // Convert data to JSON format
        success: function (data) {
          // Display success message or handle as needed
          showAlert("Member details updated successfully.", "success");
          console.log("Member details updated successfully.");
        },
        error: function (xhr, status, error) {
          showAlert("Failed to update member details.", "danger");
          console.error("Failed to update member details:", error);
          // Handle error or display error message as needed
        },
      });
    });
  }

  // Function to display dependents in a table
  function displayDependents(dependents) {
    var dependentTableHtml = `
            <table class="table table-striped table-bordered">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Relationship</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>`;
    dependents.forEach(function (dependent) {
      dependentTableHtml += `
                    <tr>
                        <td><input type="text" name="dependent_ids[]" value="${dependent.id}" readonly></td>
                        <td><input type="text" name="dependent_names[]" value="${dependent.name}" readonly></td>
                        <td><input type="text" name="dependent_relationships[]" value="${dependent.relationship}" readonly></td>
                        <td>
                            <button class="btn btn-danger delete-dependent" data-dependent-id="${dependent.id}">Delete</button>
                        </td>
                    </tr>`;
    });
    dependentTableHtml += `
                </tbody>
            </table>`;
    $("#dependentTable").html(dependentTableHtml);
  }

  // Function to handle member search
  $("#searchInput").on("input", function () {
    var query = $(this).val();
    $.ajax({
      type: "POST",
      url: "/admin/search_member",
      data: { search_query: query },
      success: function (data) {
        var resultsHtml = "";
        if (data.error) {
          resultsHtml = '<div class="alert alert-danger">' + data.error + "</div>";
        } else {
          data.forEach(function (member) {
            resultsHtml += '<div class="member-result" data-member-id="' + member.id + '">' + member.name + "</div>";
          });
        }
        $("#searchResults").html(resultsHtml);
      },
      error: function (xhr, status, error) {
        console.error("Failed to fetch members:", error);
        $("#searchResults").html('<div class="alert alert-danger">Failed to fetch members: ' + error + "</div>");
      },
    });
  });

  // Function to handle click on member result
  $(document).on("click", ".member-result", function () {
    var memberId = $(this).data("member-id");
    $.ajax({
      type: "GET",
      url: `/admin/member_details/${memberId}`,
      success: function (data) {
        console.log("Member data:", data);
        displayMemberDetails(data);
        displayDependents(data.dependents); // Display dependents for the selected member
      },
      error: function (xhr, status, error) {
        showAlert("Failed to fetch member details.", "danger");
        console.error("Failed to fetch member details:", error);
        $("#memberDetails").html('<div class="alert alert-danger">Failed to fetch member details</div>');
      },
    });
  });

  // Function to display flash messages dynamically
  function showAlert(message, type) {
    var alertClass = type === "success" ? "alert-success" : "alert-danger";
    var alertHtml = `<div class="alert ${alertClass}" role="alert">${message}</div>`;
    $("#flashMessages").html(alertHtml);
  }

  // Handle click on delete button for dependents
  $(document).on("click", ".delete-dependent", function () {
    var dependentId = $(this).data("dependent-id");
    $.ajax({
      type: "DELETE",
      url: `/admin/delete_dependent/${dependentId}`,
      success: function () {
        // Remove the corresponding HTML element from the DOM
        $(`#dependent-${dependentId}`).remove();
        showAlert("Dependent deleted successfully.", "success");
        console.log("Dependent deleted successfully.");
      },
      error: function (xhr, status, error) {
        showAlert("Failed to delete dependent.", "danger");
        console.error("Failed to delete dependent:", error);
        // Handle error or display error message as needed
      },
    });
  });

  // Function to handle updating dependents
  function updateDependents(memberId, updatedDependents) {
    $.ajax({
      type: "POST",
      url: `/admin/update_dependents/${memberId}`,
      contentType: "application/json",
      data: JSON.stringify(updatedDependents), // Send updated dependents directly
      success: function (response) {
        console.log("Dependents updated successfully");
        // Handle success as needed
      },
      error: function (xhr, status, error) {
        console.error("Failed to update dependents:", error);
        // Handle error or display error message as needed
      },
    });
  }
});
