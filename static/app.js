const apiBase = "/api";

const readingDateInput = document.getElementById("reading-date");
const readingPlanSelect = document.getElementById("reading-plan");
const bibleVersionSelect = document.getElementById("bible-version");
const readingContent = document.getElementById("reading-content");
const commentaryBox = document.getElementById("commentary");
const questionHelper = document.getElementById("question-helper");
const questionText = document.getElementById("question-text");
const answerBox = document.getElementById("answer");
const personalNotes = document.getElementById("personal-notes");
const marginNotes = document.getElementById("margin-notes");
const aiInsights = document.getElementById("ai-insights");
const saveStatus = document.getElementById("save-status");
const progressBox = document.getElementById("progress");

// Use local date, not UTC (toISOString uses UTC which can be wrong day)
const today = new Date();
const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
readingDateInput.value = todayStr;

async function fetchReading() {
  const date = readingDateInput.value;
  const planType = readingPlanSelect.value || "classic";
  const version = bibleVersionSelect.value;
  const response = await fetch(`${apiBase}/readings/${date}?version=${encodeURIComponent(version)}&plan_type=${encodeURIComponent(planType)}`);
  if (!response.ok) {
    readingContent.textContent = "Reading not found.";
    return;
  }
  const data = await response.json();
  const passages = data.passages
    .map((p) => {
      const passageText = data.passage_text?.[p];
      if (passageText && passageText.verses) {
        const verses = Object.entries(passageText.verses)
          .map(([verse, text]) => `<div><strong>${verse}</strong> ${text}</div>`)
          .join("");
        return `<li><strong>${p}</strong><div class="verse-block">${verses}</div></li>`;
      }
      return `<li>${p} <em>(text not loaded)</em></li>`;
    })
    .join("");
  readingContent.innerHTML = `<strong>${data.theme || "Daily Bread"}</strong><ul>${passages}</ul>`;
  
  // If this is a commentary plan and commentaries are included, display them
  if ((planType === "augustine_classic" || planType === "aquinas_classic") && data.commentaries) {
    const helperName = planType === "augustine_classic" ? "Saint Augustine" : "Saint Thomas Aquinas";
    const helperShort = planType === "augustine_classic" ? "Augustine" : "Aquinas";
    
    const commentaries = Object.entries(data.commentaries)
      .map(([passage, commentary]) => {
        if (commentary && commentary.trim()) {
          return `<div class="commentary-section"><h4>${helperShort} on ${passage}</h4><pre class="commentary-text">${commentary}</pre></div>`;
        }
        return "";
      })
      .filter(c => c)
      .join("");
    
    if (commentaries) {
      commentaryBox.innerHTML = `<h3>${helperName}'s Commentary</h3>${commentaries}`;
    } else {
      commentaryBox.textContent = "Commentaries are being generated. Use the 'Request Commentary' button for on-demand commentary.";
    }
  } else {
    // Clear commentary box for other plans
    commentaryBox.textContent = "";
  }
  
  await loadDiary(date, data.passages.join("; "));
  await loadProgress();
}

async function requestCommentary(helper) {
  commentaryBox.textContent = "Loading commentary... (this may take 1-2 minutes)";
  try {
    const date = readingDateInput.value;
    const planType = readingPlanSelect.value || "classic";
    const version = bibleVersionSelect.value;
    const readingResponse = await fetch(`${apiBase}/readings/${date}?version=${encodeURIComponent(version)}&plan_type=${encodeURIComponent(planType)}`);
    if (!readingResponse.ok) {
      commentaryBox.textContent = "Error: Could not load reading.";
      return;
    }
    const reading = await readingResponse.json();
    const response = await fetch(`${apiBase}/commentary`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        passage: reading.passages.join("; "),
        helper: helper,
        personalized: true,
      }),
      signal: AbortSignal.timeout(360000), // 6 minutes timeout
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({ commentary: "Request failed" }));
      commentaryBox.textContent = `Error: ${error.commentary || "Failed to get commentary. Is Ollama running?"}`;
      return;
    }
    const data = await response.json();
    commentaryBox.textContent = data.commentary || "No commentary available.";
  } catch (error) {
    commentaryBox.textContent = `Error: ${error.message || "Failed to get commentary. Make sure Ollama is running."}`;
  }
}

async function askQuestion() {
  const question = questionText.value.trim();
  if (!question) return;
  const response = await fetch(`${apiBase}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      question: question,
      helper: questionHelper.value,
    }),
  });
  const data = await response.json();
  answerBox.textContent = data.answer || "No answer available.";
}

async function saveDiary() {
  const date = readingDateInput.value;
  const planType = readingPlanSelect.value || "classic";
  const version = bibleVersionSelect.value;
  const readingResponse = await fetch(`${apiBase}/readings/${date}?version=${encodeURIComponent(version)}&plan_type=${encodeURIComponent(planType)}`);
  if (!readingResponse.ok) return;
  const reading = await readingResponse.json();

  const notes = marginNotes.value
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);

  const response = await fetch(`${apiBase}/diary`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      entry_date: date,
      reading_passage: reading.passages.join("; "),
      personal_notes: personalNotes.value,
      margin_notes: { notes },
      ai_insights: aiInsights.value,
    }),
  });

  if (response.ok) {
    saveStatus.textContent = "Saved!";
    setTimeout(() => (saveStatus.textContent = ""), 2000);
    await loadProgress();
  } else {
    saveStatus.textContent = "Save failed.";
  }
}

async function loadDiary(date, readingPassage) {
  const response = await fetch(`${apiBase}/diary/${date}`);
  if (!response.ok) return;
  const data = await response.json();
  if (!data.exists) {
    personalNotes.value = "";
    marginNotes.value = "";
    aiInsights.value = "";
    return;
  }
  personalNotes.value = data.personal_notes || "";
  aiInsights.value = data.ai_insights || "";
  const notes = data.margin_notes?.notes || [];
  marginNotes.value = notes.join("\n");
}

async function loadProgress() {
  const response = await fetch(`${apiBase}/progress`);
  if (!response.ok) return;
  const data = await response.json();
  const streakText = data.reading_streak ? ` | 🔥 Streak: ${data.reading_streak} days` : "";
  progressBox.textContent = `${data.completed_readings} / ${data.total_readings} days (${data.completion_percentage}%)${streakText}`;
}

async function loadVersions() {
  const response = await fetch(`${apiBase}/bible/versions`);
  if (!response.ok) return;
  const data = await response.json();
  bibleVersionSelect.innerHTML = "";
  data.versions.forEach((version) => {
    const option = document.createElement("option");
    option.value = version.id;
    option.textContent = `${version.id} - ${version.title}`;
    bibleVersionSelect.appendChild(option);
  });
  if (data.default_version) {
    bibleVersionSelect.value = data.default_version;
  }
}

async function loadReadingPlans() {
  const response = await fetch(`${apiBase}/reading-plans`);
  if (!response.ok) return;
  const data = await response.json();
  readingPlanSelect.innerHTML = "";
  data.plans.forEach((plan) => {
    const option = document.createElement("option");
    option.value = plan.id;
    option.textContent = plan.name;
    option.title = plan.description;
    readingPlanSelect.appendChild(option);
  });
  if (data.default) {
    readingPlanSelect.value = data.default;
  }
}

// Navigation functions
function navigateDay(offset) {
  const currentDate = new Date(readingDateInput.value + "T00:00:00");
  currentDate.setDate(currentDate.getDate() + offset);
  const newDate = currentDate.toISOString().split("T")[0];
  readingDateInput.value = newDate;
  fetchReading();
}

// Auto-save diary with debouncing
let saveTimeout = null;
function debouncedAutoSave() {
  clearTimeout(saveTimeout);
  saveTimeout = setTimeout(() => {
    saveDiary().catch(() => {
      // Silently fail for auto-save
    });
  }, 2000); // Save 2 seconds after last keystroke
}

// Export diary
async function exportDiary() {
  try {
    const response = await fetch(`${apiBase}/diary/export`);
    if (!response.ok) {
      alert("Failed to export diary. Please try again.");
      return;
    }
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `bible-diary-${new Date().toISOString().split("T")[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    saveStatus.textContent = "Exported!";
    setTimeout(() => (saveStatus.textContent = ""), 2000);
  } catch (error) {
    alert("Export failed: " + error.message);
  }
}

// Dark mode toggle
function toggleDarkMode() {
  document.body.classList.toggle("dark-mode");
  const isDark = document.body.classList.contains("dark-mode");
  localStorage.setItem("darkMode", isDark);
  const toggleBtn = document.getElementById("toggle-theme");
  toggleBtn.textContent = isDark ? "☀️" : "🌙";
}

// Keyboard shortcuts
document.addEventListener("keydown", (e) => {
  // Don't trigger shortcuts when typing in inputs
  if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA" || e.target.tagName === "SELECT") {
    if (e.key === "ArrowLeft" || e.key === "ArrowRight") {
      // Allow arrow keys in inputs
      return;
    }
  }
  
  // Ctrl/Cmd + Arrow keys for navigation
  if ((e.ctrlKey || e.metaKey) && e.key === "ArrowLeft") {
    e.preventDefault();
    navigateDay(-1);
  } else if ((e.ctrlKey || e.metaKey) && e.key === "ArrowRight") {
    e.preventDefault();
    navigateDay(1);
  }
});

// Event listeners
bibleVersionSelect.addEventListener("change", fetchReading);
readingPlanSelect.addEventListener("change", fetchReading);
document.getElementById("load-reading").addEventListener("click", fetchReading);
document.getElementById("prev-day").addEventListener("click", () => navigateDay(-1));
document.getElementById("next-day").addEventListener("click", () => navigateDay(1));
document.getElementById("export-diary").addEventListener("click", exportDiary);
document.getElementById("toggle-theme").addEventListener("click", toggleDarkMode);

// Auto-save on diary field changes
personalNotes.addEventListener("input", debouncedAutoSave);
marginNotes.addEventListener("input", debouncedAutoSave);
aiInsights.addEventListener("input", debouncedAutoSave);

document.querySelectorAll("button[data-helper]").forEach((btn) => {
  btn.addEventListener("click", () => requestCommentary(btn.dataset.helper));
});
document.getElementById("ask-question").addEventListener("click", askQuestion);
document.getElementById("save-diary").addEventListener("click", saveDiary);

// Load dark mode preference
if (localStorage.getItem("darkMode") === "true") {
  toggleDarkMode();
}

Promise.all([loadVersions(), loadReadingPlans()]).then(fetchReading);
