# 🔎 Search Intent Analyzer (Firecrawl Edition)

**Version:** 1.2.0  
**Built by:** [Knovik](https://knovik.com) • **Madusanka Premaratne (Madus)**  
**License:** MIT

---

### 🧠 Overview
**Search Intent Analyzer** helps marketing and SEO teams identify the *search intent* behind any keyword using **Firecrawl’s `/v2/search` API**.  
It classifies each keyword into one of four intents:

- **Informational** — Users seeking knowledge or tutorials  
- **Transactional** — Ready-to-buy or action-oriented users  
- **Navigational** — Looking for a brand or specific site  
- **Commercial Investigation** — Comparing options or reviews  

The app visualizes results in an **interactive Streamlit dashboard** with rich charts, color-coded badges, and per-keyword confidence scores.

---

### 🚀 Features
✅ Real-time SERP and content analysis via **Firecrawl**  
✅ Classifies keywords into **4 intent categories**  
✅ **Confidence-based scoring** using SERP features, modifiers, and page content  
✅ **Engaging dashboard** — cards, filters, and charts powered by Plotly  
✅ **CSV export**, expandable result details, and clear visual hierarchy  

---

### 🧩 Tech Stack
- **Python 3.10+**
- **Streamlit**
- **Pandas / NumPy**
- **Plotly**
- **Firecrawl API**

---

### ⚙️ Setup

#### 1. Clone the repository
```bash
git clone https://github.com/KnovikLLC/search-intent-analyzer-python.git
cd search-intent-analyzer-python
