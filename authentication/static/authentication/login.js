document.getElementById("login-form").addEventListener("submit", function (event) {
    event.preventDefault();

    let username = document.querySelector("input[name='username']").value;
    let password = document.querySelector("input[name='password']").value;
    let csrfToken = document.querySelector("input[name='csrfmiddlewaretoken']").value; // ✅ Get CSRF token

    fetch("/auth/login/", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": csrfToken  // ✅ Include CSRF Token
        },
        body: `username=${username}&password=${password}`
    })
        .then(response => {
            if (response.redirected) {
                window.location.href = response.url; // ✅ Redirect to home on success
            } else {
                return response.json();
            }
        })
        .then(data => {
            if (data && data.error) {
                alert(data.error);
            }
        })
        .catch(error => console.error("Error:", error));
});
