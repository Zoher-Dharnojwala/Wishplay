document.addEventListener("DOMContentLoaded", () => {
    loadHistory();
});

async function loadHistory() {
    const historyBox = document.getElementById("historyBox");
    const searchInput = document.getElementById("searchInput");

    // GET current logged in user
    const userId = localStorage.getItem("user_id");  
    if (!userId) return;

    const res = await fetch(`http://127.0.0.1:8000/history/list?user_id=${userId}`);
    const data = await res.json();

    if (data.status !== "success") {
        historyBox.innerHTML = "Failed to load history.";
        return;
    }

    if (data.history.length === 0) {
        historyBox.innerHTML = "No saved conversations yet.";
        return;
    }

    historyBox.innerHTML = "";

    data.history.forEach(item => {
        const div = document.createElement("div");
        div.className = "history-item";

        div.innerHTML = `
            <div class="history-header">
                <b>${item.category}</b>
                <span>${new Date(item.created_at).toLocaleString()}</span>
            </div>
            <div class="history-text">${item.answer_text}</div>
        `;

        historyBox.appendChild(div);
    });
}
