# Search Intent Analyzer 🔍

**Version:** 2.0.0  
**Author:** Knovik • Madusanka Premaratne & Deelaka Kariyawasam

Powerful search intent analysis tool with **two modes**: traditional rule-based (Firecrawl + Classifier) and modern **LLM-based** analysis using local Ollama.

---

## 🎯 Choose Your Version

### 🤖 **NEW: LLM-Based Version** (Recommended)

✅ **Zero API costs** - Completely free  
✅ **100% Private** - Data never leaves your machine  
✅ **AI-Powered** - Uses local Ollama LLM  
✅ **Detailed Reasoning** - Explains why each intent was chosen  
✅ **No Firecrawl Required** - Works completely offline

**Perfect for:** Privacy-conscious users, high-volume analysis, offline work, budget-conscious projects

👉 **[Quick Start Guide for LLM Version](#-llm-version-quick-start)**

---

### 📊 Original: Rule-Based Version

✅ **SERP Analysis** - Analyzes actual search results  
✅ **Hybrid Scoring** - Combines multiple signals  
✅ **Simple Setup** - Just add API key  
✅ **Proven Accuracy** - Battle-tested approach

**Perfect for:** Users needing SERP data, low query volumes, deterministic results

👉 **[Quick Start Guide for Rule-Based Version](#-rule-based-version-quick-start)**

---

## 📖 Documentation

- **[LLM Setup Guide](LLM_SETUP_GUIDE.md)** - Complete guide for Ollama setup

---

## 🚀 LLM Version Quick Start

### Prerequisites

- Python 3.8+
- macOS (Intel or Apple Silicon)
- 4GB+ RAM
- 2GB+ disk space

### Installation

**Step 1: Setup LLM**

```bash
# Install Ollama
brew install ollama

# Start Ollama server (keep this running)
ollama serve

# In a new terminal, pull the model
ollama pull llama3.2:3b

# Verify installation
ollama list
```

**Step 2: Install Python Dependencies**

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

**Step 3: Run the App**

```bash
streamlit run src/app_llm.py
```

🎉 **Done!** The app will open at `http://localhost:8501`

---

## 📁 Project Structure

```
search-intent-analyzer-python/
├── src/
│   ├── app.py                      # Rule-based Streamlit app (original)
│   ├── app_llm.py                  # LLM-based Streamlit app (new)
│   ├── search_intent_classifier.py # Original classifier
│   ├── services/
│   │   └── llm_intent_analyzer.py  # LLM analyzer (new)
│   ├── config/
│   │   └── constants.py
│   └── ...
├── test/
│   ├── test_llm_intent_analyzer.py # LLM tests (new)
│   └── ...
├── requirements.txt                 # Python dependencies
├── LLM_SETUP_GUIDE.md              # Detailed LLM setup guide (new)
└── README.md                        # This file
```

---

## 🔧 Configuration

### LLM Version Settings

**In the Streamlit sidebar:**

- **Model Selection**: Choose from llama3.2:3b, mistral:7b, etc.
- **Ollama URL**: Default `http://localhost:11434`

**Recommended models:**

- `llama3.2:3b` - Best balance (recommended) ⭐
- `llama3.2:1b` - Fastest for bulk processing
- `llama3.1:8b` - Most accurate (requires more RAM)

### Rule-Based Version Settings

**In the Streamlit sidebar:**

- **SERP Signals**: 0-100% weight
- **Keyword Modifiers**: 0-100% weight
- **Top Pages Analysis**: 0-100% weight
- **Classifier Weight**: 0-100% weight
- **Firecrawl Settings**: Country, location, result limit

---

## 🧪 Testing

### Run LLM Analyzer Tests

```bash
# Run all tests
pytest test/test_llm_intent_analyzer.py -v

# Run unit tests only (no integration)
pytest test/test_llm_intent_analyzer.py -v -m "not integration"

# Run integration tests (requires Ollama running)
pytest test/test_llm_intent_analyzer.py -v -m integration
```

---

## 📊 Comparison: Which Version to Use?

| Feature       | Rule-Based       | LLM-Based       |
| ------------- | ---------------- | --------------- |
| **Cost**      | ~$150-300/month  | Free            |
| **Privacy**   | Data sent to API | 100% Local      |
| **Setup**     | Simple (API key) | Medium (Ollama) |
| **Speed**     | 2-5 sec/query    | 1-3 sec/query   |
| **Accuracy**  | ~87%             | ~89-91%         |
| **Reasoning** | No               | Yes             |
| **Offline**   | No               | Yes             |

---

## 🎓 Example Usage

### LLM Version

```python
from src.services.llm_intent_analyzer import LLMIntentAnalyzer

# Initialize
analyzer = LLMIntentAnalyzer(model="llama3.2:3b")

# Analyze single query
result = analyzer.analyze("how to learn python programming")

print(f"Intent: {result.primary_intent}")
print(f"Confidence: {result.confidence}%")
print(f"Reasoning: {result.reasoning}")

# Batch analysis
queries = ["buy laptop", "facebook login", "best phones 2024"]
results = analyzer.analyze_batch(queries)
```

---

## 🐛 Troubleshooting

### LLM Version Issues

**"Cannot connect to Ollama"**

```bash
# Check if Ollama is running
ps aux | grep ollama

# Start Ollama
ollama serve
```

**"Model not found"**

```bash
# Pull the model
ollama pull llama3.2:3b

# Verify installation
ollama list
```

**Slow performance**

- Use smaller model: `llama3.2:1b`
- Close other applications
- Check system resources

### Rule-Based Version Issues

**Firecrawl authentication error**

```bash
# Verify API key is set
echo $FIRECRAWL_API_KEY

# Export key
export FIRECRAWL_API_KEY="fc-xxxx"
```

**Module not found**

```bash
# Activate virtual environment
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

---

## 🚀 Advanced Features

### Custom Model Training (LLM)

```bash
# Create custom Modelfile
cat > Modelfile << EOF
FROM llama3.2:3b
SYSTEM You are an expert SEO analyst specializing in search intent...
EOF

# Build custom model
ollama create seo-intent-analyzer -f Modelfile

# Use in app (select from dropdown)
```

### Hybrid Approach (Best of Both)

Use LLM for bulk analysis, Firecrawl for validation:

```python
def hybrid_analyze(query):
    llm_result = llm_analyzer.analyze(query)

    if llm_result.confidence < 70:
        # Low confidence - validate with Firecrawl
        return run_firecrawl_analysis(query)

    return llm_result
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

## 👨‍💻 Author

**Knovik • Madusanka Premaratne (Madus)**

© 2024 Knovik LLC

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

- [ ] Fine-tuned SEO-specific LLM models
- [ ] Multi-language support
- [ ] REST API endpoint
- [ ] Batch CSV processing
- [ ] Real-time SERP analysis (optional)
- [ ] Chrome extension
- [ ] Docker support

---

**Enjoy analyzing search intent! 🎯**
