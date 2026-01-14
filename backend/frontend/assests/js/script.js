const API_BASE = "http://127.0.0.1:8000/conversation";
const conversationBox = document.getElementById("conversationBox");
const startBtn = document.getElementById("startBtn");
const statusEl = document.getElementById("status");

function addMessage(sender, text, cls = "") {
  const msg = document.createElement("p");
  msg.className = `message ${cls}`;
  msg.innerHTML = `<b>${sender}:</b> ${text}`;
  conversationBox.appendChild(msg);
  conversationBox.scrollTop = conversationBox.scrollHeight;
}

/**
 * ✅ Robust audio player
 * Handles autoplay restrictions and delayed playback
 */
async function playQuestionAudio(audioBase64) {
  if (!audioBase64) {
    console.warn("⚠️ No audio provided");
    return;
  }

  const audio = new Audio(`data:audio/mp3;base64,${audioBase64}`);
  audio.crossOrigin = "anonymous";

  try {
    await audio.play();
    console.log("🔊 Playing AI voice...");
  } catch (err) {
    console.warn("⚠️ Autoplay blocked:", err);
    // Wait for user interaction to play audio
    document.body.addEventListener(
      "click",
      () => audio.play().catch(console.error),
      { once: true }
    );
  }

  // Wait for the audio to end before enabling mic again
  return new Promise((resolve) => {
    audio.onended = () => {
      console.log("🎧 Audio finished");
      resolve();
    };
  });
}

/**
 * Starts a new conversation category
 */
async function startConversation() {
  statusEl.textContent = "Connecting...";
  addMessage("System", "Starting conversation...");

  try {
    const category = document.getElementById("categorySelect").value;
    const res = await fetch(`${API_BASE}/start?patient_id=P001&category=${selectCategory}`);

    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    if (data.first_question_text) {
      addMessage("AI Afi", data.first_question_text, "ai");
      statusEl.textContent = "Speaking";

      // Play the AI question audio, then wait before continuing
      await playQuestionAudio(data.first_question_audio);

      statusEl.textContent = "Listening...";
    } else {
      addMessage("System", "⚠️ No question returned.");
      statusEl.textContent = "Idle";
    }
  } catch (err) {
    console.error("❌ Conversation start failed:", err);
    addMessage("System", `Error: ${err.message}`, "error");
    statusEl.textContent = "Error";
  }
}

// Event listener for button click
startBtn.addEventListener("click", startConversation);
