# llm_intent_analyzer.py — Local LLM-based Search Intent Analysis
# Version: 2.0.0
# Author: Knovik • Madusanka Premaratne (Madus)
# Co-authors: Knovik Engineering Team

import json
import re
from typing import Dict
from dataclasses import dataclass


@dataclass
class IntentResult:
    """Data class for intent analysis results."""

    primary_intent: str
    secondary_intent: str
    confidence: float
    reasoning: str
    all_scores: Dict[str, float]


class LLMIntentAnalyzer:
    """
    Local LLM-based search intent analyzer using Ollama.
    Replaces rule-based scoring with AI-powered analysis.
    """

    INTENTS = [
        "Informational",
        "Transactional",
        "Navigational",
        "Commercial Investigation",
    ]

    def __init__(
        self, model: str = "llama3.2:3b", base_url: str = "http://localhost:11434"
    ):
        """
        Initialize the LLM Intent Analyzer.

        Args:
            model: Ollama model name (default: llama3.2:3b)
            base_url: Ollama API endpoint
        """
        self.model = model
        self.base_url = base_url
        self._check_ollama_connection()

    def _check_ollama_connection(self) -> bool:
        """Check if Ollama is running and accessible."""
        try:
            import requests

            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                return True
        except Exception as e:
            raise ConnectionError(
                f"Cannot connect to Ollama at {self.base_url}. "
                f"Please ensure Ollama is installed and running.\n"
                f"Install: brew install ollama\n"
                f"Run: ollama serve\n"
                f"Pull model: ollama pull {self.model}\n"
                f"Error: {str(e)}"
            )
        return False

    def _create_prompt(self, query: str) -> str:
        """
        Create a detailed prompt for the LLM to analyze search intent.

        Args:
            query: The search query to analyze

        Returns:
            Formatted prompt string
        """
        prompt = f"""You are an expert SEO analyst specializing in search intent classification. Analyze the following search query and determine the user's search intent.
        **Search Query:** "{query}"
        **Intent Categories:**

            1. **Informational**: User seeks knowledge, answers, guides, tutorials, definitions, or how-to content.
                - Examples: "how to tie a tie", "what is machine learning", "python tutorial"

            2. **Transactional**: User intends to complete an action like buying, downloading, subscribing, or booking.
                - Examples: "buy iPhone 15", "download spotify premium", "book hotel NYC"

            3. **Navigational**: User wants to find a specific website, brand page, or login portal.
                - Examples: "facebook login", "amazon official site", "netflix homepage"

            4. **Commercial Investigation**: User is researching before making a purchase decision (comparisons, reviews, best options).
                - Examples: "best laptops 2024", "iPhone vs Samsung", "Nike shoes review"

            **Instructions:**
                1. Analyze the query carefully considering keywords, structure, and implied user intent
                2. Assign a primary intent (most likely)
                3. Assign a secondary intent (next most likely)
                4. Provide confidence scores (0-100) for ALL four intents
                5. Explain your reasoning in 1-2 sentences

                **Output Format (JSON only, no other text):**
                {{
                    "primary_intent": "Intent Name",
                    "secondary_intent": "Intent Name",
                    "confidence_scores": {{
                    "Informational": 25,
                    "Transactional": 60,
                    "Navigational": 5,
                    "Commercial Investigation": 10
                }},
                "reasoning": "Brief explanation of why this intent was chosen"
        }}

        **Important:** Respond ONLY with the JSON object, nothing else."""

        return prompt

    def _call_ollama(self, prompt: str) -> str:
        """
        Make API call to Ollama.

        Args:
            prompt: The prompt to send to the LLM

        Returns:
            Raw response from the LLM
        """
        import requests

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,  # Lower temperature for more consistent results
                "top_p": 0.9,
                "top_k": 40,
            },
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/generate", json=payload, timeout=30
            )
            response.raise_for_status()

            result = response.json()
            return result.get("response", "")

        except requests.exceptions.Timeout:
            raise TimeoutError(f"Ollama request timed out for model {self.model}")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ollama API error: {str(e)}")

    def _parse_llm_response(self, response: str, query: str) -> IntentResult:
        """
        Parse the LLM response and extract intent data.

        Args:
            response: Raw LLM response
            query: Original search query (for fallback)

        Returns:
            IntentResult object
        """
        try:
            # Extract JSON from response (in case LLM adds extra text)
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
            else:
                data = json.loads(response)

            # Extract fields
            primary = data.get("primary_intent", "Informational")
            secondary = data.get("secondary_intent", "Transactional")
            scores = data.get("confidence_scores", {})
            reasoning = data.get("reasoning", "Analysis completed")

            # Validate intents
            if primary not in self.INTENTS:
                primary = "Informational"
            if secondary not in self.INTENTS or secondary == primary:
                secondary = [i for i in self.INTENTS if i != primary][0]

            # Normalize scores to sum to 100
            total = sum(scores.values()) or 1
            normalized_scores = {k: (v / total) * 100 for k, v in scores.items()}

            # Ensure all intents have scores
            for intent in self.INTENTS:
                if intent not in normalized_scores:
                    normalized_scores[intent] = 0.0

            # Calculate confidence (primary intent score)
            confidence = normalized_scores.get(primary, 0.0)

            return IntentResult(
                primary_intent=primary,
                secondary_intent=secondary,
                confidence=round(confidence, 1),
                reasoning=reasoning,
                all_scores=normalized_scores,
            )

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Fallback to basic keyword matching if LLM response is malformed
            return self._fallback_analysis(query, error=str(e))

    def _fallback_analysis(self, query: str, error: str = "") -> IntentResult:
        """
        Fallback analysis using simple keyword matching if LLM fails.

        Args:
            query: Search query
            error: Error message from LLM parsing

        Returns:
            IntentResult with basic analysis
        """
        query_lower = query.lower()
        scores = {intent: 0.0 for intent in self.INTENTS}

        # Simple keyword matching
        if any(
            word in query_lower
            for word in ["how", "what", "why", "guide", "tutorial", "learn"]
        ):
            scores["Informational"] = 60
        elif any(
            word in query_lower
            for word in ["buy", "price", "order", "download", "book"]
        ):
            scores["Transactional"] = 60
        elif any(
            word in query_lower for word in ["login", "official", "homepage", "site"]
        ):
            scores["Navigational"] = 60
        elif any(
            word in query_lower for word in ["best", "top", "vs", "review", "compare"]
        ):
            scores["Commercial Investigation"] = 60
        else:
            scores["Informational"] = 40  # Default

        # Distribute remaining scores
        total = sum(scores.values())
        if total < 100:
            remaining = 100 - total
            for intent in self.INTENTS:
                if scores[intent] == 0:
                    scores[intent] = remaining / (len(self.INTENTS) - 1)

        primary = max(scores, key=scores.get)
        secondary = sorted(
            [k for k in scores if k != primary], key=lambda x: scores[x], reverse=True
        )[0]

        return IntentResult(
            primary_intent=primary,
            secondary_intent=secondary,
            confidence=round(scores[primary], 1),
            reasoning=(
                f"Fallback analysis (LLM error: {error[:50]})"
                if error
                else "Basic keyword analysis"
            ),
            all_scores=scores,
        )

    def analyze(self, query: str) -> IntentResult:
        """
        Analyze search intent for a given query using local LLM.

        Args:
            query: The search query to analyze

        Returns:
            IntentResult containing primary/secondary intents, confidence, and reasoning
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        prompt = self._create_prompt(query.strip())

        try:
            response = self._call_ollama(prompt)
            result = self._parse_llm_response(response, query)
            return result

        except Exception as e:
            # Use fallback if LLM fails
            print(f"Warning: LLM analysis failed for '{query}': {str(e)}")
            return self._fallback_analysis(query, error=str(e))

    def analyze_batch(self, queries: list) -> list:
        """
        Analyze multiple queries in batch.

        Args:
            queries: List of search queries

        Returns:
            List of IntentResult objects
        """
        results = []
        for query in queries:
            try:
                result = self.analyze(query)
                results.append(result)
            except Exception as e:
                # Add error result
                results.append(
                    IntentResult(
                        primary_intent="Error",
                        secondary_intent="Error",
                        confidence=0.0,
                        reasoning=f"Analysis failed: {str(e)}",
                        all_scores={intent: 0.0 for intent in self.INTENTS},
                    )
                )
        return results


# Utility function for quick testing
def quick_test(query: str, model: str = "llama3.2:3b"):
    """Quick test function for the analyzer."""
    analyzer = LLMIntentAnalyzer(model=model)
    result = analyzer.analyze(query)

    print(f"\n🔍 Query: {query}")
    print(f"✅ Primary Intent: {result.primary_intent}")
    print(f"📊 Confidence: {result.confidence}%")
    print(f"💭 Reasoning: {result.reasoning}")
    print(f"\n📈 All Scores:")
    for intent, score in result.all_scores.items():
        print(f"   {intent}: {score:.1f}%")


if __name__ == "__main__":
    # Test the analyzer
    test_queries = [
        "how to train a dog",
        "buy iPhone 15 pro",
        "amazon login",
        "best laptops 2024 comparison",
    ]

    print("=" * 60)
    print("LLM Intent Analyzer - Test Suite")
    print("=" * 60)

    for query in test_queries:
        quick_test(query)
        print("-" * 60)
