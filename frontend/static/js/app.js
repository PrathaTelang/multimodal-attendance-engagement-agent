/**
 * EduSense AI Dashboard Controller.
 * Handles real-time polling, canvas charts, UI transitions, and tab switches.
 */

document.addEventListener("DOMContentLoaded", () => {
  // Navigation Tabs
  const navTabs = document.querySelectorAll(".nav-tab");
  const tabPanes = document.querySelectorAll(".tab-pane");

  navTabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const target = tab.dataset.tab;
      navTabs.forEach((t) => t.classList.remove("active"));
      tabPanes.forEach((p) => p.classList.remove("active"));

      tab.classList.add("active");
      const targetPane = document.getElementById(target);
      if (targetPane) targetPane.classList.add("active");

      if (target === "tab-teacher") loadTeacherProfile();
      if (target === "tab-analytics") loadAnalyticsTrends();
    });
  });

  // End / Toggle Session Button
  const btnEndSession = document.getElementById("btn-end-session");
  let isSessionRunning = true;

  btnEndSession.addEventListener("click", async () => {
    if (isSessionRunning) {
      if (confirm("End current session and finalize attendance records?")) {
        await fetch("/api/session/stop", { method: "POST" });
        btnEndSession.innerText = "Start Session";
        btnEndSession.style.background = "linear-gradient(135deg, #10b981, #059669)";
        isSessionRunning = false;
      }
    } else {
      await fetch("/api/session/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_name: "CS101: Classroom Intelligence", teacher_id: "T_101" })
      });
      btnEndSession.innerText = "End Session";
      btnEndSession.style.background = "linear-gradient(135deg, #dc2626, #b91c1c)";
      isSessionRunning = true;
    }
  });

  // Initialize Audio Streamer
  const streamer = new window.AudioStreamer();
  streamer.start((metrics) => {
    updateAudioMetricsUI(metrics);
  });

  // Polling Interval for Status & Leaderboard (1.2 seconds)
  setInterval(pollSessionStatus, 1200);
  pollSessionStatus();

  // Export Buttons
  document.getElementById("btn-export-csv")?.addEventListener("click", () => {
    window.location.href = "/api/export/csv";
  });
  document.getElementById("btn-export-pdf")?.addEventListener("click", () => {
    window.open("/api/export/pdf", "_blank");
  });
});

// Update Live Audio Metrics
function updateAudioMetricsUI(audio) {
  if (!audio) return;
  const dbVal = document.getElementById("meter-db-value");
  const dbFill = document.getElementById("meter-db-fill");
  const speechRatio = document.getElementById("meter-speech-ratio");
  const audioState = document.getElementById("audio-state-tag");

  if (dbVal) dbVal.innerText = `${audio.db_level || -45.0} dB`;
  if (speechRatio) speechRatio.innerText = `${Math.round((audio.speech_ratio || 0.1) * 100)}%`;
  
  if (dbFill) {
    // -60 dB to 0 dB mapped to 0-100%
    const pct = Math.max(0, Math.min(100, ((audio.db_level + 60) / 60) * 100));
    dbFill.style.width = `${pct}%`;
  }

  if (audioState && audio.acoustic_state) {
    audioState.innerText = audio.acoustic_state.replace("_", " ").toUpperCase();
  }
}

// Poll Active Session Status
async function pollSessionStatus() {
  try {
    const res = await fetch("/api/session/status");
    if (!res.ok) return;
    const data = await res.json();

    // Session Timer
    const durationSec = data.session_duration_seconds || 0;
    const hrs = String(Math.floor(durationSec / 3600)).padStart(2, "0");
    const mins = String(Math.floor((durationSec % 3600) / 60)).padStart(2, "0");
    const secs = String(durationSec % 60).padStart(2, "0");
    const timerElem = document.getElementById("session-timer");
    if (timerElem) timerElem.innerText = `${hrs}:${mins}:${secs}`;

    // Active Counts & HUD
    const hudTracks = document.getElementById("hud-tracks");
    if (hudTracks) hudTracks.innerText = `Active: ${data.active_participants || 0}`;

    const hudAttn = document.getElementById("hud-avg-attn");
    if (hudAttn) hudAttn.innerText = `Avg Attn: ${Math.round(data.avg_attention || 0)}%`;

    // Audio Widget
    updateAudioMetricsUI(data.audio);

    // AI Suggestions Box
    if (data.ai_insight) {
      const insightElem = document.getElementById("ai-insight-text");
      const recElem = document.getElementById("ai-recommendation-text");
      if (insightElem && data.ai_insight.insight) insightElem.innerText = data.ai_insight.insight;
      if (recElem && data.ai_insight.recommendation) recElem.innerText = data.ai_insight.recommendation;
    }

    // Alerts List
    const alertsContainer = document.getElementById("alerts-container");
    if (alertsContainer && data.alerts) {
      alertsContainer.innerHTML = "";
      data.alerts.slice(0, 3).forEach((alt) => {
        const item = document.createElement("div");
        const severityClass = alt.severity === "high" ? "alert-high" : (alt.severity === "medium" ? "alert-warning" : "alert-info");
        item.className = `alert-item ${severityClass}`;
        item.innerHTML = `<span>●</span> <span>${alt.message}</span>`;
        alertsContainer.appendChild(item);
      });
    }

    // Live Attendance Table
    fetchAttendanceTable();

  } catch (err) {
    console.error("Error polling session status", err);
  }
}

// Fetch Attendance and Populate Leaderboard
async function fetchAttendanceTable() {
  try {
    const res = await fetch("/api/attendance");
    if (!res.ok) return;
    const records = await res.json();

    const tbody = document.getElementById("leaderboard-body");
    if (!tbody) return;

    tbody.innerHTML = "";
    records.forEach((r, idx) => {
      const tr = document.createElement("tr");
      
      let badgeClass = "badge-absent";
      if (r.attendance_status === "Present") badgeClass = "badge-present";
      else if (r.attendance_status === "Partial") badgeClass = "badge-partial";

      tr.innerHTML = `
        <td><strong>#${idx + 1}</strong></td>
        <td>${r.student_name} (${r.person_id})</td>
        <td>${r.presence_duration_seconds}s</td>
        <td><span class="badge-status ${badgeClass}">${r.attendance_status}</span></td>
        <td><strong>${r.avg_attention_score}%</strong></td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {}
}

// Load Teacher Profile Tab
async function loadTeacherProfile() {
  try {
    const res = await fetch("/api/teacher/profile?teacher_id=T_101");
    if (!res.ok) return;
    const p = await res.json();

    document.getElementById("teacher-effectiveness-num").innerText = p.effectiveness_score;
    document.getElementById("teacher-trend-num").innerText = `+${p.trend}% vs last month`;

    const strengthsList = document.getElementById("teacher-strengths-list");
    if (strengthsList && p.strengths) {
      strengthsList.innerHTML = p.strengths.map((s) => `<li>${s}</li>`).join("");
    }

    const recsList = document.getElementById("teacher-recs-list");
    if (recsList && p.recommendations) {
      recsList.innerHTML = p.recommendations.map((r) => `<li>${r}</li>`).join("");
    }

    const historyGrid = document.getElementById("class-history-grid");
    if (historyGrid && p.class_history) {
      historyGrid.innerHTML = p.class_history.map((c) => `
        <div class="class-history-card">
          <div class="class-name">${c.name}</div>
          <div class="class-stat">${c.engagement}% Avg</div>
          <small style="color: #64748b;">Attendance: ${c.attendance || '90%'}</small>
        </div>
      `).join("");
    }
  } catch (err) {}
}

// Load Session Analytics Tab & Render Canvas Charts
async function loadAnalyticsTrends() {
  try {
    const res = await fetch("/api/analytics/trends");
    if (!res.ok) return;
    const data = await res.json();

    renderAttentionLineChart(data.attention_trend);
    renderEmotionBarChart(data.emotion_distribution);
    renderReflectiveSummaries(data.student_summaries);
  } catch (err) {}
}

// Canvas Line Chart for Attention Trend
function renderAttentionLineChart(trendPoints) {
  const canvas = document.getElementById("attention-chart-canvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const w = canvas.width = canvas.parentElement.clientWidth;
  const h = canvas.height = canvas.parentElement.clientHeight || 240;

  ctx.clearRect(0, 0, w, h);

  if (!trendPoints || trendPoints.length < 2) return;

  const padding = 40;
  const graphW = w - padding * 2;
  const graphH = h - padding * 2;

  // Grid lines
  ctx.strokeStyle = "#1e293b";
  ctx.lineWidth = 1;
  for (let i = 0; i <= 4; i++) {
    const y = padding + (graphH / 4) * i;
    ctx.beginPath();
    ctx.moveTo(padding, y);
    ctx.lineTo(w - padding, y);
    ctx.stroke();

    ctx.fillStyle = "#64748b";
    ctx.font = "11px sans-serif";
    ctx.fillText(`${100 - i * 25}%`, 8, y + 4);
  }

  // Draw smooth attention curve
  ctx.beginPath();
  ctx.strokeStyle = "#6366f1";
  ctx.lineWidth = 3;

  trendPoints.forEach((pt, i) => {
    const x = padding + (graphW / (trendPoints.length - 1)) * i;
    const y = padding + graphH - (pt.attention / 100) * graphH;
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.stroke();

  // Gradient area fill
  const grad = ctx.createLinearGradient(0, padding, 0, h - padding);
  grad.addColorStop(0, "rgba(99, 102, 241, 0.35)");
  grad.addColorStop(1, "rgba(99, 102, 241, 0.0)");
  ctx.lineTo(w - padding, h - padding);
  ctx.lineTo(padding, h - padding);
  ctx.closePath();
  ctx.fillStyle = grad;
  ctx.fill();

  // Plot data points
  trendPoints.forEach((pt, i) => {
    const x = padding + (graphW / (trendPoints.length - 1)) * i;
    const y = padding + graphH - (pt.attention / 100) * graphH;
    ctx.beginPath();
    ctx.arc(x, y, 4, 0, Math.PI * 2);
    ctx.fillStyle = "#38bdf8";
    ctx.fill();
    ctx.strokeStyle = "#ffffff";
    ctx.lineWidth = 1.5;
    ctx.stroke();
  });
}

// Canvas Bar Chart for Emotion / Engagement Distribution
function renderEmotionBarChart(distribution) {
  const canvas = document.getElementById("emotion-chart-canvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const w = canvas.width = canvas.parentElement.clientWidth;
  const h = canvas.height = canvas.parentElement.clientHeight || 240;

  ctx.clearRect(0, 0, w, h);
  if (!distribution) return;

  const categories = Object.keys(distribution);
  const values = Object.values(distribution);
  const maxVal = Math.max(...values, 10);

  const colors = {
    focused: "#10b981",
    engaged: "#06b6d4",
    neutral: "#64748b",
    distracted: "#f59e0b",
    drowsy: "#ef4444"
  };

  const padding = 35;
  const barWidth = (w - padding * 2) / categories.length - 15;

  categories.forEach((cat, idx) => {
    const val = values[idx];
    const barH = (val / maxVal) * (h - padding * 2);
    const x = padding + idx * (barWidth + 15) + 8;
    const y = h - padding - barH;

    // Draw bar
    ctx.fillStyle = colors[cat] || "#6366f1";
    ctx.beginPath();
    ctx.roundRect(x, y, barWidth, barH, [4, 4, 0, 0]);
    ctx.fill();

    // Value label
    ctx.fillStyle = "#ffffff";
    ctx.font = "12px sans-serif";
    ctx.textAlign = "center";
    ctx.fillText(`${val}`, x + barWidth / 2, y - 6);

    // Category label
    ctx.fillStyle = "#94a3b8";
    ctx.font = "11px sans-serif";
    ctx.fillText(cat.toUpperCase(), x + barWidth / 2, h - 12);
  });
}

// Render Reflective Student Summaries Table
function renderReflectiveSummaries(summaries) {
  const tbody = document.getElementById("feedback-table-body");
  if (!tbody || !summaries) return;

  tbody.innerHTML = "";
  summaries.forEach((s) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><strong>${s.student_name}</strong> (${s.person_id})</td>
      <td>${s.presence_seconds}s</td>
      <td><span class="badge-status ${s.status === 'Present' ? 'badge-present' : 'badge-partial'}">${s.status}</span></td>
      <td><strong>${s.avg_attention}%</strong></td>
      <td class="feedback-pill">${s.reflective_feedback}</td>
    `;
    tbody.appendChild(tr);
  });
}
