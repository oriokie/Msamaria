function markContributionPaid(memberId, caseId) {
  fetch("/contributions/mark_contribution_paid", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCSRFToken(),
    },
    body: JSON.stringify({ member_id: memberId, case_id: caseId }),
  })
    .then((response) => {
      console.log("Response received:", response);
      if (response.ok) {
        console.log("Contribution marked as paid successfully");
        location.reload(); // Reload the page after successful marking
      } else {
        console.error("Failed to mark contribution as paid");
      }
    })
    .catch((error) => {
      console.error("Error marking contribution as paid:", error);
    });
}

function undoContribution(memberId, caseId) {
  fetch("/contributions/undo_contribution", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCSRFToken(),
    },
    body: JSON.stringify({ member_id: memberId, case_id: caseId }),
  })
    .then((response) => {
      console.log("Response received:", response);
      if (response.ok) {
        console.log("Contribution payment undone successfully");
        location.reload(); // Reload the page after successful undoing
      } else {
        console.error("Failed to undo contribution");
      }
    })
    .catch((error) => {
      console.error("Error undoing contribution:", error);
    });
}

function getCSRFToken() {
  const token = document.querySelector('meta[name="csrf-token"]');
  return token ? token.content : "";
}
