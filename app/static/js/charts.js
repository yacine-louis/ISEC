/**
 * charts.js — CipherX frequency analysis chart (Chart.js)
 * Renders an animated grouped bar chart for observed vs reference letter frequencies.
 */

"use strict";

const chartsMap = {}; // { canvasId: chartInstance }

/**
 * Initialize or update a frequency chart on a specific canvas.
 * @param {string} canvasId   - ID of the canvas element
 * @param {string[]} labels   - alphabet letters
 * @param {number[]} observed - observed frequencies (0–1)
 * @param {number[]} reference - reference language frequencies (0–1)
 * @param {string}   language  - language name for label
 */
function renderFrequencyChart(canvasId, labels, observed, reference, language) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;

  const accentColor = "rgba(108,99,255,0.85)";
  const refColor = "rgba(0,212,255,0.55)";
  const accentBorder = "rgba(108,99,255,1)";
  const refBorder = "rgba(0,212,255,0.9)";

  // Adapt chart styling to current theme (dark vs light mode)
  const rootStyles = getComputedStyle(document.body);
  const tickColor =
    rootStyles.getPropertyValue("--text-3").trim() || "#535870";
  const isLightMode = document.body.classList.contains("light-mode");
  const gridColorX = isLightMode
    ? "rgba(0,0,0,0.04)"
    : "rgba(255,255,255,0.04)";
  const gridColorY = isLightMode
    ? "rgba(0,0,0,0.10)"
    : "rgba(255,255,255,0.05)";
  const axisBorderColor = isLightMode
    ? "rgba(0,0,0,0.15)"
    : "rgba(255,255,255,0.07)";

  const data = {
    labels,
    datasets: [
      {
        label: "Observed",
        data: observed,
        backgroundColor: accentColor,
        borderColor: accentBorder,
        borderWidth: 1,
        borderRadius: 3,
        borderSkipped: false,
      },
      {
        label: `Reference (${language})`,
        data: reference,
        backgroundColor: refColor,
        borderColor: refBorder,
        borderWidth: 1,
        borderRadius: 3,
        borderSkipped: false,
      },
    ],
  };

  const fontSize = language === "arabic" ? 18 : 12;

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    animation: {
      duration: 600,
      easing: "easeOutQuart",
    },
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: "rgba(17,20,31,0.95)",
        borderColor: "rgba(108,99,255,0.3)",
        borderWidth: 1,
        titleColor: "#e8eaf0",
        bodyColor: "#8b91a8",
        padding: 10,
        callbacks: {
          label: (ctx) =>
            ` ${ctx.dataset.label}: ${(ctx.parsed.y * 100).toFixed(2)}%`,
        },
      },
    },
    scales: {
      x: {
        ticks: {
          color: tickColor,
          font: {
            family: "'Noto Sans Arabic', 'JetBrains Mono', monospace",
            size: fontSize,
          },
          maxRotation: 45,
        },
        grid: { color: gridColorX },
        border: { color: axisBorderColor },
      },
      y: {
        ticks: {
          color: tickColor,
          font: {
            family: "'Noto Sans Arabic', 'JetBrains Mono', monospace",
            size: fontSize,
          },
          callback: (v) => (v * 100).toFixed(1) + "%",
        },
        grid: { color: gridColorY },
        border: { color: axisBorderColor },
        beginAtZero: true,
      },
    },
  };

  if (chartsMap[canvasId]) {
    chartsMap[canvasId].data = data;
    chartsMap[canvasId].update("active");
  } else {
    chartsMap[canvasId] = new Chart(ctx, { type: "bar", data, options });
  }
}

/**
 * Destroy chart by canvas ID (called on panel switch or clear).
 */
function destroyFrequencyChart(canvasId) {
  if (chartsMap[canvasId]) {
    chartsMap[canvasId].destroy();
    delete chartsMap[canvasId];
  }
}
