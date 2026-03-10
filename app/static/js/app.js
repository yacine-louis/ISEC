/**
 * app.js — CipherX SPA logic
 * Handles routing, API calls, animations, and all UI interactions.
 */

"use strict";

// ─── State ──────────────────────────────────────────────────────────────────
const state = {
  currentPanel: "encrypt",
  settings: {
    darkMode: true,
    animation: true,
    defaultLang: "english",
    defaultCipher: "caesar",
  },
};

// ─── DOM helpers ─────────────────────────────────────────────────────────────
const $ = (id) => document.getElementById(id);
const qs = (sel) => document.querySelector(sel);

// ─── Toast notification ───────────────────────────────────────────────────────
let toastTimer;
function showToast(msg, type = "info", duration = 2800) {
  const t = $("toast");
  t.textContent = msg;
  t.className = `toast ${type} show`;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    t.classList.remove("show");
  }, duration);
}

// ─── Status bar ──────────────────────────────────────────────────────────────
function setStatus(label, type = "ready") {
  const dot = $("status-dot");
  const lbl = $("status-label");
  lbl.textContent = label;
  dot.className =
    "status-dot" +
    (type === "busy" ? " busy" : type === "error" ? " error" : "");
}

// ─── Scan-line animation ──────────────────────────────────────────────────────
function playScanAnimation() {
  if (!state.settings.animation) return Promise.resolve();
  return new Promise((resolve) => {
    const overlay = $("scan-overlay");
    overlay.classList.remove("hidden");
    // reset
    const line = overlay.querySelector(".scan-line");
    line.style.animation = "none";
    void line.offsetWidth; // reflow
    line.style.animation = "";
    setTimeout(() => {
      overlay.classList.add("hidden");
      resolve();
    }, 850);
  });
}

// ─── Copy to clipboard ────────────────────────────────────────────────────────
async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text);
    showToast("Copied to clipboard ✓", "success");
  } catch {
    showToast("Copy failed — select & copy manually", "error");
  }
}

// ─── Shuffle array ───────────────────────────────────────────────────────────
function shuffleArray(array) {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
}

// ─── Export to file ───────────────────────────────────────────────────────────
function exportText(text, filename = "output.txt") {
  const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
  showToast("File downloaded ✓", "success");
}

// ─── Load text from file ──────────────────────────────────────────────────────
function loadFile(fileInput, targetArea) {
  fileInput.click();
  fileInput.onchange = () => {
    const file = fileInput.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => {
      targetArea.value = e.target.result;
      targetArea.dispatchEvent(new Event("input"));
      showToast(`Loaded "${file.name}" ✓`, "info");
    };
    reader.readAsText(file, "UTF-8");
    fileInput.value = "";
  };
}

// ─── Result display ───────────────────────────────────────────────────────────
function setOutput(el, text) {
  el.textContent = text;
  el.classList.remove("result-appear");
  void el.offsetWidth;
  el.classList.add("result-appear");
  el.style.color = text ? "var(--accent-2)" : "var(--text-3)";
}

// ─── API call wrapper ─────────────────────────────────────────────────────────
async function apiCall(endpoint, body) {
  const resp = await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ error: resp.statusText }));
    throw new Error(err.error || `HTTP ${resp.status}`);
  }
  return resp.json();
}

// ─── Panel Navigation ─────────────────────────────────────────────────────────
const PANEL_TITLES = {
  encrypt: ["Encrypt", "Transform plaintext into ciphertext"],
  decrypt: ["Decrypt", "Recover plaintext from ciphertext"],
  frequency: ["Frequency Analysis", "Visualise letter distribution patterns"],
  settings: ["Settings", "Customise your CipherX experience"],
};

function switchPanel(name) {
  document.querySelectorAll(".panel").forEach((p) => p.classList.add("hidden"));
  document
    .querySelectorAll(".nav-item")
    .forEach((n) => n.classList.remove("active"));

  // Handle charts canvas resizing issue when switching panels
  if (name === "decrypt" && chartsMap["dec-freq-chart"]) {
    setTimeout(() => chartsMap["dec-freq-chart"].resize(), 0);
  }
  if (name === "frequency" && chartsMap["freq-chart"]) {
    setTimeout(() => chartsMap["freq-chart"].resize(), 0);
  }

  $(`panel-${name}`).classList.remove("hidden");
  $(`nav-${name}`).classList.add("active");

  const [title, sub] = PANEL_TITLES[name];
  $("page-title").textContent = title;
  $("page-sub").textContent = sub;
  state.currentPanel = name;
}

// ─────────────────────────────────────────────────────────────────────────────
//  ENCRYPT PANEL
// ─────────────────────────────────────────────────────────────────────────────
function initEncryptPanel() {
  const input = $("enc-input");
  const output = $("enc-output");

  // Character counter
  input.addEventListener("input", () => {
    $("enc-char-count").textContent = input.value.length;
  });

  // Cipher selector → show/hide key params
  $("enc-cipher").addEventListener("change", () => updateEncCipherParams());
  updateEncCipherParams();

  // Language selector → clear substitution key when language changes
  $("enc-language").addEventListener("change", () => {
    const language = $("enc-language").value;
    const placeholders = {
      english: "abcdefghijklmnopqrstuvwxyz",
      arabic: "ابتثجحخدذرزسشصضطظعغفقكلمنهوي",
    };
    if ($("enc-cipher").value === "substitution") {
      $("enc-key").value = "";
      $("enc-key").placeholder = placeholders[language] || "";
    }
  });

  // Load file
  $("enc-load-file").addEventListener("click", () =>
    loadFile($("enc-file-input"), input),
  );

  // Clear
  $("enc-clear").addEventListener("click", () => {
    input.value = "";
    $("enc-char-count").textContent = "0";
    output.innerHTML =
      '<span class="output-placeholder">Encrypted text will appear here…</span>';
    const badge = $("enc-meta-badge");
    if (badge) badge.classList.add("hidden");
  });

  // Copy
  $("enc-copy").addEventListener("click", () => {
    const txt = output.textContent;
    if (txt && !txt.includes("will appear")) copyText(txt);
  });

  // Export
  $("enc-export").addEventListener("click", () => {
    const txt = output.textContent;
    if (txt && !txt.includes("will appear")) exportText(txt, "ciphertext.txt");
  });

  // Encrypt button
  $("enc-btn").addEventListener("click", async () => {
    const text = input.value.trim();
    if (!text) {
      showToast("Please enter some text first", "error");
      return;
    }

    const cipher = $("enc-cipher").value;
    const language = $("enc-language").value;
    const body = { text, cipher, language };

    if (cipher === "caesar") body.shift = parseInt($("enc-shift").value) || 3;
    if (cipher === "affine") {
      body.a = parseInt($("enc-a").value) || 5;
      body.b = parseInt($("enc-b").value) || 8;
    }
    if (cipher === "substitution") {
      body.key = $("enc-key").value.trim();
      const alphabets = {
        english: "abcdefghijklmnopqrstuvwxyz",
        arabic: "ابتثجحخدذرزسشصضطظعغفقكلمنهوي",
      };
      const alphabet = alphabets[language];
      const key = body.key;
      if (
        key.length !== alphabet.length ||
        new Set(key).size !== alphabet.length ||
        ![...key].every((c) => alphabet.includes(c))
      ) {
        showToast(
          "Invalid substitution key. It must contain each letter of the alphabet exactly once.",
          "error",
        );
        return;
      }
    }

    setStatus("Encrypting…", "busy");
    $("enc-btn").classList.add("loading");

    try {
      await playScanAnimation();
      const data = await apiCall("/api/encrypt", body);
      setOutput(output, data.result);

      let metaText = `Time: ${data.execution_time_ms}ms`;
      if (data.meta) {
          if (cipher === "caesar") metaText += ` | Shift: ${data.meta.shift}`;
          if (cipher === "affine") metaText += ` | a: ${data.meta.a}, b: ${data.meta.b}`;
          if (cipher === "substitution") metaText += ` | Key: ${data.meta.key}`;
      }
      const badge = $("enc-meta-badge");
      if (badge) {
          badge.textContent = metaText;
          badge.classList.remove("hidden");
      }

      showToast("Encryption complete ✓", "success");
      setStatus("Ready");
    } catch (e) {
      showToast(e.message, "error");
      setStatus("Error", "error");
      setTimeout(() => setStatus("Ready"), 3000);
    } finally {
      $("enc-btn").classList.remove("loading");
    }
  });
}

function updateEncCipherParams() {
  const c = $("enc-cipher").value;
  const language = $("enc-language").value;
  const placeholders = {
    english: "abcdefghijklmnopqrstuvwxyz",
    arabic: "ابتثجحخدذرزسشصضطظعغفقكلمنهوي",
  };
  $("enc-caesar-params").classList.toggle("hidden", c !== "caesar");
  $("enc-affine-params").classList.toggle("hidden", c !== "affine");
  $("enc-sub-params").classList.toggle("hidden", c !== "substitution");
  if (c === "substitution") {
    $("enc-key").placeholder = placeholders[language] || "";
  }
}

// Shuffle key for substitution
$("enc-shuffle-key").addEventListener("click", () => {
  const language = $("enc-language").value;
  const alphabets = {
    english: "abcdefghijklmnopqrstuvwxyz",
    arabic: "ابتثجحخدذرزسشصضطظعغفقكلمنهوي",
  };
  const alphabet = alphabets[language];
  const shuffled = shuffleArray(alphabet.split("")).join("");
  $("enc-key").value = shuffled;
  showToast("Key shuffled ✓", "success");
});

// ─────────────────────────────────────────────────────────────────────────────
//  DECRYPT PANEL
// ─────────────────────────────────────────────────────────────────────────────
function initDecryptPanel() {
  const input = $("dec-input");
  const output = $("dec-output");

  input.addEventListener("input", () => {
    $("dec-char-count").textContent = input.value.length;
  });

  $("dec-language").addEventListener("change", () => {
    const language = $("dec-language").value;
  });
  $("dec-cipher").addEventListener("change", () => updateDecParams());
  updateDecParams();

  $("dec-load-file").addEventListener("click", () =>
    loadFile($("dec-file-input"), input),
  );
  $("dec-clear").addEventListener("click", () => {
    input.value = "";
    $("dec-char-count").textContent = "0";
    output.innerHTML =
      '<span class="output-placeholder">Decrypted text will appear here…</span>';
    $("dec-chart-container").classList.add("hidden");
    destroyFrequencyChart("dec-freq-chart");
    const badge = $("dec-meta-badge");
    if (badge) badge.classList.add("hidden");
  });
  $("dec-copy").addEventListener("click", () => {
    const txt = output.textContent;
    if (txt && !txt.includes("will appear")) copyText(txt);
  });
  $("dec-export").addEventListener("click", () => {
    const txt = output.textContent;
    if (txt && !txt.includes("will appear")) exportText(txt, "plaintext.txt");
  });

  $("dec-btn").addEventListener("click", async () => {
    const text = input.value.trim();
    if (!text) {
      showToast("Please paste some ciphertext first", "error");
      return;
    }

    const cipher = $("dec-cipher").value;
    const language = $("dec-language").value;
    const body = { text, cipher, language, method: "frequency" };

    const ngram_size = parseInt($("dec-ngram-size").value) || 4;
    body.ngram_size = ngram_size;
    if (cipher === "caesar") {
      const top_n_map = { 1: 10, 2: 20, 3: 50, 4: 100 };
      body.top_n = top_n_map[ngram_size] || 10;
    } else if (cipher === "affine") {
      const top_n_map = { 1: 8, 2: 6, 3: 5, 4: 4 };
      body.top_n = top_n_map[ngram_size] || 8;
    } else {
      body.top_n = 10;
    }

    setStatus("Decrypting…", "busy");
    $("dec-btn").classList.add("loading");

    try {
      await playScanAnimation();
      const data = await apiCall("/api/decrypt", body);
      setOutput(output, data.result);

      let metaText = `Time: ${data.execution_time_ms}ms`;
      if (data.meta) {
          if (cipher === "caesar") metaText += ` | Shift: ${data.meta.shift}`;
          if (cipher === "affine") metaText += ` | a: ${data.meta.a}, b: ${data.meta.b}`;
          if (cipher === "substitution") metaText += ` | Key: ${data.meta.key}`;
      }
      const badge = $("dec-meta-badge");
      if (badge) {
          badge.textContent = metaText;
          badge.classList.remove("hidden");
      }

      // Immediately load frequency data for the decrypted result
      try {
        const freqData = await apiCall("/api/frequency", {
          text: data.result,
          language: language,
        });
        const labels = freqData.alphabet;
        const observed = labels.map((l) => freqData.observed[l] || 0);
        const reference = labels.map((l) => freqData.reference[l] || 0);

        $("dec-chart-container").classList.remove("hidden");
        renderFrequencyChart(
          "dec-freq-chart",
          labels,
          observed,
          reference,
          freqData.language,
        );
      } catch (err) {
        console.warn("Could not load frequency data for decrypted text:", err);
        $("dec-chart-container").classList.add("hidden");
      }

      showToast("Decryption complete ✓", "success");
      setStatus("Ready");
    } catch (e) {
      showToast(e.message, "error");
      setStatus("Error", "error");
      setTimeout(() => setStatus("Ready"), 3000);
    } finally {
      $("dec-btn").classList.remove("loading");
    }
  });
}

function updateDecParams() {
  const cipher = $("dec-cipher").value;
  $("dec-freq-params").classList.toggle(
    "hidden",
    !(cipher === "caesar" || cipher === "affine" || cipher === "substitution"),
  );
}

// ─────────────────────────────────────────────────────────────────────────────
//  FREQUENCY ANALYSIS PANEL
// ─────────────────────────────────────────────────────────────────────────────
function initFrequencyPanel() {
  $("freq-language").addEventListener("change", () => {
    const language = $("freq-language").value;
  });

  $("freq-clear").addEventListener("click", () => {
    $("freq-input").value = "";
    destroyFrequencyChart("freq-chart");
    $("freq-stats").innerHTML = "";
  });

  $("freq-load-file").addEventListener("click", () =>
    loadFile($("freq-file-input"), $("freq-input")),
  );

  $("freq-btn").addEventListener("click", async () => {
    const text = $("freq-input").value.trim();
    const language = $("freq-language").value;
    if (!text) {
      showToast("Enter some text to analyse", "error");
      return;
    }

    setStatus("Analysing…", "busy");
    try {
      const data = await apiCall("/api/frequency", { text, language });

      const labels = data.alphabet;
      const observed = labels.map((l) => data.observed[l] || 0);
      const reference = labels.map((l) => data.reference[l] || 0);

      renderFrequencyChart(
        "freq-chart",
        labels,
        observed,
        reference,
        data.language,
      );

      // Stats
      const uniqueLetters = Object.values(data.observed).filter(
        (v) => v > 0,
      ).length;
      const topLetter = labels.reduce((a, b) =>
        (data.observed[a] || 0) > (data.observed[b] || 0) ? a : b,
      );
      $("freq-stats").innerHTML = `
        <div class="freq-stat">
          <span class="freq-stat-value">${data.total_chars}</span>
          <span class="freq-stat-label">Total letters</span>
        </div>
        <div class="freq-stat">
          <span class="freq-stat-value">${uniqueLetters}</span>
          <span class="freq-stat-label">Unique letters</span>
        </div>
        <div class="freq-stat">
          <span class="freq-stat-value">${topLetter.toUpperCase()}</span>
          <span class="freq-stat-label">Most frequent</span>
        </div>
        <div class="freq-stat">
          <span class="freq-stat-value">${data.language}</span>
          <span class="freq-stat-label">Language</span>
        </div>
      `;

      showToast("Frequency analysis complete ✓", "success");
      setStatus("Ready");
    } catch (e) {
      showToast(e.message, "error");
      setStatus("Error", "error");
      setTimeout(() => setStatus("Ready"), 3000);
    }
  });
}

// ─────────────────────────────────────────────────────────────────────────────
//  SETTINGS PANEL
// ─────────────────────────────────────────────────────────────────────────────
function initSettingsPanel() {
  $("settings-dark-mode").addEventListener("change", (e) => {
    state.settings.darkMode = e.target.checked;
    document.body.classList.toggle("light-mode", !e.target.checked);
    showToast(
      e.target.checked ? "Dark mode enabled" : "Light mode enabled",
      "info",
    );
  });

  $("settings-animation").addEventListener("change", (e) => {
    state.settings.animation = e.target.checked;
    showToast(
      e.target.checked ? "Animations enabled" : "Animations disabled",
      "info",
    );
  });

  $("settings-default-lang").addEventListener(
    "change",
    (e) => (state.settings.defaultLang = e.target.value),
  );
  $("settings-default-cipher").addEventListener(
    "change",
    (e) => (state.settings.defaultCipher = e.target.value),
  );
}

// ─────────────────────────────────────────────────────────────────────────────
//  SIDEBAR NAVIGATION
// ─────────────────────────────────────────────────────────────────────────────
function initNav() {
  document.querySelectorAll(".nav-item").forEach((btn) => {
    btn.addEventListener("click", () => switchPanel(btn.dataset.panel));
  });
}

// ─────────────────────────────────────────────────────────────────────────────
//  KEYBOARD SHORTCUTS
// ─────────────────────────────────────────────────────────────────────────────
function initKeyboard() {
  document.addEventListener("keydown", (e) => {
    if (e.altKey) {
      if (e.key === "1") switchPanel("encrypt");
      if (e.key === "2") switchPanel("decrypt");
      if (e.key === "3") switchPanel("frequency");
      if (e.key === "4") switchPanel("settings");
    }
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      // Trigger active panel's action button
      if (state.currentPanel === "encrypt") $("enc-btn").click();
      if (state.currentPanel === "decrypt") $("dec-btn").click();
      if (state.currentPanel === "frequency") $("freq-btn").click();
    }
  });
}

// ─────────────────────────────────────────────────────────────────────────────
//  BOOT
// ─────────────────────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  initNav();
  initEncryptPanel();
  initDecryptPanel();
  initFrequencyPanel();
  initSettingsPanel();
  initKeyboard();
  switchPanel("encrypt");
  setStatus("Ready");
});
