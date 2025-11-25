# LLM-Based Search Intent Analyzer

## 🚀 Quick Start Guide

This guide will help you set up and run the **LLM-powered Search Intent Analyzer** using **Ollama** for local, privacy-focused analysis.

---

## 📋 Prerequisites

- **macOS** (Intel or Apple Silicon)
- **Python 3.8+**
- **Homebrew** (for installing Ollama)

---

## 🔧 Installation

### Step 1: Install Ollama

```bash
# Install Ollama using Homebrew
brew install ollama
```

### Step 2: Start Ollama Server

```bash
# Start the Ollama service
ollama serve
```

**Note:** Keep this terminal window open. Ollama must be running for the analyzer to work.

### Step 3: Pull the LLM Model

Open a **new terminal** and run:

```bash
# Pull the recommended model (llama3.2:3b - ~2GB)
ollama pull llama3.2:3b
```

**Alternative models:**
```bash
# Smaller, faster model (~1GB)
ollama pull llama3.2:1b

# Larger, more accurate model (~4.7GB)
ollama pull llama3.1:8b

# Mistral model (~4.1GB)
ollama pull mistral:7b

# Microsoft Phi-3 (~2.3GB)
ollama pull phi3:mini
```

### Step 4: Verify Installation

```bash
# List all downloaded models
ollama list
```

You should see your downloaded model(s) listed.

### Step 5: Install Python Dependencies

```bash
# Navigate to project directory
cd /path/to/search-intent-analyzer-python

# Install requirements
pip install -r requirements.txt
```

---

## 🎯 Running the App

### Method 1: Run the LLM-based App

```bash
# Start the Streamlit app
streamlit run src/app_llm.py
```

The app will open in your browser at `http://localhost:8501`

### Method 2: Test the Analyzer Directly

```bash
# Run the analyzer test script
python -m src.services.llm_intent_analyzer
```

---

## 🧪 Testing with Sample Queries

Once the app is running:

1. Click **"📋 Load Examples"** button
2. Click **"🚀 Run Analysis"**
3. View results in the **Results** tab

Or enter your own queries like:
```
how to train a dog
buy iPhone 15 pro
amazon login
best laptops 2024 comparison
```

---

## 🎨 Features

### ✅ What's New in LLM Version

- **No API Keys Required** - 100% local processing
- **Privacy First** - Your data never leaves your machine
- **No Firecrawl Dependency** - No need for external search API
- **Detailed Reasoning** - LLM explains why it chose each intent
- **Confidence Scores** - Get scores for ALL four intent categories
- **Fast Processing** - Analyze queries in seconds
- **Batch Support** - Process up to 100 queries at once

### 🔍 Supported Intent Categories

1. **Informational** - How-to guides, tutorials, definitions
2. **Transactional** - Buy, download, subscribe, book
3. **Navigational** - Brand searches, login pages, official sites
4. **Commercial Investigation** - Reviews, comparisons, "best" searches

---

## ⚙️ Configuration

### Model Selection

In the sidebar, you can choose different models:

- `llama3.2:3b` ⭐ **Recommended** - Best balance of speed and accuracy
- `llama3.2:1b` - Fastest, good for testing
- `llama3.1:8b` - Most accurate, slower
- `mistral:7b` - Alternative option
- `phi3:mini` - Microsoft's compact model

### Performance Tips

**For faster analysis:**
- Use `llama3.2:1b` or `llama3.2:3b`
- Reduce batch size

**For higher accuracy:**
- Use `llama3.1:8b` or `mistral:7b`
- Ensure Ollama is the only heavy process running

---

## 🐛 Troubleshooting

### Issue: "Cannot connect to Ollama"

**Solution:**
```bash
# Check if Ollama is running
ps aux | grep ollama

# If not running, start it
ollama serve
```

### Issue: "Model not found"

**Solution:**
```bash
# Pull the model
ollama pull llama3.2:3b

# Verify it's installed
ollama list
```

### Issue: Slow performance

**Solution:**
- Use a smaller model (`llama3.2:1b`)
- Close other applications
- On Apple Silicon, ensure Rosetta is not being used

### Issue: Timeout errors

**Solution:**
- Increase timeout in `llm_intent_analyzer.py`:
```python
# Change line in _call_ollama method:
timeout=60  # Increase to 120 for slower machines
```

---

## 📊 Understanding Results

### Confidence Score

- **80-100%** - Very clear intent
- **60-79%** - Clear intent
- **40-59%** - Moderate confidence (mixed intent likely)
- **0-39%** - Unclear intent

### Reasoning Field

The LLM provides a brief explanation of why it chose the intent. This helps you understand the analysis.

### Score Breakdown

Each query gets scores for all 4 intents, normalized to sum to 100%.

---

## 🆚 Comparison: Old vs New

| Feature | Old (Firecrawl) | New (LLM) |
|---------|----------------|-----------|
| **API Key Required** | ✅ Yes | ❌ No |
| **Privacy** | Data sent to API | 100% Local |
| **Cost** | Pay per request | Free |
| **Speed** | Depends on API | Fast (local) |
| **Setup** | Simple | Requires Ollama |
| **Reasoning** | No | ✅ Yes |
| **SERP Analysis** | ✅ Yes | ❌ No |
| **Accuracy** | High (with SERP) | High (LLM-based) |

---

## 💡 Advanced Usage

### Custom Model Training

You can use Ollama with custom models:

```bash
# Create a Modelfile
echo "FROM llama3.2:3b" > Modelfile
echo "SYSTEM You are an SEO expert..." >> Modelfile

# Create custom model
ollama create my-custom-model -f Modelfile
```

Then select your custom model in the app.

### Batch Processing via CLI

```python
from src.services.llm_intent_analyzer import LLMIntentAnalyzer

# Initialize
analyzer = LLMIntentAnalyzer(model="llama3.2:3b")

# Analyze multiple queries
queries = ["how to code", "buy laptop", "google login"]
results = analyzer.analyze_batch(queries)

# Process results
for result in results:
    print(f"{result.primary_intent}: {result.confidence}%")
```

---

## 📚 Resources

- **Ollama Documentation**: https://ollama.ai/
- **Available Models**: https://ollama.ai/library
- **Streamlit Docs**: https://docs.streamlit.io/

---

## 🤝 Support

For issues or questions:
1. Check this README
2. Review the troubleshooting section
3. Open an issue on GitHub

---

## 📄 License

MIT License - See LICENSE file for details

---

## 👨‍💻 Author

**Knovik • Madusanka Premaratne & Deelaka Kariyawasam**

© 2024 Knovik LLC
