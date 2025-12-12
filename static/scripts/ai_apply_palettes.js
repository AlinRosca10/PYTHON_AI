async function applyPaletteColors(colors, caption) {
    // assume colors is array of 4 (#rrggbb or rgb(...))
    if (!Array.isArray(colors) || colors.length < 4) return;
    document.documentElement.setAttribute("data-theme", "custom-ai");
    document.documentElement.style.setProperty("--g1", colors[0]);
    document.documentElement.style.setProperty("--g2", colors[1]);
    document.documentElement.style.setProperty("--g3", colors[2]);
    document.documentElement.style.setProperty("--g4", colors[3]);

    // show preview
    const preview = document.getElementById("ai-palette-preview");
    preview.innerHTML = "";
    colors.slice(0,4).forEach(c => {
        const el = document.createElement("div");
        el.style.width = "36px";
        el.style.height = "36px";
        el.style.borderRadius = "6px";
        el.style.background = c;
        el.title = c;
        preview.appendChild(el);
    });

    if (caption) {
        const t = document.createElement("div");
        t.style.marginLeft = "12px";
        t.style.color = "var(--muted)";
        t.textContent = caption;
        preview.appendChild(t);
    }

    // save
    localStorage.setItem("palette", "custom-ai");
    localStorage.setItem("aiPalette", JSON.stringify(colors));
    localStorage.setItem("aiPrompt", document.getElementById("ai-prompt").value || "");
}

document.getElementById("ai-gen-btn").addEventListener("click", async () => {
    const prompt = document.getElementById("ai-prompt").value.trim();
    if (!prompt) return alert("Scrie o descriere: ex 'night cyberpunk'");

    // UX: arată că cererea rulează
    const btn = document.getElementById("ai-gen-btn");
    btn.disabled = true;
    btn.textContent = "Generare…";

    try {
        const resp = await fetch("/api/generate_palette", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ prompt })
        });

        if (!resp.ok) {
            const err = await resp.json().catch(()=>({error: "server"}));
            alert("Eroare: " + (err.error || resp.statusText));
            return;
        }

        const data = await resp.json();
        const colors = data.colors;
        const caption = data.caption || (`${prompt} — ${data.source}`);
        await applyPaletteColors(colors, caption);

    } catch (e) {
        console.error(e);
        alert("Eroare la generare.");
    } finally {
        btn.disabled = false;
        btn.textContent = "Generează paletă AI";
    }
});

// reaplică paleta AI la load dacă există
const savedAI = localStorage.getItem("aiPalette");
if (savedAI) {
    try {
        const colors = JSON.parse(savedAI);
        const caption = localStorage.getItem("aiPrompt") || "";
        applyPaletteColors(colors, caption);
    } catch(e){}
}