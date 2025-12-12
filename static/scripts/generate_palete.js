// FUNCȚIE utility – conversie HSV → RGB
function hsvToRgb(h, s, v) {
    let f = (n, k = (n + h / 60) % 6) =>
        v - v * s * Math.max(Math.min(k, 4 - k, 1), 0);
    return [f(5), f(3), f(1)];
}

// GENEREAZĂ PALETE ESTETICE
function generatePalette() {
    // O nuanță principală random
    const baseHue = Math.floor(Math.random() * 360);

    // 3 variații armonice
    const hues = [
        baseHue,
        (baseHue + 40) % 360,
        (baseHue + 80) % 360,
        (baseHue + 200) % 360
    ];

    // Saturație și luminozitate random-„estetică”
    const s = 0.45 + Math.random() * 0.35;  // 45%–80%
    const v = 0.75 + Math.random() * 0.25;  // 75%–100%

    const colors = hues.map(h => {
        const [r, g, b] = hsvToRgb(h, s, v);
        return `rgb(${Math.floor(r * 255)}, ${Math.floor(g * 255)}, ${Math.floor(b * 255)})`;
    });

    return {
        g1: colors[0],
        g2: colors[1],
        g3: colors[2],
        g4: colors[3],
    };
}

// APLICAREA PALETEI CUSTOM
function applyCustomPalette(p) {
    document.documentElement.setAttribute("data-theme", "custom");

    document.documentElement.style.setProperty("--g1", p.g1);
    document.documentElement.style.setProperty("--g2", p.g2);
    document.documentElement.style.setProperty("--g3", p.g3);
    document.documentElement.style.setProperty("--g4", p.g4);
}

// CLICK → GENEREAZĂ
document.getElementById("generate-palette").addEventListener("click", () => {
    const pal = generatePalette();
    applyCustomPalette(pal);

    // salvăm în localStorage
    localStorage.setItem("theme", "custom");
    localStorage.setItem("customPalette", JSON.stringify(pal));
});

// Dacă există paletă custom → o reaplicăm
const savedPal = localStorage.getItem("customPalette");
if (savedPal) {
    applyCustomPalette(JSON.parse(savedPal));
}