document.addEventListener("DOMContentLoaded", function () {
  const dependentsContainer = document.getElementById("dependentsContainer");
  const addDependentBtn = document.getElementById("addDependentBtn");
  const form = document.getElementById("memberForm");
  let dependentCount = 0;

  // Function to add a new dependent field
  function addDependentField() {
    const template = document.getElementById("dependentTemplate");
    const dependentCard = template.content.cloneNode(true);

    // Add event listener to remove button in each dependent card
    dependentCard.querySelector(".removeDependent").addEventListener("click", function () {
      this.closest(".mt-6").remove(); // Adjusted class to match the outer div containing the dependent card
    });

    // Append the new dependent card to the container
    dependentsContainer.appendChild(dependentCard);
    dependentCount++;
  }

  // Add event listener to the "Add Dependent" button
  addDependentBtn.addEventListener("click", addDependentField);

  // Handle form submission
  form.addEventListener("submit", function (e) {
    e.preventDefault(); // Prevent default form submission behavior
    console.log("Form submission intercepted!"); // Debugging step

    // Gather form data
    const formData = new FormData(form); // Gather form data
    const memberData = Object.fromEntries(formData); // Convert form data to an object
    console.log("Form Data:", memberData); // Debugging step

    // Gather data for all dependents
    const dependents = [];
    document.querySelectorAll(".mt-6").forEach((card) => {
      const nameInput = card.querySelector('[name="dependent_name"]');
      const phoneInput = card.querySelector('[name="dependent_phone_number"]');
      const relationshipInput = card.querySelector('[name="dependent_relationship"]');

      if (nameInput && phoneInput && relationshipInput) {
        dependents.push({
          name: nameInput.value,
          phone_number: phoneInput.value,
          relationship: relationshipInput.value,
        });
      } else {
        console.error("Missing dependent fields in card.");
      }
    });

    // Add dependents to the data object, defaulting to an empty array if none
    memberData.dependents = dependents.length > 0 ? dependents : [];

    console.log("Complete Form Data (with dependents):", memberData); // Debugging step

    // Make a POST request to the server with the form and dependent data
    fetch("/regnew", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": formData.get("csrf_token"), // Ensure CSRF token is included
      },
      body: JSON.stringify(memberData),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("Server Response:", data); // Debugging step
        if (data.success) {
          alert("Registration successful!"); // Display success message
          form.reset(); // Reset form
          dependentsContainer.innerHTML = ""; // Clear dependents
          dependentCount = 0;
        } else {
          alert("Registration failed: " + data.message); // Display error message
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        alert("An error occurred. Please try again."); // Handle any errors
      });
  });
});
