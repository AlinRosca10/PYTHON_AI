window.AI_PALETTES = [
    {desc: "pastel calm soft gentle", colors: ["#ffdce5", "#ffeef7", "#e3f6ff", "#f4eaff"]},
    {desc: "sunset warm orange pink", colors: ["#ff9a8b", "#ff6a88", "#ff99ac", "#d4145a"]},
    {desc: "forest deep natural green", colors: ["#a8e6cf", "#56c596", "#379683", "#0b8457"]},
    {desc: "night cyberpunk neon dark", colors: ["#0d0221", "#ff2e63", "#08d9d6", "#252a34"]},
    {desc: "vaporwave retro purple teal", colors: ["#ff71ce", "#01cdfe", "#b967ff", "#05ffa1"]},
    {desc: "coffee beige brown warm", colors: ["#e7d7c1", "#c29b77", "#8f6b4a", "#5c3c23"]},
    {desc: "minimal grey neutral clean", colors: ["#dcdcdc", "#c1c1c1", "#a7a7a7", "#8c8c8c"]},
    {desc: "ocean cold blue teal", colors: ["#6bf3fc", "#33ccee", "#2299dd", "#0b58b3"]},
    {desc: "witchcore dark purple green", colors: ["#2e0249", "#570a57", "#a91079", "#0fbf8f"]},
    {desc: "autumn brown orange golden", colors: ["#e8c07d", "#d9534f", "#c6652e", "#8b4513"]},
    {desc: "ice neon blue arctic", colors: ["#dfffff", "#9ef6ff", "#6ad5ff", "#2ea8ff"]},
    {desc: "desert warm sand yellow", colors: ["#f4e4ba", "#e6b566", "#d89234", "#a65e16"]},
    {desc: "rainy day cold grey blue", colors: ["#c7d0d8", "#a6b1b7", "#7a8b99", "#4a5c66"]},
    {desc: "fire neon hot red", colors: ["#ff595e", "#ffca3a", "#8ac926", "#1982c4"]},
    {desc: "midnight dark blue navy", colors: ["#0a1626", "#0f1f3d", "#112c55", "#1b3a73"]},
    {desc: "cute kawaii candy", colors: ["#ffd6e0", "#ffabe1", "#c0fdff", "#a0ffe6"]},
    {desc: "luxury gold black", colors: ["#000000", "#2d2d2d", "#bfa764", "#f2c572"]},
    {desc: "matte muted modern", colors: ["#c0c5ce", "#a7adba", "#65737e", "#4f5b66"]},
    {desc: "fresh mint green", colors: ["#c4fcef", "#7bdff2", "#059dc0", "#0a5e8f"]},
    {desc: "retro 80s purple blue", colors: ["#8a2be2", "#4b0082", "#4169e1", "#00bfff"]},
];

function embedText(txt) {
    txt = txt.toLowerCase();
    const vec = Array(26).fill(0);

    for (let ch of txt) {
        let i = ch.charCodeAt(0) - 97;
        if (i >= 0 && i < 26) vec[i] += 1;
    }
    return vec;
}

function cosineSimilarity(a, b) {
    let dot = 0, na = 0, nb = 0;
    for (let i = 0; i < a.length; i++) {
        dot += a[i] * b[i];
        na += a[i] * a[i];
        nb += b[i] * b[i];
    }
    return dot / (Math.sqrt(na) * Math.sqrt(nb));
}

function aiGeneratePalette(prompt) {
    const qVec = embedText(prompt);

    let best = null;
    let bestScore = -1;

    for (const p of window.AI_PALETTES) {
        const pVec = embedText(p.desc);
        const score = cosineSimilarity(qVec, pVec);

        if (score > bestScore) {
            best = p;
            bestScore = score;
        }
    }

    // Mică variație estetică random
    return best.colors.map(c => slightlyVary(c));
}

function slightlyVary(hex) {
    const v = 8; // ±8 variație
    let r = parseInt(hex.slice(1,3),16) + (Math.random()*v*2 - v);
    let g = parseInt(hex.slice(3,5),16) + (Math.random()*v*2 - v);
    let b = parseInt(hex.slice(5,7),16) + (Math.random()*v*2 - v);

    r = Math.max(0, Math.min(255, Math.round(r)));
    g = Math.max(0, Math.min(255, Math.round(g)));
    b = Math.max(0, Math.min(255, Math.round(b)));

    return `rgb(${r},${g},${b})`;
}

document.getElementById("ai-generate").addEventListener("click", () => {
    const text = document.getElementById("prompt").value.trim();
    if (!text) return;

    const colors = aiGeneratePalette(text);

    document.documentElement.setAttribute("data-theme", "custom-ai");

    document.documentElement.style.setProperty("--g1", colors[0]);
    document.documentElement.style.setProperty("--g2", colors[1]);
    document.documentElement.style.setProperty("--g3", colors[2]);
    document.documentElement.style.setProperty("--g4", colors[3]);

    localStorage.setItem("palette", "custom-ai");
    localStorage.setItem("aiPrompt", text);
    localStorage.setItem("aiPalette", JSON.stringify(colors));
});