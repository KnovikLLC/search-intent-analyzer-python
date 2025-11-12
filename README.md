# Search Intent Analyzer (Streamlit)

A lightweight app to classify **search intent** (Informational / Transactional / Navigational / Commercial Investigation)
using SERP features, keyword modifiers, and top-page content cues.

- **Version:** 1.0.0  
- **Author:** Knovik • Madusanka Premaratne (Madus)  
- **License:** MIT

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Push this folder to a **public GitHub repo** (e.g., `knovik/search-intent-analyzer`).
2. Go to https://share.streamlit.io → **Create app** → pick your repo/branch → `app.py`.
3. (Optional) Add API keys in **Settings → Secrets**:

```toml
# Streamlit secrets
SERPAPI_KEY = "xxxxxxxxxxxxxxxx"
```

4. Click **Deploy**. That’s it.

## Versioning

- Start at **1.0.0**
- **Patch** = bug fixes → 1.0.1
- **Minor** = features → 1.1.0
- **Major** = breaking changes → 2.0.0

## Screenshot-like banner/footer

The app renders a centered banner and footer including your name and version.
