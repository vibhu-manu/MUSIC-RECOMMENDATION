const sessionId = crypto.randomUUID();
const userId = localStorage.getItem("mood_music_user_id") || crypto.randomUUID();
localStorage.setItem("mood_music_user_id", userId);

const statusEl = document.querySelector("#status");
const webcam = document.querySelector("#webcam");
const canvas = document.querySelector("#snapshot");
const captureBtn = document.querySelector("#captureBtn");
const refreshBtn = document.querySelector("#refreshBtn");
const emotionGrid = document.querySelector("#emotionGrid");
const providerStatus = document.querySelector("#providerStatus");
const songList = document.querySelector("#songList");
const emotionTitle = document.querySelector("#emotionTitle");
const moodControls = document.querySelector("#moodControls");
const languageSelect = document.querySelector("#languageSelect");

let lastProbabilities = null;
let lastRecommendationId = null;

const emotions = ["happy", "sad", "angry", "fear", "surprise", "disgust", "love"];

function setStatus(message) {
  statusEl.textContent = message;
}

function renderEmotion(probabilities = {}) {
  emotionGrid.innerHTML = emotions
    .map((emotion) => {
      const value = probabilities[emotion] || 0;
      return `
        <div class="emotion-row">
          <strong>${emotion}</strong>
          <div class="bar"><span style="width:${Math.round(value * 100)}%"></span></div>
          <span>${Math.round(value * 100)}%</span>
        </div>
      `;
    })
    .join("");
}

function renderMoodControls() {
  moodControls.innerHTML = emotions
    .map((emotion) => `<button data-mood="${emotion}" title="Test ${emotion} recommendations">${emotion}</button>`)
    .join("");
}

function renderSongs(songs = []) {
  if (!songs.length) {
    songList.innerHTML = '<div class="empty">Capture a mood to generate recommendations.</div>';
    return;
  }

  songList.innerHTML = songs
    .map(
      (song, index) => `
        <article class="song-card">
          <div class="song-main">
            <div>
              <div class="song-title">${index + 1}. ${song.track_name}</div>
              <div class="song-meta">${song.artist_name} · ${song.genre} · ${song.language.toUpperCase()} · ${Math.round(song.tempo)} BPM</div>
            </div>
            <div class="score-container" style="text-align: right;">
              <div class="score" style="font-size: 18px; color: var(--accent); font-weight: 800;">${Math.round(song.mood_match_score)}% Match</div>
              <div class="rank-score" style="font-size: 12px; color: var(--muted); font-variant-numeric: tabular-nums; font-weight: 500;">Score: ${song.rank_score.toFixed(2)}</div>
            </div>
          </div>
          <div class="reason-list">
            ${song.reasons.map((reason) => `<span class="reason">${reason}</span>`).join("")}
          </div>
          <div class="actions">
            <button class="like" data-action="like" data-song-id="${song.song_id}">Like</button>
            <button data-action="skip" data-song-id="${song.song_id}">Skip</button>
            <button class="dislike" data-action="dislike" data-song-id="${song.song_id}">Dislike</button>
          </div>
        </article>
      `
    )
    .join("");
}

async function api(path, payload) {
  const response = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}

async function initCamera() {
  renderEmotion();
  renderSongs();
  renderMoodControls();
  try {
    const health = await fetch("/api/health").then((response) => response.json());
    providerStatus.textContent = health.active_emotion_provider === "deepface"
      ? "Model: DeepFace pretrained emotion detector"
      : `Model: ${health.active_emotion_provider} fallback${health.emotion_provider_error ? ` (${health.emotion_provider_error})` : ""}`;
  } catch (error) {
    providerStatus.textContent = "Model status unavailable";
  }
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
    webcam.srcObject = stream;
    setStatus("Camera ready. Capture a mood when you are ready.");
  } catch (error) {
    setStatus("Camera unavailable. Demo mode will still work.");
  }
}

function captureFrame() {
  const context = canvas.getContext("2d");
  context.drawImage(webcam, 0, 0, canvas.width, canvas.height);
  return canvas.toDataURL("image/jpeg", 0.75);
}

async function detectAndRecommend() {
  captureBtn.disabled = true;
  refreshBtn.disabled = true;
  try {
    setStatus("Detecting facial emotion...");
    const imageBase64 = webcam.srcObject ? captureFrame() : null;
    const emotion = await api("/api/emotion", {
      user_id: userId,
      session_id: sessionId,
      image_base64: imageBase64,
      reset_smoothing: true,
    });
    providerStatus.textContent = emotion.provider === "deepface"
      ? "Model: DeepFace pretrained emotion detector"
      : `Model: ${emotion.provider} fallback${emotion.provider_error ? ` (${emotion.provider_error})` : ""}`;
    lastProbabilities = emotion.smoothed_probabilities;
    renderEmotion(lastProbabilities);
    emotionTitle.textContent = `${emotion.emotion} recommendations`;
    setStatus("Ranking songs with mood, popularity, diversity, novelty, and feedback.");
    const recommendations = await api("/api/recommendations", {
      user_id: userId,
      session_id: sessionId,
      probabilities: lastProbabilities,
      limit: 15,
      language: languageSelect.value,
    });
    lastRecommendationId = recommendations.recommendation_id;
    renderSongs(recommendations.recommendations);
    setStatus("Recommendations ready. Feedback updates your user embedding.");
  } catch (error) {
    setStatus(`Error: ${error.message}`);
  } finally {
    captureBtn.disabled = false;
    refreshBtn.disabled = false;
  }
}

async function recommendForMood(mood) {
  const probabilities = {};
  let total = 0;
  emotions.forEach((emotion) => {
    const val = emotion === mood ? 0.7 + Math.random() * 0.3 : Math.random() * 0.2;
    probabilities[emotion] = val;
    total += val;
  });
  Object.keys(probabilities).forEach(emotion => probabilities[emotion] /= total);
  
  lastProbabilities = probabilities;
  renderEmotion(probabilities);
  emotionTitle.textContent = `${mood} recommendations`;
  setStatus(`Showing ${mood} recommendation profile.`);
  const recommendations = await api("/api/recommendations", {
    user_id: userId,
    session_id: sessionId,
    probabilities,
    limit: 15,
    language: languageSelect.value,
  });
  lastRecommendationId = recommendations.recommendation_id;
  renderSongs(recommendations.recommendations);
}

async function sendFeedback(action, songId, button) {
  if (!lastRecommendationId) return;
  button.disabled = true;
  try {
    await api("/api/feedback", {
      user_id: userId,
      session_id: sessionId,
      recommendation_id: lastRecommendationId,
      song_id: songId,
      action,
    });
    button.textContent = "Saved";
    if (lastProbabilities) {
      const recommendations = await api("/api/recommendations", {
        user_id: userId,
        session_id: sessionId,
        probabilities: lastProbabilities,
        limit: 10,
        language: languageSelect.value,
      });
      lastRecommendationId = recommendations.recommendation_id;
      renderSongs(recommendations.recommendations);
    }
  } catch (error) {
    setStatus(`Feedback error: ${error.message}`);
    button.disabled = false;
  }
}

captureBtn.addEventListener("click", detectAndRecommend);
refreshBtn.addEventListener("click", () => {
  if (lastProbabilities) {
    detectAndRecommend();
  }
});
songList.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button) return;
  sendFeedback(button.dataset.action, button.dataset.songId, button);
});
moodControls.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-mood]");
  if (!button) return;
  recommendForMood(button.dataset.mood);
});
languageSelect.addEventListener("change", async () => {
  if (lastProbabilities) {
    setStatus("Updating recommendations for new language...");
    const recommendations = await api("/api/recommendations", {
      user_id: userId,
      session_id: sessionId,
      probabilities: lastProbabilities,
      limit: 10,
      language: languageSelect.value,
    });
    lastRecommendationId = recommendations.recommendation_id;
    renderSongs(recommendations.recommendations);
    setStatus("Recommendations updated.");
  }
});

initCamera();
