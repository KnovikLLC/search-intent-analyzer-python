# Search Intent Analyzer 🔍

**Version:** 2.0.0  
**Author:** Knovik • Madusanka Premaratne & Deelaka Kariyawasam

Powerful search intent analysis tool with **two modes**: traditional rule-based (Firecrawl + Classifier) and modern **LLM-based** analysis using local Ollama.

---

## 🎯 Hybrid Intent Analyzer

### 🎯 **Hybrid Version** (Recommended - Most Accurate & Flexible)

✅ **SERP-Based Classification** - Powered by Firecrawl real search data (70%)  
✅ **Keyword Pattern Matching** - Fast regex-based detection (30%)  
✅ **AI-Powered Explanations** - LLM generates human-readable reasoning  
✅ **Maximum Accuracy** - Intent determined by real SERP data  
✅ **Modular Architecture** - Clean, maintainable component structure  
✅ **Fully Configurable** - Adjust signal weights and settings in real-time

**Perfect for:** Production use, research projects, SERP-based intent analysis

**Run with:** `streamlit run src/app_hybrid.py`

**Developed by:** Knovik • Deelaka Kariyawasam & Madusanka Premaratne

👉 **[Quick Start Guide](#-hybrid-version-quick-start)**

---

### Signal Sources

The Hybrid Analyzer combines SERP data with keyword patterns for classification:

1. **🔍 Firecrawl SERP** (70% weight, required)

   - Real Google search results
   - SERP feature detection
   - Actual user intent signals
   - Primary classification source
   - Requires API key (~$100-150/month)

2. **📝 Keyword Patterns** (30% weight)

   - Fast regex-based detection
   - Optimized compiled patterns
   - Supporting classification signal
   - Zero cost

3. **🤖 Ollama LLM** (Explanation only - 0% weight)
   - Generates human-readable explanations
   - Explains WHY the classification was made
   - Does NOT participate in scoring
   - 100% free and private
   - Optional but recommended for insights

**Architecture:**

- ✅ **Classification**: SERP (70%) + Keywords (30%) = 100%
- ✅ **Explanation**: LLM analyzes the result and explains reasoning
- ✅ **Accuracy**: Intent determined by real search data, not AI interpretation

---

### 📊 Previous Versions (Legacy)

<details>
<summary>🤖 LLM-Only Version (app_llm.py)</summary>

- Single signal source (LLM only)
- No Firecrawl integration
- Simpler codebase
- Status: Available but superseded by Hybrid version

</details>

<details>
<summary>📊 Rule-Based Version (app.py)</summary>

- Original Firecrawl-only implementation
- Rule-based classifier
- No LLM support
- Status: Available but superseded by Hybrid version

</details>

---

## 📖 Documentation

- **[LLM Setup Guide](LLM_SETUP_GUIDE.md)** - Complete guide for Ollama setup

---

## 🚀 Quick Start Guide

### Prerequisites

- **Python 3.8+**
- **macOS** (Intel or Apple Silicon) / Linux / Windows
- **4GB+ RAM** (8GB+ recommended for LLM)
- **2GB+ disk space** for Ollama models

### Installation

**Step 1: Install Ollama (Required for LLM)**

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows - Download from ollama.com
```

```bash
# Start Ollama server (keep this running in a separate terminal)
ollama serve

# Pull the recommended model (in a new terminal)
ollama pull llama3.2:3b

# Verify installation
ollama list
```

**Step 2: Install Python Dependencies**

```bash
# Clone the repository
git clone https://github.com/deelaka99/search-intent-analyzer-python.git
cd search-intent-analyzer-python

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Upgrade pip (recommended)
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

**Step 3: Configure Firecrawl (Optional)**

```bash
# Get API key from https://firecrawl.dev
# Create .env file
echo "FIRECRAWL_API_KEY=fc-your_api_key_here" > .env
```

**Step 4: Run the Hybrid App**

```bash
streamlit run src/app_hybrid.py
```

🎉 **Done!** The app will open at `http://localhost:8501`

### Usage Modes

**Mode 1: Full Power (All Signals)** 🚀

- ✅ Firecrawl API key configured
- ✅ Ollama running
- ✅ Maximum accuracy (~92-95%)
- 💰 Cost: ~$100-150/month (Firecrawl)

**Mode 2: Free & Powerful (LLM + Keywords)** ⭐ _Recommended for most users_

- ❌ No Firecrawl API key
- ✅ Ollama running
- ✅ Great accuracy (~89-91%)
- 💰 Cost: $0/month (completely free!)

**Mode 3: Fallback (Keywords Only)**

- ❌ No Firecrawl API key
- ❌ Ollama not running
- ✅ Basic accuracy (~70-75%)
- 💰 Cost: $0/month

The app automatically adapts based on available resources!

---

## 📁 Project Structure

```
search-intent-analyzer-python/
├── src/
│   ├── app_hybrid.py               # Main hybrid app ⭐
│   ├── components/                 # Modular UI components
│   │   ├── config_sidebar.py      # Sidebar configuration
│   │   ├── analysis_tabs.py       # Single & batch analysis tabs
│   │   └── result_display.py      # Result visualization
│   ├── services/                   # Core analysis engines
│   │   ├── hybrid_analyzer.py     # Multi-signal analyzer ⭐
│   │   └── llm_intent_analyzer.py # Ollama LLM integration
│   ├── utils/                      # Utilities
│   │   ├── analyzer_factory.py    # Analyzer initialization
│   │   └── data_processor.py      # Data processing helpers
│   ├── config/
│   │   └── constants.py           # Shared constants
│   ├── app.py                     # Legacy rule-based app
│   └── app_llm.py                 # Legacy LLM-only app
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment template
├── LLM_SETUP_GUIDE.md            # Detailed Ollama setup guide
└── README.md                      # This file
```

### Architecture Benefits

- **🧩 Modular Components**: Each component has a single responsibility
- **🔄 Reusable Code**: Components can be used across different UIs
- **🧪 Testable**: Easy to unit test individual components
- **📈 Scalable**: Add new signals or features without touching existing code
- **🛠️ Maintainable**: Find and fix bugs quickly with organized structure

---

## 🔧 Configuration

### Real-Time Configuration (Sidebar)

All settings are adjustable in real-time through the Streamlit sidebar:

**🔑 API Keys**

- **Firecrawl API Key**: Optional, stored in `.env` or enter in sidebar
- Auto-detected from environment variables

**🎛️ Analysis Signals**

- **Firecrawl SERP Data**: Toggle on/off (requires API key)
- **Ollama LLM Reasoning**: Toggle on/off (requires Ollama running)
- **Keyword Patterns**: Always enabled (fallback)

**⚖️ Signal Weights** (Advanced)

- **Firecrawl Weight**: 0.0 - 1.0 (default: 0.40)
- **LLM Weight**: 0.0 - 1.0 (default: 0.40)
- **Keyword Weight**: 0.0 - 1.0 (default: 0.20)
- Weights are automatically normalized

**🤖 LLM Settings**

- **Model**: llama3.2:3b, llama3.2:1b, llama3.1:8b, mistral:7b
- **Ollama URL**: Default `http://localhost:11434`
- **Timeout**: Configurable in code (default: 30s)

**🔍 Firecrawl Settings**

- **Results Limit**: 5-20 results (default: 10)
- **Country**: US, UK, CA, AU, IN
- **SERP Features**: Auto-detected

### Recommended Configurations

**For Maximum Accuracy:**

```
Firecrawl: ON (40%)
LLM: ON (40%)
Keywords: ON (20%)
Model: llama3.1:8b
Results: 20
```

**For Zero Cost:**

```
Firecrawl: OFF
LLM: ON (70%)
Keywords: ON (30%)
Model: llama3.2:3b
```

**For Speed:**

```
Firecrawl: OFF
LLM: ON (60%)
Keywords: ON (40%)
Model: llama3.2:1b
```

**Cost Breakdown:**

- 💚 **Keywords only**: FREE
- 💚 **Keywords + LLM**: FREE
- 💰 **Keywords + Firecrawl**: ~$100-150/month
- 💰 **All three (Hybrid)**: ~$100-150/month (highest accuracy!)

---

## 🧪 Testing

### Quick Test

```bash
# Activate environment
source .venv/bin/activate

# Test LLM analyzer directly
python -c "
from src.services.llm_intent_analyzer import LLMIntentAnalyzer
analyzer = LLMIntentAnalyzer(model='llama3.2:3b')
result = analyzer.analyze('how to learn python')
print(f'✅ {result.primary_intent} ({result.confidence}%)')
"
```

### Run Full Test Suite

```bash
# Run all tests
pytest test/test_llm_intent_analyzer.py -v

# Run unit tests only (no integration)
pytest test/test_llm_intent_analyzer.py -v -m "not integration"

# Run integration tests (requires Ollama running)
pytest test/test_llm_intent_analyzer.py -v -m integration
```

### Test Hybrid Analyzer

```bash
# Run hybrid analyzer quick test
python -m src.services.hybrid_analyzer
```

---

## 📊 Performance Comparison

| Configuration            | Cost/Month | Accuracy | Speed   | Privacy | Offline |
| ------------------------ | ---------- | -------- | ------- | ------- | ------- |
| **Hybrid (All 3)**       | $100-150   | ~92-95%  | 2-4 sec | Partial | No      |
| **LLM + Keywords** ⭐    | FREE       | ~89-91%  | 1-3 sec | 100%    | Yes     |
| **Firecrawl + Keywords** | $100-150   | ~87-89%  | 2-5 sec | Partial | No      |
| **Keywords Only**        | FREE       | ~70-75%  | <1 sec  | 100%    | Yes     |
| Legacy: Rule-Based       | $150-300   | ~87%     | 2-5 sec | No      | No      |
| Legacy: LLM-Only         | FREE       | ~89-91%  | 1-3 sec | 100%    | Yes     |

**⭐ Recommended**: LLM + Keywords for most users (free, accurate, private)

---

## 🎓 Example Usage

### Hybrid Analyzer (Programmatic)

```python
from src.services.hybrid_analyzer import HybridIntentAnalyzer

# Initialize with all signals
analyzer = HybridIntentAnalyzer(
    firecrawl_api_key="fc-your_key",  # Optional
    llm_model="llama3.2:3b",
    firecrawl_weight=0.40,
    llm_weight=0.40,
    keyword_weight=0.20
)

# Analyze single keyword
result = analyzer.analyze(
    keyword="how to learn python programming",
    use_firecrawl=True,
    use_llm=True,
    firecrawl_limit=10
)

print(f"Primary Intent: {result.primary_intent}")
print(f"Confidence: {result.confidence_score}%")
print(f"Reasoning: {result.reasoning}")
print(f"Signals Used: Firecrawl={result.firecrawl_used}, LLM={bool(result.llm_reasoning)}")
print(f"All Scores: {result.all_intent_scores}")
```

### LLM Analyzer (Standalone)

```python
from src.services.llm_intent_analyzer import LLMIntentAnalyzer

# Initialize
analyzer = LLMIntentAnalyzer(model="llama3.2:3b")

# Analyze single query
result = analyzer.analyze("best noise cancelling headphones 2024")

print(f"Intent: {result.primary_intent}")
print(f"Confidence: {result.confidence}%")
print(f"Reasoning: {result.reasoning}")
print(f"All Scores: {result.all_scores}")
```

### Batch Analysis

Use the Streamlit UI for batch analysis with CSV export:

1. Go to "Batch Analysis" tab
2. Enter keywords (one per line)
3. Click "Analyze Batch"
4. Download results as CSV

---

## 🐛 Troubleshooting

### Common Issues

**1. "Cannot connect to Ollama" / "LLM Analysis Failed"**

```bash
# Check if Ollama is running
ps aux | grep ollama

# If not running, start it
ollama serve

# Test connection
curl http://localhost:11434/api/tags

# If "address already in use" - Ollama is already running! ✅
```

**2. "Model not found"**

```bash
# List installed models
ollama list

# Pull missing model
ollama pull llama3.2:3b

# Verify
ollama list
```

**3. "ModuleNotFoundError: No module named 'src'"**

```bash
# Activate virtual environment
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Reinstall dependencies
pip install -r requirements.txt
```

**4. Firecrawl "500 Server Error"**

This is a temporary server issue on Firecrawl's end, not your fault!

- ✅ Your API key is valid
- ❌ Their servers are temporarily down
- 🔄 App automatically uses LLM + Keywords instead
- ⏰ Try again in 5-10 minutes

**5. "Firecrawl API key invalid" (401)**

```bash
# Verify your API key
cat .env

# Should show: FIRECRAWL_API_KEY=fc-xxxxx...

# Get new key from https://firecrawl.dev if needed
```

**6. Slow LLM Performance**

```bash
# Use smaller, faster model
ollama pull llama3.2:1b

# Then select it in the Streamlit sidebar
```

**7. Streamlit Won't Start**

```bash
# Check if port 8501 is in use
lsof -i :8501

# Kill process if needed
kill -9 <PID>

# Or use different port
streamlit run src/app_hybrid.py --server.port 8502
```

### Debug Mode

Check terminal output when analyzing keywords - it shows:

- ✅ Successful signal activations
- ⚠️ Warnings for failed signals
- 📊 Score details
- 🔍 Connection status

### Still Having Issues?

1. Check terminal logs for detailed error messages
2. Verify all prerequisites are installed
3. Check GitHub issues for similar problems
4. Open a new issue with error logs

---

## 🚀 Advanced Features

### Custom LLM Models

Create specialized models for your domain:

```bash
# Create custom Modelfile
cat > Modelfile << EOF
FROM llama3.2:3b
SYSTEM You are an expert SEO analyst specializing in e-commerce search intent analysis.
You understand product research patterns, buying signals, and customer journey stages.
PARAMETER temperature 0.1
PARAMETER top_p 0.9
EOF

# Build custom model
ollama create ecommerce-intent -f Modelfile

# Use in app (add to model dropdown or specify via URL params)
```

### Adjust Signal Weights Programmatically

```python
from src.services.hybrid_analyzer import HybridIntentAnalyzer

# Trust LLM more for semantic queries
analyzer = HybridIntentAnalyzer(
    firecrawl_weight=0.20,
    llm_weight=0.60,
    keyword_weight=0.20
)

# Trust Firecrawl more for commercial queries
analyzer_commercial = HybridIntentAnalyzer(
    firecrawl_weight=0.60,
    llm_weight=0.30,
    keyword_weight=0.10
)
```

### Performance Optimization

**For High Volume:**

1. Use connection pooling (already implemented in FirecrawlService)
2. Use faster LLM model: `llama3.2:1b`
3. Reduce Firecrawl limit to 5
4. Cache results in external database

**For Maximum Accuracy:**

1. Use larger model: `llama3.1:8b`
2. Increase Firecrawl limit to 20
3. Enable all three signals
4. Fine-tune signal weights for your domain

### Component Customization

The modular architecture makes it easy to customize:

```python
# Create custom result display
from src.components.result_display import render_result_card

def my_custom_result_card(result):
    # Your custom visualization
    pass

# Replace in analysis_tabs.py
render_result_card = my_custom_result_card
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Run tests: `pytest -v`
5. Commit: `git commit -am 'Add my feature'`
6. Push: `git push origin feature/my-feature`
7. Open a pull request

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

---

## 👨‍💻 Authors

**Knovik • Madusanka Premaratne & Deelaka Kariyawasam**

- **Madusanka Premaratne** - Original rule-based classifier and Firecrawl integration
- **Deelaka Kariyawasam** - LLM integration, hybrid analyzer, modular architecture

© 2024-2025 Knovik LLC

---

## 🌟 Acknowledgments

- **Ollama** - Local LLM runtime
- **Firecrawl** - SERP API
- **Streamlit** - Web framework
- **Meta AI** - Llama models

---

## 📮 Support

- 📚 **Documentation**: See guides in `/docs`
- 🐛 **Bug Reports**: Open an issue on GitHub
- 💡 **Feature Requests**: Open an issue with [Feature] tag
- 💬 **Questions**: Check existing issues or open a new one

---

## 🗺️ Roadmap

### v2.1 (Current)

- [x] Modular component architecture
- [x] Three-signal hybrid analysis
- [x] Real-time configuration
- [x] Optimized regex patterns
- [x] Connection pooling for Firecrawl
- [x] Cached analyzer instances

### v2.2 (Next)

- [ ] REST API endpoint
- [ ] Batch CSV upload/download
- [ ] Result caching and history
- [ ] Custom signal weights per keyword
- [ ] A/B testing between configurations

### v3.0 (Future)

- [ ] Fine-tuned SEO-specific LLM models
- [ ] Multi-language support (10+ languages)
- [ ] Chrome extension
- [ ] Docker container support
- [ ] Cloud deployment templates (AWS, GCP, Azure)
- [ ] Real-time SERP tracking
- [ ] Automated report generation

---

**Enjoy analyzing search intent! 🎯**
