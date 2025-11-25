# test_llm_intent_analyzer.py — Unit Tests for LLM Intent Analyzer
# Version: 2.0.0
# Author: Knovik • Madusanka Premaratne & Deelaka Kariyawasam

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import pytest
import json
from unittest.mock import Mock, patch
from src.services.llm_intent_analyzer import LLMIntentAnalyzer, IntentResult


class TestLLMIntentAnalyzer:
    """Test suite for LLM Intent Analyzer."""

    @pytest.fixture
    def mock_ollama_response(self):
        """Mock successful Ollama API response."""
        return {
            "response": json.dumps(
                {
                    "primary_intent": "Informational",
                    "secondary_intent": "Transactional",
                    "confidence_scores": {
                        "Informational": 70,
                        "Transactional": 15,
                        "Navigational": 5,
                        "Commercial Investigation": 10,
                    },
                    "reasoning": "Query contains 'how to' indicating informational intent",
                }
            )
        }

    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance with mocked connection check."""
        with patch.object(
            LLMIntentAnalyzer, "_check_ollama_connection", return_value=True
        ):
            return LLMIntentAnalyzer(model="llama3.2:3b")

    def test_initialization(self):
        """Test analyzer initialization."""
        with patch.object(
            LLMIntentAnalyzer, "_check_ollama_connection", return_value=True
        ):
            analyzer = LLMIntentAnalyzer(model="llama3.2:3b")
            assert analyzer.model == "llama3.2:3b"
            assert analyzer.base_url == "http://localhost:11434"

    def test_create_prompt(self, analyzer):
        """Test prompt creation."""
        query = "how to train a dog"
        prompt = analyzer._create_prompt(query)

        assert query in prompt
        assert "Informational" in prompt
        assert "Transactional" in prompt
        assert "Navigational" in prompt
        assert "Commercial Investigation" in prompt
        assert "JSON" in prompt

    @patch("requests.post")
    def test_call_ollama_success(self, mock_post, analyzer, mock_ollama_response):
        """Test successful Ollama API call."""
        mock_post.return_value.json.return_value = mock_ollama_response
        mock_post.return_value.raise_for_status = Mock()

        prompt = "Test prompt"
        response = analyzer._call_ollama(prompt)

        assert isinstance(response, str)
        assert "primary_intent" in response

    @patch("requests.post")
    def test_call_ollama_timeout(self, mock_post, analyzer):
        """Test Ollama API timeout handling."""
        import requests

        mock_post.side_effect = requests.exceptions.Timeout()

        with pytest.raises(TimeoutError):
            analyzer._call_ollama("test prompt")

    def test_parse_llm_response_success(self, analyzer):
        """Test parsing valid LLM response."""
        response = json.dumps(
            {
                "primary_intent": "Transactional",
                "secondary_intent": "Commercial Investigation",
                "confidence_scores": {
                    "Informational": 10,
                    "Transactional": 75,
                    "Navigational": 5,
                    "Commercial Investigation": 10,
                },
                "reasoning": "User wants to buy something",
            }
        )

        result = analyzer._parse_llm_response(response, "buy laptop")

        assert isinstance(result, IntentResult)
        assert result.primary_intent == "Transactional"
        assert result.secondary_intent == "Commercial Investigation"
        assert result.confidence > 0
        assert "buy something" in result.reasoning.lower()

    def test_parse_llm_response_with_extra_text(self, analyzer):
        """Test parsing response with extra text around JSON."""
        response = """Here's the analysis:
        {
            "primary_intent": "Navigational",
            "secondary_intent": "Informational",
            "confidence_scores": {
                "Informational": 20,
                "Transactional": 5,
                "Navigational": 70,
                "Commercial Investigation": 5
            },
            "reasoning": "User looking for specific website"
        }
        Hope this helps!"""

        result = analyzer._parse_llm_response(response, "amazon login")

        assert result.primary_intent == "Navigational"
        assert result.confidence > 0

    def test_parse_llm_response_malformed(self, analyzer):
        """Test fallback when response is malformed."""
        response = "This is not JSON at all!"

        result = analyzer._parse_llm_response(response, "how to code")

        assert isinstance(result, IntentResult)
        assert result.primary_intent in analyzer.INTENTS
        assert (
            "fallback" in result.reasoning.lower()
            or "basic" in result.reasoning.lower()
        )

    def test_fallback_analysis_informational(self, analyzer):
        """Test fallback analysis for informational query."""
        result = analyzer._fallback_analysis("how to train a dog")

        assert result.primary_intent == "Informational"
        assert result.confidence > 0
        assert sum(result.all_scores.values()) == pytest.approx(100.0, rel=0.1)

    def test_fallback_analysis_transactional(self, analyzer):
        """Test fallback analysis for transactional query."""
        result = analyzer._fallback_analysis("buy iPhone 15 pro")

        assert result.primary_intent == "Transactional"
        assert result.confidence > 0

    def test_fallback_analysis_navigational(self, analyzer):
        """Test fallback analysis for navigational query."""
        result = analyzer._fallback_analysis("facebook login")

        assert result.primary_intent == "Navigational"
        assert result.confidence > 0

    def test_fallback_analysis_commercial(self, analyzer):
        """Test fallback analysis for commercial query."""
        result = analyzer._fallback_analysis("best laptops 2024")

        assert result.primary_intent == "Commercial Investigation"
        assert result.confidence > 0

    @patch.object(LLMIntentAnalyzer, "_call_ollama")
    def test_analyze_success(self, mock_call, analyzer, mock_ollama_response):
        """Test successful query analysis."""
        mock_call.return_value = mock_ollama_response["response"]

        result = analyzer.analyze("how to learn python")

        assert isinstance(result, IntentResult)
        assert result.primary_intent in analyzer.INTENTS
        assert result.secondary_intent in analyzer.INTENTS
        assert result.primary_intent != result.secondary_intent
        assert 0 <= result.confidence <= 100

    def test_analyze_empty_query(self, analyzer):
        """Test analysis with empty query."""
        with pytest.raises(ValueError):
            analyzer.analyze("")

    @patch.object(LLMIntentAnalyzer, "_call_ollama")
    def test_analyze_with_failure(self, mock_call, analyzer):
        """Test analysis falls back on LLM failure."""
        mock_call.side_effect = Exception("LLM error")

        result = analyzer.analyze("test query")

        # Should use fallback
        assert isinstance(result, IntentResult)
        assert result.primary_intent in analyzer.INTENTS

    @patch.object(LLMIntentAnalyzer, "analyze")
    def test_analyze_batch(self, mock_analyze, analyzer):
        """Test batch analysis."""
        mock_analyze.return_value = IntentResult(
            primary_intent="Informational",
            secondary_intent="Transactional",
            confidence=85.0,
            reasoning="Test",
            all_scores={
                "Informational": 85,
                "Transactional": 10,
                "Navigational": 3,
                "Commercial Investigation": 2,
            },
        )

        queries = ["query1", "query2", "query3"]
        results = analyzer.analyze_batch(queries)

        assert len(results) == 3
        assert all(isinstance(r, IntentResult) for r in results)

    def test_score_normalization(self, analyzer):
        """Test that scores are normalized to 100%."""
        response = json.dumps(
            {
                "primary_intent": "Informational",
                "secondary_intent": "Transactional",
                "confidence_scores": {
                    "Informational": 50,
                    "Transactional": 30,
                    "Navigational": 15,
                    "Commercial Investigation": 5,
                },
                "reasoning": "Test",
            }
        )

        result = analyzer._parse_llm_response(response, "test")
        total = sum(result.all_scores.values())

        assert total == pytest.approx(100.0, rel=0.01)

    def test_all_intents_have_scores(self, analyzer):
        """Test that all intents receive scores."""
        response = json.dumps(
            {
                "primary_intent": "Informational",
                "secondary_intent": "Transactional",
                "confidence_scores": {
                    "Informational": 80,
                    "Transactional": 20,
                    # Missing Navigational and Commercial Investigation
                },
                "reasoning": "Test",
            }
        )

        result = analyzer._parse_llm_response(response, "test")

        for intent in analyzer.INTENTS:
            assert intent in result.all_scores
            assert result.all_scores[intent] >= 0


class TestIntentResult:
    """Test IntentResult data class."""

    def test_intent_result_creation(self):
        """Test creating IntentResult instance."""
        result = IntentResult(
            primary_intent="Informational",
            secondary_intent="Transactional",
            confidence=85.5,
            reasoning="Test reasoning",
            all_scores={
                "Informational": 85.5,
                "Transactional": 10.0,
                "Navigational": 2.5,
                "Commercial Investigation": 2.0,
            },
        )

        assert result.primary_intent == "Informational"
        assert result.secondary_intent == "Transactional"
        assert result.confidence == 85.5
        assert result.reasoning == "Test reasoning"
        assert len(result.all_scores) == 4


# Integration-style tests (require Ollama running)
class TestLLMIntentAnalyzerIntegration:
    """Integration tests - only run if Ollama is available."""

    @pytest.mark.integration
    def test_real_ollama_connection(self):
        """Test real connection to Ollama (requires Ollama running)."""
        try:
            analyzer = LLMIntentAnalyzer(model="llama3.2:3b")
            assert analyzer is not None
        except ConnectionError:
            pytest.skip("Ollama not running")

    @pytest.mark.integration
    def test_real_analysis(self):
        """Test real query analysis (requires Ollama running)."""
        try:
            analyzer = LLMIntentAnalyzer(model="llama3.2:3b")
            result = analyzer.analyze("how to learn python programming")

            assert isinstance(result, IntentResult)
            assert result.primary_intent in analyzer.INTENTS
            assert result.confidence > 0
        except ConnectionError:
            pytest.skip("Ollama not running")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
