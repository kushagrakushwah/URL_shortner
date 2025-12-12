const API_BASE = "https://stlk.up.railway.app";

const btn = document.getElementById("shortenBtn");
const input = document.getElementById("urlInput");
const resultBox = document.getElementById("resultBox");

btn.addEventListener("click", async () => {
  const longUrl = input.value.trim();

  if (!longUrl) {
    resultBox.innerHTML = "<span style='color:red;'>Please enter a URL</span>";
    return;
  }

  resultBox.innerHTML = "⏳ Shortening URL...";

  try {
    const res = await fetch(`${API_BASE}/shorten`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: longUrl }),
    });

    const data = await res.json();

    if (data.short_url) {
      resultBox.innerHTML = `
        <strong>Short URL:</strong><br>
        <a href="${data.short_url}" target="_blank">${data.short_url}</a>
      `;
    } else {
      resultBox.innerHTML = "<span style='color:red;'>Error shortening URL</span>";
    }
  } catch (err) {
    resultBox.innerHTML = "<span style='color:red;'>❌ Backend unreachable</span>";
  }
});
