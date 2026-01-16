const apiBase = "/api";

const readingDateInput = document.getElementById("reading-date");
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

const today = new Date().toISOString().split("T")[0];
readingDateInput.value = today;

async function fetchReading() {
  const date = readingDateInput.value;
  const version = bibleVersionSelect.value;
  const response = await fetch(`${apiBase}/readings/${date}?version=${encodeURIComponent(version)}`);
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
  await loadDiary(date, data.passages.join("; "));
  await loadProgress();
}

async function requestCommentary(helper) {
  const date = readingDateInput.value;
  const version = bibleVersionSelect.value;
  const readingResponse = await fetch(`${apiBase}/readings/${date}?version=${encodeURIComponent(version)}`);
  if (!readingResponse.ok) return;
  const reading = await readingResponse.json();
  const response = await fetch(`${apiBase}/commentary`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      passage: reading.passages.join("; "),
      helper: helper,
      personalized: true,
    }),
  });
  const data = await response.json();
  commentaryBox.textContent = data.commentary || "No commentary available.";
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
  const version = bibleVersionSelect.value;
  const readingResponse = await fetch(`${apiBase}/readings/${date}?version=${encodeURIComponent(version)}`);
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
  progressBox.textContent = `${data.completed_readings} / ${data.total_readings} days (${data.completion_percentage}%)`;
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

bibleVersionSelect.addEventListener("change", fetchReading);
document.getElementById("load-reading").addEventListener("click", fetchReading);
document.querySelectorAll("button[data-helper]").forEach((btn) => {
  btn.addEventListener("click", () => requestCommentary(btn.dataset.helper));
});
document.getElementById("ask-question").addEventListener("click", askQuestion);
document.getElementById("save-diary").addEventListener("click", saveDiary);

loadVersions().then(fetchReading);
