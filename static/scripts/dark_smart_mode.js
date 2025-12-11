    const emojiBtn = document.getElementById("theme-toggle");

    function animateEmoji(isDark) {
        let frames = isDark
            ? ["🌓", "🌘", "🌙"]   // Light → Dark
            : ["🌙", "🌒", "✨"];   // Dark → Light

        let i = 0;
        const interval = setInterval(() => {
            emojiBtn.textContent = frames[i];
            i++;
            if (i === frames.length) clearInterval(interval);
        }, 60); // viteza fiecărei faze
    }

    /*  ---------------- DARK MODE INTELIGENT ----------------
        ✔ Preferință utilizator → are prioritate absolută
        ✔ Prima vizită → detectare automată
        ✔ Auto schimbare la 18:00 / 06:00
        ✔ Cron → verificare la fiecare minut
        ✔ Tranziție animată fade
        ----------------------------------------------------- */

    function applyTheme(theme, withFade = false) {
        const isDark = theme === "dark"
        if (withFade) {
            document.body.classList.add("fade-transition");
            setTimeout(() => {
                document.body.classList.remove("fade-transition");
            }, 500);
        }

        if (isDark) {
            document.body.classList.add("dark");
        } else {
            document.body.classList.remove("dark");
        }

        // 🔥 Actualizăm emoji-ul aici
        animateEmoji(isDark);
    }

    function isNightTime() {
        const hour = new Date().getHours();
        return (hour >= 18 || hour < 6);
    }

    // 1. Verificăm preferința salvată (user choice)
    const saved = localStorage.getItem("theme");

    if (saved) {
        applyTheme(saved);
    } else {
        // 2. Prima vizită → stabilim în funcție de oră
        applyTheme(isNightTime() ? "dark" : "light");
    }

    // 3. Toggle manual (în acest caz *blochează* detectarea automată)
    document.getElementById("theme-toggle").addEventListener("click", () => {
        const isDark = document.body.classList.toggle("dark");
        localStorage.setItem("theme", isDark ? "dark" : "light");
        applyTheme(isDark ? "dark" : "light", true);
    });

    // 4. CRON → verificare la fiecare minut
    setInterval(() => {
        // Dacă userul a setat manual → nu mai schimbăm automat
        if (localStorage.getItem("theme")) return;

        const shouldBeDark = isNightTime();
        const currentlyDark = document.body.classList.contains("dark");

        if (shouldBeDark !== currentlyDark) {
            applyTheme(shouldBeDark ? "dark" : "light", true);
        }
    }, 60 * 1000); // 1 minut