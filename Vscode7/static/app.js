document.addEventListener("DOMContentLoaded", function () {
    // Show current date and time
    const now = new Date();
    document.getElementById("datetime").textContent = "Current time: " + now.toLocaleString();

    // Dark mode toggle
    const toggleBtn = document.getElementById("darkToggle");
    toggleBtn.addEventListener("click", () => {
        document.body.classList.toggle("dark-mode");
    });

    // Form validation (for login/signup pages)
    const forms = document.querySelectorAll("form");
    forms.forEach(form => {
        form.addEventListener("submit", function (e) {
            const inputs = form.querySelectorAll("input");
            let empty = false;
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    empty = true;
                }
            });
            if (empty) {
                e.preventDefault();
                alert("Please fill in all fields.");
            }
        });
    });
});
// static/app.js - JavaScript for user authentication application
// This file contains the client-side logic for handling dark mode and form validation.