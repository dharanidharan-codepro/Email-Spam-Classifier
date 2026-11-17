/**
 * Sleep Quality Predictor — Frontend JavaScript
 * 
 * Features:
 *  - Animated star & particle background
 *  - Form validation with inline error animations
 *  - API calls to Flask /predict endpoint
 *  - Dramatic result display with animations
 *  - localStorage prediction history
 *  - Chart.js trend visualizations
 *  - Toast notifications with slide-in
 *  - Confetti burst on "Good" prediction
 */

// ============================================================
//  DOM ELEMENTS
// ============================================================
const sleepForm = document.getElementById('sleep-form');
const btnPredict = document.getElementById('btn-predict');
const btnReset = document.getElementById('btn-reset');
const btnHistory = document.getElementById('btn-history');
const btnClearHistory = document.getElementById('btn-clear-history');

const loadingOverlay = document.getElementById('loading-overlay');
const resultSection = document.getElementById('result-section');
const resultCard = document.getElementById('result-card');
const resultEmoji = document.getElementById('result-emoji');
const resultLabel = document.getElementById('result-label');
const resultDescription = document.getElementById('result-description');
const resultConfidence = document.getElementById('result-confidence');
const confidenceFill = document.getElementById('confidence-fill');
const tipsList = document.getElementById('tips-list');

const historySection = document.getElementById('history-section');
const historyTableContainer = document.getElementById('history-table-container');
const chartsGrid = document.getElementById('charts-grid');

const stressSlider = document.getElementById('stress');
const stressDisplay = document.getElementById('stress-display');

const STORAGE_KEY = 'sleep_predictor_history';
const API_URL = '/predict';

// ============================================================
//  INIT
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
    initSlider();
    initEventListeners();
});

// ============================================================
//  ANIMATED STARS
// ============================================================
function createStars() {
    const container = document.getElementById('stars-container');
    if (!container) return;

    for (let i = 0; i < 100; i++) {
        const star = document.createElement('div');
        star.className = 'star' + (Math.random() > 0.85 ? ' large' : '');
        star.style.left = Math.random() * 100 + '%';
        star.style.top = Math.random() * 100 + '%';
        star.style.setProperty('--dur', (2 + Math.random() * 5) + 's');
        star.style.setProperty('--max-op', (0.3 + Math.random() * 0.7).toFixed(2));
        star.style.animationDelay = (Math.random() * 6) + 's';
        container.appendChild(star);
    }
}

// ============================================================
//  FLOATING PARTICLES
// ============================================================
function createParticles() {
    const colors = [
        'rgba(124, 111, 255, 0.15)',
        'rgba(168, 85, 247, 0.12)',
        'rgba(236, 72, 153, 0.1)',
        'rgba(99, 102, 241, 0.12)',
        'rgba(192, 132, 252, 0.1)',
    ];

    for (let i = 0; i < 15; i++) {
        const p = document.createElement('div');
        p.className = 'particle';
        const size = 4 + Math.random() * 8;
        p.style.width = size + 'px';
        p.style.height = size + 'px';
        p.style.left = Math.random() * 100 + '%';
        p.style.top = Math.random() * 100 + '%';
        p.style.background = colors[Math.floor(Math.random() * colors.length)];
        p.style.setProperty('--p-dur', (6 + Math.random() * 10) + 's');
        p.style.setProperty('--p-opacity', (0.1 + Math.random() * 0.2).toFixed(2));
        p.style.setProperty('--p-x1', (Math.random() * 60 - 30) + 'px');
        p.style.setProperty('--p-y1', (Math.random() * 60 - 30) + 'px');
        p.style.setProperty('--p-x2', (Math.random() * 60 - 30) + 'px');
        p.style.setProperty('--p-y2', (Math.random() * 60 - 30) + 'px');
        p.style.setProperty('--p-x3', (Math.random() * 60 - 30) + 'px');
        p.style.setProperty('--p-y3', (Math.random() * 60 - 30) + 'px');
        p.style.animationDelay = (Math.random() * 8) + 's';
        document.body.appendChild(p);
    }
}

// ============================================================
//  CONFETTI BURST (for "Good" results)
// ============================================================
function burstConfetti() {
    const colors = ['#34d399', '#6366f1', '#fbbf24', '#a855f7', '#ec4899', '#3b82f6'];
    const container = document.body;

    for (let i = 0; i < 40; i++) {
        const piece = document.createElement('div');
        piece.style.cssText = `
            position: fixed;
            width: ${4 + Math.random() * 6}px;
            height: ${4 + Math.random() * 6}px;
            background: ${colors[Math.floor(Math.random() * colors.length)]};
            border-radius: ${Math.random() > 0.5 ? '50%' : '2px'};
            left: 50%;
            top: 50%;
            z-index: 150;
            pointer-events: none;
            opacity: 1;
        `;

        const angle = Math.random() * Math.PI * 2;
        const velocity = 100 + Math.random() * 200;
        const dx = Math.cos(angle) * velocity;
        const dy = Math.sin(angle) * velocity - 100;
        const rotation = Math.random() * 720 - 360;

        piece.animate([
            { transform: 'translate(0, 0) rotate(0deg)', opacity: 1 },
            { transform: `translate(${dx}px, ${dy + 300}px) rotate(${rotation}deg)`, opacity: 0 }
        ], {
            duration: 1200 + Math.random() * 800,
            easing: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)',
        }).onfinish = () => piece.remove();

        container.appendChild(piece);
    }
}

// ============================================================
//  STRESS SLIDER
// ============================================================
function initSlider() {
    if (!stressSlider || !stressDisplay) return;
    const update = () => {
        const val = stressSlider.value;
        stressDisplay.textContent = val + '/10';
        // Keep the stress value readable while signaling higher levels warmly.
        stressDisplay.style.color = val <= 5 ? 'var(--mint)' : 'var(--peach)';
    };
    stressSlider.addEventListener('input', update);
    update();
}

// ============================================================
//  EVENT LISTENERS
// ============================================================
function initEventListeners() {
    sleepForm.addEventListener('submit', handleSubmit);
    btnReset.addEventListener('click', handleReset);
    btnHistory.addEventListener('click', toggleHistory);
    btnClearHistory.addEventListener('click', clearHistory);

    // Clear validation on input
    sleepForm.querySelectorAll('.form-input, .form-select').forEach(input => {
        input.addEventListener('input', () => clearFieldError(input));
        input.addEventListener('change', () => clearFieldError(input));
    });

    sleepForm.querySelectorAll('input[type="radio"]').forEach(radio => {
        radio.addEventListener('change', () => {
            const el = document.getElementById('error-interruptions');
            if (el) el.classList.remove('visible');
        });
    });
}

// ============================================================
//  VALIDATION
// ============================================================
function validateForm() {
    let valid = true;
    clearAllErrors();

    const checks = [
        {
            id: 'sleep-duration',
            test: v => v && !isNaN(parseFloat(v)) && parseFloat(v) > 0 && parseFloat(v) <= 24,
            msg: 'Please enter a valid sleep duration (0.5-24 hours).'
        },
        { id: 'bedtime', test: v => !!v, msg: 'Please select a valid bedtime.' },
        { id: 'wake-time', test: v => !!v, msg: 'Please select a valid wake-up time.' },
        { id: 'caffeine', test: v => !!v, msg: 'Please select a caffeine intake level.' },
        {
            id: 'exercise',
            test: v => v !== '' && !isNaN(parseFloat(v)) && parseFloat(v) >= 0 && parseFloat(v) <= 300,
            msg: 'Please enter a valid exercise duration (0-300 min).'
        },
        {
            id: 'screen-time',
            test: v => v !== '' && !isNaN(parseFloat(v)) && parseFloat(v) >= 0 && parseFloat(v) <= 600,
            msg: 'Please enter a valid screen time (0-600 min).'
        },
        { id: 'mood', test: v => !!v, msg: 'Please select your mood before sleep.' },
    ];

    checks.forEach(({ id, test, msg }) => {
        const el = document.getElementById(id);
        if (!test(el.value)) {
            showFieldError(id, msg);
            valid = false;
        }
    });

    // Radio check
    if (!document.querySelector('input[name="interruptions"]:checked')) {
        const e = document.getElementById('error-interruptions');
        if (e) { e.textContent = 'Please select yes or no.'; e.classList.add('visible'); }
        valid = false;
    }

    return valid;
}

function showFieldError(fieldId, message) {
    const input = document.getElementById(fieldId);
    const err = document.getElementById('error-' + fieldId);
    if (input) input.classList.add('invalid');
    if (err) { err.textContent = message; err.classList.add('visible'); }
}

function clearFieldError(input) {
    input.classList.remove('invalid');
    const err = document.getElementById('error-' + input.id);
    if (err) err.classList.remove('visible');
}

function clearAllErrors() {
    document.querySelectorAll('.error-message').forEach(e => e.classList.remove('visible'));
    document.querySelectorAll('.invalid').forEach(e => e.classList.remove('invalid'));
}

// ============================================================
//  FORM SUBMISSION
// ============================================================
async function handleSubmit(e) {
    e.preventDefault();

    if (!validateForm()) {
        showToast('Please fix the errors in the form.', 'error');
        return;
    }

    const data = {
        sleep_duration: parseFloat(document.getElementById('sleep-duration').value),
        bedtime: document.getElementById('bedtime').value,
        wake_time: document.getElementById('wake-time').value,
        caffeine: document.getElementById('caffeine').value,
        exercise: parseFloat(document.getElementById('exercise').value),
        screen_time: parseFloat(document.getElementById('screen-time').value),
        stress: parseInt(stressSlider.value, 10),
        mood: document.getElementById('mood').value,
        interruptions: document.querySelector('input[name="interruptions"]:checked').value,
    };

    showLoading(true);
    resultSection.classList.remove('visible');

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });

        const result = await response.json();

        if (!response.ok) {
            const msg = result.error || 'Prediction failed.';
            const details = result.details;
            showToast(Array.isArray(details) ? msg + ' ' + details.join(' ') : msg, 'error');
            return;
        }

        displayResult(result);
        saveToHistory(data, result);
        showToast('Prediction complete!', 'success');

    } catch (error) {
        console.error('API Error:', error);
        showToast('Could not connect to the server. Make sure Flask is running.', 'error');
    } finally {
        showLoading(false);
    }
}

// ============================================================
//  DISPLAY RESULT
// ============================================================
function displayResult(result) {
    const prediction = result.prediction;
    const confidence = result.confidence;
    const tips = result.tips || [];

    resultCard.classList.remove('result-good', 'result-average', 'result-poor');

    const configs = {
        'Good': {
            emoji: '&#127769;',
            label: 'GOOD',
            desc: 'Your predicted sleep quality is Good. Keep it up!',
            cls: 'result-good'
        },
        'Average': {
            emoji: '&#128528;',
            label: 'AVERAGE',
            desc: 'Your predicted sleep quality is Average. Small changes can help!',
            cls: 'result-average'
        },
        'Poor': {
            emoji: '&#9888;&#65039;',
            label: 'POOR',
            desc: 'Your predicted sleep quality is Poor. Check the suggestions below.',
            cls: 'result-poor'
        }
    };

    const cfg = configs[prediction] || configs['Average'];
    resultEmoji.innerHTML = cfg.emoji;
    resultLabel.textContent = cfg.label;
    resultDescription.textContent = cfg.desc;
    resultCard.classList.add(cfg.cls);

    // Confidence bar
    if (confidence != null) {
        const pct = Math.round(confidence * 100);
        resultConfidence.textContent = 'Confidence: ' + pct + '%';
        confidenceFill.style.width = '0%';
        setTimeout(() => { confidenceFill.style.width = pct + '%'; }, 150);
    } else {
        resultConfidence.textContent = '';
        confidenceFill.style.width = '0%';
    }

    // Tips
    tipsList.innerHTML = '';
    tips.forEach(tip => {
        const div = document.createElement('div');
        div.className = 'tip-item';
        div.textContent = tip;
        tipsList.appendChild(div);
    });

    // Show
    resultSection.classList.add('visible');
    setTimeout(() => resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' }), 250);

    // Confetti on Good
    if (prediction === 'Good') {
        setTimeout(burstConfetti, 400);
    }
}

// ============================================================
//  RESET
// ============================================================
function handleReset() {
    sleepForm.reset();
    clearAllErrors();
    resultSection.classList.remove('visible');

    stressSlider.value = 5;
    stressDisplay.textContent = '5/10';
    stressDisplay.style.color = 'var(--mint)';

    document.getElementById('bedtime').value = '23:00';
    document.getElementById('wake-time').value = '06:30';
    document.getElementById('caffeine').value = 'Moderate';
    document.getElementById('mood').value = 'Neutral';

    showToast('Form reset successfully.', 'info');
}

// ============================================================
//  LOADING
// ============================================================
function showLoading(show) {
    if (show) {
        loadingOverlay.classList.add('active');
        btnPredict.disabled = true;
    } else {
        loadingOverlay.classList.remove('active');
        btnPredict.disabled = false;
    }
}

// ============================================================
//  TOAST
// ============================================================
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = 'toast toast-' + type;

    const icons = { error: '\u26A0', success: '\u2713', info: '\u2139' };
    toast.textContent = (icons[type] || '') + '  ' + message;

    container.appendChild(toast);
    setTimeout(() => { if (toast.parentNode) toast.remove(); }, 4200);
}

// ============================================================
//  HISTORY
// ============================================================
function getHistory() {
    try {
        const raw = localStorage.getItem(STORAGE_KEY);
        return raw ? JSON.parse(raw) : [];
    } catch { return []; }
}

function saveToHistory(inputData, result) {
    const history = getHistory();
    history.unshift({
        id: Date.now(),
        date: new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
        time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        sleep_duration: inputData.sleep_duration,
        exercise: inputData.exercise,
        screen_time: inputData.screen_time,
        stress: inputData.stress,
        caffeine: inputData.caffeine,
        mood: inputData.mood,
        interruptions: inputData.interruptions,
        prediction: result.prediction,
        confidence: result.confidence,
        tips: result.tips,
    });
    if (history.length > 50) history.pop();
    localStorage.setItem(STORAGE_KEY, JSON.stringify(history));

    if (historySection.classList.contains('visible')) renderHistory();
}

function toggleHistory() {
    if (historySection.classList.contains('visible')) {
        historySection.classList.remove('visible');
        btnHistory.innerHTML = '&#128202; Past Predictions';
    } else {
        renderHistory();
        historySection.classList.add('visible');
        btnHistory.innerHTML = '&#128202; Hide History';
        setTimeout(() => historySection.scrollIntoView({ behavior: 'smooth', block: 'start' }), 200);
    }
}

function renderHistory() {
    const history = getHistory();

    if (history.length === 0) {
        historyTableContainer.innerHTML = `
            <div class="empty-state">
                <span class="empty-icon">&#128203;</span>
                <p>No predictions yet.</p>
                <p style="font-size:0.85rem; margin-top:6px; opacity:0.6;">Make your first prediction to start tracking!</p>
            </div>`;
        chartsGrid.style.display = 'none';
        return;
    }

    let html = '<table class="history-table"><thead><tr>';
    html += '<th>Date</th><th>Time</th><th>Sleep</th><th>Exercise</th><th>Screen</th><th>Stress</th><th>Result</th>';
    html += '</tr></thead><tbody>';

    history.forEach(e => {
        const bc = 'badge-' + e.prediction.toLowerCase();
        html += `<tr><td>${e.date}</td><td>${e.time}</td><td>${e.sleep_duration}h</td>
                 <td>${e.exercise} min</td><td>${e.screen_time} min</td><td>${e.stress}/10</td>
                 <td><span class="badge ${bc}">${e.prediction}</span></td></tr>`;
    });

    html += '</tbody></table>';
    historyTableContainer.innerHTML = html;

    if (history.length >= 2) {
        chartsGrid.style.display = 'grid';
        renderCharts(history);
    } else {
        chartsGrid.style.display = 'none';
    }
}

function clearHistory() {
    if (getHistory().length === 0) {
        showToast('History is already empty.', 'info');
        return;
    }
    localStorage.removeItem(STORAGE_KEY);
    renderHistory();
    showToast('Prediction history cleared.', 'success');
}

// ============================================================
//  CHARTS
// ============================================================
let chartInstances = {};

function destroyChart(id) {
    if (chartInstances[id]) { chartInstances[id].destroy(); delete chartInstances[id]; }
}

function chartDefaults() {
    return {
        responsive: true,
        maintainAspectRatio: true,
        plugins: { legend: { display: false } },
        scales: {
            x: { ticks: { color: '#706c99', font: { size: 10 } }, grid: { color: 'rgba(255,255,255,0.03)' } },
            y: { ticks: { color: '#706c99', font: { size: 10 } }, grid: { color: 'rgba(255,255,255,0.03)' } },
        },
        elements: { line: { tension: 0.4, borderWidth: 2.5 }, point: { radius: 4, hoverRadius: 7 } },
    };
}

function renderCharts(history) {
    const data = [...history].reverse().slice(-15);
    const labels = data.map(e => e.date);

    // Sleep
    destroyChart('sleep');
    const c1 = document.getElementById('chart-sleep');
    if (c1) chartInstances['sleep'] = new Chart(c1, {
        type: 'line',
        data: { labels, datasets: [{ data: data.map(e => e.sleep_duration), borderColor: '#a78bfa', backgroundColor: 'rgba(167,139,250,0.08)', fill: true }] },
        options: { ...chartDefaults(), scales: { ...chartDefaults().scales, y: { ...chartDefaults().scales.y, suggestedMin: 3, suggestedMax: 11 } } },
    });

    // Stress
    destroyChart('stress');
    const c2 = document.getElementById('chart-stress');
    if (c2) chartInstances['stress'] = new Chart(c2, {
        type: 'line',
        data: { labels, datasets: [{ data: data.map(e => e.stress), borderColor: '#fbbf24', backgroundColor: 'rgba(251,191,36,0.08)', fill: true }] },
        options: { ...chartDefaults(), scales: { ...chartDefaults().scales, y: { ...chartDefaults().scales.y, suggestedMin: 0, suggestedMax: 10 } } },
    });

    // Screen
    destroyChart('screen');
    const c3 = document.getElementById('chart-screen');
    if (c3) chartInstances['screen'] = new Chart(c3, {
        type: 'line',
        data: { labels, datasets: [{ data: data.map(e => e.screen_time), borderColor: '#f87171', backgroundColor: 'rgba(248,113,113,0.08)', fill: true }] },
        options: chartDefaults(),
    });

    // Quality
    destroyChart('quality');
    const c4 = document.getElementById('chart-quality');
    if (c4) {
        const qMap = { 'Good': 3, 'Average': 2, 'Poor': 1 };
        const qColors = data.map(e => e.prediction === 'Good' ? '#34d399' : e.prediction === 'Average' ? '#fbbf24' : '#f87171');
        chartInstances['quality'] = new Chart(c4, {
            type: 'bar',
            data: { labels, datasets: [{ data: data.map(e => qMap[e.prediction] || 2), backgroundColor: qColors, borderRadius: 8, barThickness: 22 }] },
            options: { ...chartDefaults(), scales: { ...chartDefaults().scales, y: { ...chartDefaults().scales.y, min: 0, max: 4, ticks: { ...chartDefaults().scales.y.ticks, callback: v => ({ 1: 'Poor', 2: 'Avg', 3: 'Good' }[v] || ''), stepSize: 1 } } } },
        });
    }
}
