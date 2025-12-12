/* =============== HELPER =============== */

function fadeHTML() {
    const root = document.documentElement;
    root.classList.add("fade-transition");
    setTimeout(() => root.classList.remove("fade-transition"), 500);
}

/* =============== PALETTE =============== */

function applyPalette(palette, withFade = false) {
    const root = document.documentElement;
    if (withFade) fadeHTML();

    clearCustomPalette();

    root.setAttribute("data-palette", palette);
    localStorage.setItem("palette", palette);
}

/* =============== MODE (LIGHT / DARK) =============== */

function applyMode(mode, withFade = false) {
    const root = document.documentElement;
    if (withFade) fadeHTML();

    root.setAttribute("data-mode", mode);
    localStorage.setItem("mode", mode);
}

function isNightTime() {
    const h = new Date().getHours();
    return (h >= 18 || h < 6);
}

/* =============== INIT LOGIC =============== */

// Load palette (default ocean)
const savedPalette = localStorage.getItem("palette") || "ocean";
applyPalette(savedPalette);

// Check for custom theme
const savedTheme = localStorage.getItem("theme");
if (savedTheme === "custom") {
    document.documentElement.setAttribute("data-theme", "custom");
}

// Load mode
const savedMode = localStorage.getItem("mode");

if (savedMode) {
    // User preference dominates
    applyMode(savedMode);
} else {
    // Auto detect
    applyMode(isNightTime() ? "dark" : "light");
}

/* =============== UI HANDLERS =============== */

const palettePicker = document.getElementById("palette-picker");
if (palettePicker) {
    palettePicker.value = savedPalette;
    palettePicker.addEventListener("change", e => {
        applyPalette(e.target.value, true);
    });
}

// Mode toggle (ex. moon button)
const toggle = document.getElementById("theme-toggle");
if (toggle) {
    toggle.addEventListener("click", () => {
        const current = document.documentElement.getAttribute("data-mode");
        const next = current === "dark" ? "light" : "dark";
        applyMode(next, true);
    });
}

/* =============== CRON AUTO =============== */

setInterval(() => {
    // If the user set a preference manually → do NOT auto change
    if (localStorage.getItem("mode")) return;

    const shouldBeDark = isNightTime();
    const current = document.documentElement.getAttribute("data-mode");

    if ((shouldBeDark && current !== "dark") ||
        (!shouldBeDark && current !== "light")) {

        applyMode(shouldBeDark ? "dark" : "light", true);
    }
}, 60 * 1000);