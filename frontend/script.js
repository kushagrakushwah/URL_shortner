const btn = document.getElementById("shortenBtn");
const input = document.getElementById("urlInput");
const resultBox = document.getElementById("resultBox");

// IMPORTANT: change this ONLY if backend is NOT on localhost
const API_URL = "http://127.0.0.1:8000/shorten";

btn.addEventListener("click", async () => {
    const longUrl = input.value.trim();

    if (!longUrl) {
        resultBox.innerHTML = "<span style='color:red;'>Please enter a URL</span>";
        return;
    }

    resultBox.innerHTML = "⏳ Shortening... please wait";

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ url: longUrl })
        });

        if (!response.ok) throw new Error("Server error");

        const data = await response.json();

        // DISPLAY SHORT URL AND KEEP IT PERMANENT
        resultBox.innerHTML = `
            ✔ Short URL:<br><br>
            <a href="${data.short_url}" target="_blank">${data.short_url}</a>
        `;
    }
    catch (err) {
        resultBox.innerHTML = "<span style='color:red;'>❌ Backend not running or fetch failed!</span>";
    }
});
