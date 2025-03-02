document.getElementById("signup-form").addEventListener("submit", function (event) {
    event.preventDefault();

    let username = document.querySelector("input[name='username']").value;
    let email = document.querySelector("input[name='email']").value;
    let password = document.querySelector("input[name='password']").value;
    let confirmPassword = document.querySelector("input[name='confirm-password']").value;
    let csrfToken = document.querySelector("input[name='csrfmiddlewaretoken']").value;

    if (password !== confirmPassword) {
        alert("Passwords do not match!");
        return;
    }

    fetch("/auth/signup/", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": csrfToken
        },
        body: `username=${username}&email=${email}&password=${password}`
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                alert("Signup successful! Redirecting to login...");
                window.location.href = "/auth/login/"; // ✅ Redirects to login page
            }
        })
        .catch(error => console.error("Error:", error));
});
