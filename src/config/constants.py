__version__ = "2.0.0"
AUTHOR = "Knovik Engineering Team"

INTENTS = ["Informational", "Transactional", "Navigational", "Commercial Investigation"]

INTENT_COLORS = {
    "Informational": "#2563eb",
    "Transactional": "#16a34a",
    "Navigational": "#f59e0b",
    "Commercial Investigation": "#ef4444",
}

AVAILABLE_MODELS = [
    "llama3.2:3b",
    "llama3.2:1b",
    "llama3.1:8b",
    "mistral:7b",
    "phi3:mini",
    "gemma2:2b",
]

EXAMPLE_QUERIES = """how to learn python programming
buy macbook pro 2024
facebook login page
best noise cancelling headphones
what is artificial intelligence
download spotify premium
apple official website
nike air max vs adidas ultraboost"""

CARD_CSS = """<style>
.badge{display:inline-block;padding:3px 10px;border-radius:999px;font-size:12px;font-weight:600;color:white}
.card{border:1px solid #e6e6e6;border-radius:14px;padding:14px 16px;margin-bottom:12px;background:#fff}
.card h4{margin:0 0 6px 0}
.kv{font-size:13px;color:#444}
.kv b{color:#111}
.smallmuted{color:#666;font-size:12px}
.reasoning{background:#f8f9fa;padding:10px;border-left:3px solid #2563eb;margin-top:8px;font-size:13px}
.score-bar{display:flex;align-items:center;margin:4px 0}
.score-label{width:180px;font-weight:500}
.score-progress{flex:1;height:20px;background:#e9ecef;border-radius:4px;overflow:hidden}
.score-fill{height:100%;background:#2563eb;transition:width 0.3s}
.score-value{width:60px;text-align:right;font-weight:600}
</style>"""
