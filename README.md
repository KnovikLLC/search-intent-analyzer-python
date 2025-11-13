# Search Intent Analyzer (Firecrawl + Classifier)
Version: 1.3.0

Lightweight Streamlit app that combines Firecrawl search/content extraction with a custom classifier to score and analyze search intent from SERP results and page titles. The project provides a hybrid scoring approach (Firecrawl signals + classifier scores) and a simple UI to explore results.

Key features
- Uses Firecrawl APIs to fetch search results and page content
- Applies a custom, uploadable classifier (see `search_intent_classifier.py`) to rank/score results by intent
- Hybrid fusion strategy combining multiple signals with configurable weights
- Streamlit UI (`app.py`) for interactive exploration

Quick start
1. Create and activate a virtual environment (recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set your Firecrawl API key (required):

```bash
export FIRECRAWL_API_KEY="fc-xxxx"
```

4. Run the Streamlit app:

```bash
streamlit run app.py
```

Where things live
- `app.py` — Streamlit application entrypoint and UI wiring
- `search_intent_classifier.py` — classifier utilities / model loading and scoring helpers
- `requirements.txt` — Python dependencies used by the app

Environment variables
- FIRECRAWL_API_KEY: API key for Firecrawl. Obtain from your Firecrawl account and export it before running the app.

Classifier notes
- The classifier module accepts an uploaded model or pre-trained weights (follow the code and docstrings in `search_intent_classifier.py` for details). If your classifier requires additional configuration or files, place them alongside the repo and update the app to point to the path.

Troubleshooting
- "Module not found" when running: make sure the virtualenv is activated and `pip install -r requirements.txt` completed successfully.
- Firecrawl authentication error: confirm `FIRECRAWL_API_KEY` is exported in the same shell used to run Streamlit, and the key is valid.
- If Streamlit shows a blank page or server errors: check the terminal where you ran `streamlit run app.py` for Python traceback and fix missing packages or import errors.

Contributing
- Open an issue describing the feature or bug.
- Create a branch from `dev` for code changes and open a pull request with a clear description and any test notes.

License
- See the `LICENSE` file in the repository root.

Contact / Maintainer
- For questions about this project, open an issue or contact the maintainer listed in the repository metadata.

Small TODOs
- Add example classifier model or a short example showing how to upload a model in the app
- Add unit tests for the classifier helpers in `search_intent_classifier.py`

Enjoy — open the Streamlit UI and start analyzing search intent!
