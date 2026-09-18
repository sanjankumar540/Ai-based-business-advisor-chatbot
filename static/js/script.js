// script.js
// Small shared front-end behaviors for the AI Business Assistant

document.addEventListener("DOMContentLoaded", function () {
  // Auto-dismiss alerts after 5 seconds
  document.querySelectorAll(".alert").forEach(function (alertEl) {
    setTimeout(function () {
      var bsAlert = bootstrap.Alert.getOrCreateInstance(alertEl);
      if (bsAlert) bsAlert.close();
    }, 5000);
  });
});
