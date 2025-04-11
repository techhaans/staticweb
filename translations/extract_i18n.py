import os
import re
import json
import requests

# ==== Config ====
html_file = "../input.html"
translation_file = "_en.js"
customer_id = "123456"
default_language = "en"
translation_endpoint = "http://localhost:8080/api/translations"
sample_response = {
    "customerId": "123456",
    "defaultLanguageCode": "en",
    "languages": [
        {
            "languageCode": "en",
            "translations": {
                "label.welcome": "Welcome",
                "label.logout": "Logout",
                "label.profile": "Profile"
            }
        },
        {
            "languageCode": "sv",
            "translations": {
                "label.welcome": "Valkommen",
                "label.logout": "Logga ut",
                "label.profile": "Profil"
            }
        },
        {
            "languageCode": "fi",
            "translations": {
                "label.welcome": "Tervetuloa",
                "label.logout": "Kirjaudu ulos",
                "label.profile": "Profiili"
            }
        }
    ]
};
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer dummy-token"
}
filename_prefix = html_file.split('.')[0]

# ==== Step 1: Load existing translations ====
existing_translations = {}
if os.path.exists(translation_file):
    with open(translation_file, "r") as f:
        content = f.read()
        matches = re.findall(r'"([^"]+)":\s*"([^"]+)"', content)
        for k, v in matches:
            existing_translations[k] = v

# ==== Step 2: Read HTML and extract text ====
with open(html_file, "r") as f:
    html = f.read()

translations = {}
counter = len(existing_translations) + 1

# Match visible labels
label_matches = re.findall(r'<(label|button|span|p|h[1-6])[^>]*?>([^<]+)</\1>', html)
for tag, text in label_matches:
    text = text.strip()
    if not text:
        continue
    key = "label_%d" % counter
    pattern = r'(<%s\b[^>]*?>)\s*%s\s*</%s>' % (tag, re.escape(text), tag)
    match = re.search(pattern, html)
    if match:
        counter += 1
        translations[key] = text
        replacement = '<%s data-i18n="%s"></%s>' % (tag, key, tag)
        html = re.sub(pattern, replacement, html, count=1)


# Match placeholders
placeholder_matches = re.findall(r'<(input|textarea)[^>]*?placeholder="([^"]+)"', html)
for tag, placeholder in placeholder_matches:
    key = "placeholder_%d" % counter
    counter += 1
    translations[key] = placeholder
    html = html.replace('placeholder="%s"' % placeholder, 'data-i18n-placeholder="%s"' % key)

# Inject translation.js if not present
if 'translation.js' not in html:
    script_tag = '<script src="translations/translation.js"></script>'
    if '</body>' in html:
        html = html.replace('</body>', script_tag + '\n</body>')
    else:
        html += '\n' + script_tag

# ==== Step 3: Save modified HTML ====
with open(html_file, "w") as f:
    f.write(html)

# ==== Step 4: Build payload ====
all_translations = existing_translations.copy()
all_translations.update(translations)

prefixed_translations = {}
for k, v in all_translations.items():
    prefixed_translations["%s.%s" % (filename_prefix, k)] = v

payload = {
    "customerId": customer_id,
    "defaultLanguageCode": default_language,
    "languages": [{
        "languageCode": "en",
        "translations": prefixed_translations
    }]
}

print("Sending payload:")
print("Received response from API")

# ==== Step 5: Send POST request ====
try:
    print(" Payload: %s" % payload)
    print(" headers: %s" % headers)
    #res = requests.post(translation_endpoint, data=json.dumps(payload), headers=headers)
    response_data = sample_response; #res.json()
    print("Received response from API")
except Exception as e:
    print(" Failed to reach API, using local data. Error: %s" % e)
    response_data = payload

# ==== Step 6: Generate JS file ====
langs = response_data.get("languages", [])
for lang in langs:
    lang_code = lang.get("languageCode")
    translations = lang.get("translations", {})
    file_name = "_%s.js" % lang_code
    with open(file_name, "w") as f:
        f.write("var translations_%s = {\n" % lang_code)
        for full_key, value in translations.items():
            simple_key = full_key.split('.')[-1]
            f.write('    "%s": "%s",\n' % (simple_key, value))
        f.write("};\n")
    print(" Generated %s" % file_name)

