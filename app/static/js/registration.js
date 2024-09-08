document.addEventListener("DOMContentLoaded", function () {
  const dependentsContainer = document.getElementById("dependentsContainer");
  const addDependentBtn = document.getElementById("addDependentBtn");
  const form = document.getElementById("memberForm");
  let dependentCount = 0;

  function addDependentField() {
    const template = document.getElementById("dependentTemplate");
    const dependentCard = template.content.cloneNode(true);

    dependentCard.querySelector(".removeDependent").addEventListener("click", function () {
      this.closest(".dependent-card").remove();
    });

    dependentsContainer.appendChild(dependentCard);
    dependentCount++;
  }

  addDependentBtn.addEventListener("click", addDependentField);

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    const formData = new FormData(form);
    const memberData = Object.fromEntries(formData);

    // Gather dependent data
    const dependents = [];
    document.querySelectorAll(".dependent-card").forEach((card) => {
      dependents.push({
        name: card.querySelector('[name="dependent_name"]').value,
        phone_number: card.querySelector('[name="dependent_phone_number"]').value,
        relationship: card.querySelector('[name="dependent_relationship"]').value,
      });
    });

    // Add dependents to the data object
    memberData.dependents = dependents;

    fetch("/regnew", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": formData.get("csrf_token"),
      },
      body: JSON.stringify(memberData),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          alert("Registration successful!");
          form.reset();
          dependentsContainer.innerHTML = "";
          dependentCount = 0;
        } else {
          alert("Registration failed: " + data.message);
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        alert("An error occurred. Please try again.");
      });
  });
});
