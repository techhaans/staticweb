function applyTranslations(translations) {
    // Replace innerText for elements with data-i18n
    document.querySelectorAll("[data-i18n]").forEach((el) => {
        const key = el.getAttribute("data-i18n");
        if (translations[key]) {
            el.textContent = translations[key];
        }
    });

    // Replace placeholder for elements with data-i18n-placeholder
    document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
        const key = el.getAttribute("data-i18n-placeholder");
        if (translations[key]) {
            el.setAttribute("placeholder", translations[key]);
        }
    });
}

function loadLanguage(lang) {
    const existingScript = document.getElementById("lang-script");
    if (existingScript) {
        existingScript.remove();
    }

    const script = document.createElement("script");
    script.id = "lang-script";
    script.src = `translations/_${lang}.js`;
    script.onload = () => {
        const langData = window[`translations_${lang}`];
        console.log(langData);
        if (!langData) {
            console.error(`Translation data not found for language: ${lang}`);
            return;
        }
        applyTranslations(langData);
    };
    document.body.appendChild(script);
}

document.getElementById("language").addEventListener("change", function () {
    loadLanguage(this.value);
});

window.addEventListener("DOMContentLoaded", () => {
    loadLanguage("en");
});
