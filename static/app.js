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
  
  // Load proactive insights if available
  if (data.passages && data.passages.length > 0) {
    loadProactiveInsights(data.passages[0], date);
  }
}

let currentCommentaryPassage = null;
let currentCommentaryHelper = null;

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
    const passages = reading.passages.join("; ");
    currentCommentaryPassage = passages;
    currentCommentaryHelper = helper;
    
    // Try to get latest version from living commentary system
    try {
      const versionResponse = await fetch(`${apiBase}/commentary/latest/${encodeURIComponent(passages.split(";")[0])}?helper=${helper}`);
      if (versionResponse.ok) {
        const versionData = await versionResponse.json();
        commentaryBox.textContent = versionData.content || "No commentary available.";
        displayCommentaryMeta(versionData);
        checkForConflicts(passages.split(";")[0]);
        return;
      }
    } catch (e) {
      // Fallback to regular generation
    }
    
    // Fallback: generate new commentary
    const response = await fetch(`${apiBase}/commentary`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        passage: passages,
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
    
    // Hide meta if not from living commentary
    document.getElementById("commentary-meta").style.display = "none";
  } catch (error) {
    commentaryBox.textContent = `Error: ${error.message || "Failed to get commentary. Make sure Ollama is running."}`;
  }
}

function displayCommentaryMeta(versionData) {
  const metaDiv = document.getElementById("commentary-meta");
  const versionInfo = document.getElementById("commentary-version-info");
  const qualityScore = document.getElementById("commentary-quality-score");
  
  versionInfo.textContent = `Version ${versionData.version}`;
  qualityScore.textContent = ` | Quality: ${(versionData.quality_score * 100).toFixed(0)}%`;
  
  metaDiv.style.display = "block";
  document.getElementById("view-versions-btn").style.display = "inline-block";
  document.getElementById("feedback-btn").style.display = "inline-block";
}

async function checkForConflicts(passage) {
  try {
    const response = await fetch(`${apiBase}/commentary/conflicts/${encodeURIComponent(passage)}`);
    if (!response.ok) return;
    
    const data = await response.json();
    if (data.conflicts && data.conflicts.length > 0) {
      const conflictsPanel = document.getElementById("commentary-conflicts-panel");
      const conflictsContent = document.getElementById("conflicts-content");
      
      conflictsContent.innerHTML = data.conflicts.map(conflict => `
        <div style="margin: 10px 0; padding: 10px; background: white; border-radius: 4px;">
          <strong>Issue:</strong> ${conflict.issue}
        </div>
      `).join("");
      
      conflictsPanel.style.display = "block";
    }
  } catch (e) {
    // Silently fail
  }
}

async function loadCommentaryVersions() {
  if (!currentCommentaryPassage || !currentCommentaryHelper) return;
  
  const passage = currentCommentaryPassage.split(";")[0];
  const versionsPanel = document.getElementById("commentary-versions-panel");
  const versionsList = document.getElementById("versions-list");
  
  try {
    const response = await fetch(`${apiBase}/commentary/versions/${encodeURIComponent(passage)}?helper=${currentCommentaryHelper}`);
    if (!response.ok) {
      versionsList.innerHTML = "<p>No versions found.</p>";
      return;
    }
    
    const data = await response.json();
    versionsList.innerHTML = data.versions.map(v => `
      <div style="padding: 10px; margin: 10px 0; background: #f9f9f9; border-radius: 4px; border-left: 3px solid #4a90e2;">
        <strong>Version ${v.version}</strong> 
        <span style="color: #666; font-size: 12px;">(${new Date(v.generated_at).toLocaleDateString()})</span>
        <div style="font-size: 12px; margin-top: 5px;">
          Quality: ${(v.quality_score * 100).toFixed(0)}% | 
          Feedback: ${v.feedback_count} | 
          ${v.improvements.length > 0 ? `Improvements: ${v.improvements.join(", ")}` : ""}
        </div>
      </div>
    `).join("");
    
    versionsPanel.style.display = versionsPanel.style.display === "none" ? "block" : "none";
  } catch (error) {
    versionsList.innerHTML = `<p>Error loading versions: ${error.message}</p>`;
  }
}

async function submitCommentaryFeedback() {
  if (!currentCommentaryPassage || !currentCommentaryHelper) return;
  
  const passage = currentCommentaryPassage.split(";")[0];
  const rating = document.getElementById("feedback-rating").value;
  const feedbackText = document.getElementById("feedback-text").value.trim();
  
  if (!rating && !feedbackText) {
    alert("Please provide a rating or feedback.");
    return;
  }
  
  try {
    const response = await fetch(`${apiBase}/commentary/feedback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        passage: passage,
        helper: currentCommentaryHelper,
        feedback: feedbackText || "No comment",
        rating: rating ? parseInt(rating) : null
      })
    });
    
    if (!response.ok) {
      throw new Error("Failed to submit feedback");
    }
    
    const data = await response.json();
    
    if (data.new_version_generated) {
      alert("Thank you for your feedback! A new improved version has been generated.");
      // Reload commentary
      requestCommentary(currentCommentaryHelper);
    } else {
      alert("Thank you for your feedback!");
    }
    
    // Hide feedback panel
    document.getElementById("commentary-feedback-panel").style.display = "none";
    document.getElementById("feedback-rating").value = "";
    document.getElementById("feedback-text").value = "";
  } catch (error) {
    alert(`Error submitting feedback: ${error.message}`);
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

// Living Commentary System integration
document.getElementById("view-versions-btn").addEventListener("click", loadCommentaryVersions);
document.getElementById("feedback-btn").addEventListener("click", () => {
  const panel = document.getElementById("commentary-feedback-panel");
  panel.style.display = panel.style.display === "none" ? "block" : "none";
});
document.getElementById("submit-feedback").addEventListener("click", submitCommentaryFeedback);
document.getElementById("cancel-feedback").addEventListener("click", () => {
  document.getElementById("commentary-feedback-panel").style.display = "none";
  document.getElementById("feedback-rating").value = "";
  document.getElementById("feedback-text").value = "";
});

// Load dark mode preference
if (localStorage.getItem("darkMode") === "true") {
  toggleDarkMode();
}

// Proactive Insights
async function loadProactiveInsights(passage, readingDate) {
  try {
    const response = await fetch(`${apiBase}/predictive/insights/${encodeURIComponent(passage)}?reading_date=${readingDate}`);
    if (!response.ok) return;
    
    const insights = await response.json();
    if (insights.predictions && insights.predictions.length > 0) {
      displayProactiveInsights(insights);
    }
  } catch (error) {
    // Silently fail - insights are optional
  }
}

function displayProactiveInsights(insights) {
  // Create or update insights section
  let insightsBox = document.getElementById("proactive-insights");
  if (!insightsBox) {
    // Find commentary box and add insights above it
    const commentarySection = document.querySelector('section.card h2');
    if (commentarySection && commentarySection.textContent.includes("AI Commentary")) {
      insightsBox = document.createElement("div");
      insightsBox.id = "proactive-insights";
      insightsBox.className = "card";
      insightsBox.style.marginTop = "1.5rem";
      commentarySection.parentElement.parentElement.insertBefore(insightsBox, commentarySection.parentElement);
      
      const title = document.createElement("h2");
      title.textContent = "💡 Proactive Insights";
      insightsBox.appendChild(title);
      
      const content = document.createElement("div");
      content.id = "insights-content";
      content.className = "content";
      insightsBox.appendChild(content);
    }
  }
  
  if (insightsBox) {
    const content = document.getElementById("insights-content");
    if (content) {
      const predictions = insights.predictions.map(p => {
        const icon = {
          "question": "❓",
          "connection": "🔗",
          "warning": "⚠️",
          "suggestion": "💭"
        }[p.type] || "•";
        
        return `<div style="padding: 10px; margin: 8px 0; background: #f0f7ff; border-left: 3px solid #4a90e2; border-radius: 4px;">
          <strong>${icon} ${p.type.charAt(0).toUpperCase() + p.type.slice(1)}:</strong> ${p.content}
        </div>`;
      }).join("");
      
      content.innerHTML = predictions;
    }
  }
}

Promise.all([loadVersions(), loadReadingPlans()]).then(fetchReading);
