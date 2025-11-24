"""
Hybrid Intent Analyzer - Combines Firecrawl SERP data with Ollama LLM reasoning
Version: 2.0.0
Author: Knovik • Deelaka Kariyawasam

This module provides the most accurate intent classification by combining:
1. Firecrawl API - Real SERP data from Google
2. Ollama LLM - AI-powered semantic reasoning
3. Keyword patterns - Rule-based analysis

Hybrid approach benefits:
- Firecrawl provides actual search results and SERP features
- Ollama LLM provides semantic understanding and reasoning
- Keyword patterns catch obvious signals
- Combined scoring increases accuracy
"""

from typing import Dict, List
from dataclasses import dataclass, field
from enum import Enum
import requests
import re

from .llm_intent_analyzer import LLMIntentAnalyzer


class IntentConfidence(Enum):
    """Confidence level for intent classification."""

    VERY_HIGH = "Very High"  # 85-100%
    HIGH = "High"  # 70-84%
    MEDIUM = "Medium"  # 50-69%
    LOW = "Low"  # 0-49%


@dataclass
class HybridIntentResult:
    """Result from hybrid intent analysis."""

    keyword: str
    primary_intent: str
    secondary_intent: str
    confidence_score: float
    confidence_level: IntentConfidence
    all_intent_scores: Dict[str, float] = field(default_factory=dict)

    # LLM signals
    llm_reasoning: str = ""
    llm_confidence: float = 0.0
    llm_primary_intent: str = ""

    # Firecrawl signals
    firecrawl_used: bool = False
    firecrawl_results_count: int = 0
    serp_features: List[str] = field(default_factory=list)
    dominant_content_type: str = "general"

    # Keyword signals
    keyword_scores: Dict[str, float] = field(default_factory=dict)

    # Analysis metadata
    is_mixed_intent: bool = False
    reasoning: str = ""


class KeywordAnalyzer:
    """Analyzes keywords for intent patterns using regex."""

    # Compile regex patterns once at class level for better performance
    _PATTERNS = {
        "Informational": re.compile(
            r"\b(how\s+to|what\s+(?:is|are|does)|why|guide|tutorial|learn|explain|steps|tips)\b",
            re.IGNORECASE,
        ),
        "Transactional": re.compile(
            r"\b(buy|purchase|order|coupon|price|cheap|deal|sale|shop|affordable|discount)\b",
            re.IGNORECASE,
        ),
        "Navigational": re.compile(
            r"\b(login|sign\s+in|account|download|official\s+site|homepage|website)\b",
            re.IGNORECASE,
        ),
        "Commercial Investigation": re.compile(
            r"\b(best|top|review|compare|vs|alternative|option|versus)\b", re.IGNORECASE
        ),
    }

    _SCORE_PER_MATCH = 25
    _DEFAULT_SCORE = 50

    def analyze(self, keyword: str) -> Dict[str, float]:
        """
        Analyze keyword for intent patterns using compiled regex.

        Returns:
            Intent scores (0-100)
        """
        scores = {intent: 0.0 for intent in self._PATTERNS.keys()}

        # Check each pattern (each match adds score)
        for intent, pattern in self._PATTERNS.items():
            matches = pattern.findall(keyword)
            if matches:
                scores[intent] += self._SCORE_PER_MATCH

        # Default to informational if no patterns match
        if not any(scores.values()):
            scores["Informational"] = self._DEFAULT_SCORE

        # Normalize to 100
        total = sum(scores.values())
        return {k: (v / total) * 100 for k, v in scores.items()}


class FirecrawlSERPAnalyzer:
    """Analyzes SERP features from Firecrawl results."""

    # Define keyword sets for faster lookups
    _INFORMATIONAL_KEYWORDS = frozenset(["how to", "guide", "tutorial", "what is"])
    _TRANSACTIONAL_KEYWORDS = frozenset(["buy", "price", "shop", "order"])
    _COMMERCIAL_KEYWORDS = frozenset(["review", "best", "vs", "compare"])
    _NAVIGATIONAL_KEYWORDS = frozenset(["login", "sign in", "official"])
    _PAA_KEYWORDS = frozenset(["people also ask", "related questions"])

    def analyze_serp_features(
        self, firecrawl_results: List[Dict]
    ) -> tuple[List[str], Dict[str, float]]:
        """
        Analyze SERP features and return intent signals.

        Returns:
            (features_list, intent_scores)
        """
        features = set()
        content_types = []

        for result in firecrawl_results:
            title_snippet = (
                f"{result.get('title', '')} {result.get('description', '')}".lower()
            )
            markdown = result.get("markdown", "").lower()

            # Detect content types using set intersection
            if any(kw in title_snippet for kw in self._INFORMATIONAL_KEYWORDS):
                content_types.append("informational")
            if any(kw in title_snippet for kw in self._TRANSACTIONAL_KEYWORDS):
                content_types.append("transactional")
            if any(kw in title_snippet for kw in self._COMMERCIAL_KEYWORDS):
                content_types.append("commercial")
            if any(kw in title_snippet for kw in self._NAVIGATIONAL_KEYWORDS):
                content_types.append("navigational")

            # Detect SERP features
            if markdown.count("?") > 3:
                features.add("FAQ")
            if any(kw in markdown for kw in self._PAA_KEYWORDS):
                features.add("People Also Ask")
            if "$" in markdown or "price" in markdown:
                features.add("Shopping")

        # Calculate intent scores from content types
        type_counts = {
            "Informational": content_types.count("informational"),
            "Transactional": content_types.count("transactional"),
            "Commercial Investigation": content_types.count("commercial"),
            "Navigational": content_types.count("navigational"),
        }

        total = sum(type_counts.values()) or 1
        intent_scores = {k: (v / total) * 100 for k, v in type_counts.items()}

        return list(features), intent_scores


class FirecrawlService:
    """Service for fetching SERP data via Firecrawl API."""

    _DEFAULT_TIMEOUT = 60
    _MAX_RESULTS = 20

    def __init__(
        self, api_key: str, search_url: str = "https://api.firecrawl.dev/v1/search"
    ):
        self.api_key = api_key
        self.search_url = search_url
        # Reuse session for connection pooling
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
        )

    def search(self, query: str, limit: int = 10, country: str = "US") -> List[Dict]:
        """
        Search using Firecrawl API with connection pooling.

        Returns:
            List of search results with markdown and HTML content
        """
        if not self.api_key:
            raise ValueError("Firecrawl API key is required")

        payload = {
            "query": query,
            "limit": min(limit, self._MAX_RESULTS),
            "country": country,
            "sources": ["web"],
            "scrapeOptions": {
                "formats": ["markdown", "html"],
                "onlyMainContent": True,
            },
        }

        try:
            response = self._session.post(
                self.search_url, json=payload, timeout=self._DEFAULT_TIMEOUT
            )
            response.raise_for_status()
            return response.json().get("data", [])

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            error_msgs = {
                401: "❌ Firecrawl API Error: Invalid or expired API key (401 Unauthorized)\n   Please check your API key at firecrawl.dev",
                403: "❌ Firecrawl API Error: Forbidden (403) - Check your subscription plan",
                429: "⚠️  Firecrawl API Error: Rate limit exceeded (429) - Wait and retry",
                500: "⚠️  Firecrawl API Error: Server error (500) - Try again later",
            }
            print(error_msgs.get(status_code, f"⚠️  Firecrawl request failed: {str(e)}"))
            return []
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Firecrawl connection failed: {str(e)}")
            return []

    def __del__(self):
        """Clean up session on object destruction."""
        if hasattr(self, "_session"):
            self._session.close()


class HybridIntentAnalyzer:
    """
    Hybrid analyzer combining Firecrawl SERP data with Ollama LLM reasoning.

    Provides the most accurate intent classification by combining:
    - Keyword pattern matching (fast, rule-based)
    - Firecrawl SERP data (actual search results)
    - Ollama LLM semantic reasoning (AI-powered)
    """

    def __init__(
        self,
        firecrawl_api_key: str = "",
        llm_model: str = "llama3.2:3b",
        llm_base_url: str = "http://localhost:11434",
        firecrawl_weight: float = 0.40,
        llm_weight: float = 0.40,
        keyword_weight: float = 0.20,
    ):
        """
        Initialize Hybrid Intent Analyzer.

        Args:
            firecrawl_api_key: Firecrawl API key (optional)
            llm_model: Ollama model name
            llm_base_url: Ollama API endpoint
            firecrawl_weight: Weight for Firecrawl signals (0-1)
            llm_weight: Weight for LLM signals (0-1)
            keyword_weight: Weight for keyword signals (0-1)
        """
        # Normalize weights
        total = firecrawl_weight + llm_weight + keyword_weight
        self.firecrawl_weight = firecrawl_weight / total
        self.llm_weight = llm_weight / total
        self.keyword_weight = keyword_weight / total

        # Initialize services
        self.firecrawl = (
            FirecrawlService(firecrawl_api_key) if firecrawl_api_key else None
        )
        self.llm_analyzer = None  # Lazy init
        self.llm_model = llm_model
        self.llm_base_url = llm_base_url

        self.keyword_analyzer = KeywordAnalyzer()
        self.serp_analyzer = FirecrawlSERPAnalyzer()

    def _init_llm(self):
        """Lazy initialize LLM analyzer."""
        if self.llm_analyzer is None:
            try:
                self.llm_analyzer = LLMIntentAnalyzer(
                    model=self.llm_model, base_url=self.llm_base_url
                )
            except Exception as e:
                print(f"Warning: LLM initialization failed: {str(e)}")
                self.llm_analyzer = None

    def aggregate_scores(
        self,
        keyword_scores: Dict[str, float],
        firecrawl_scores: Dict[str, float] = None,
        llm_scores: Dict[str, float] = None,
    ) -> Dict[str, float]:
        """
        Aggregate scores from all signal sources with weighted averaging.

        Returns:
            Combined intent scores (0-100)
        """
        final_scores = {
            "Informational": 0.0,
            "Transactional": 0.0,
            "Navigational": 0.0,
            "Commercial Investigation": 0.0,
        }

        # Apply keyword scores
        for intent, score in keyword_scores.items():
            final_scores[intent] += score * self.keyword_weight

        # Apply Firecrawl SERP scores
        if firecrawl_scores:
            for intent, score in firecrawl_scores.items():
                final_scores[intent] += score * self.firecrawl_weight

        # Apply LLM scores
        if llm_scores:
            for intent, score in llm_scores.items():
                final_scores[intent] += score * self.llm_weight

        # Normalize to 100
        total = sum(final_scores.values()) or 1
        return {k: (v / total) * 100 for k, v in final_scores.items()}

    def analyze(
        self,
        keyword: str,
        use_firecrawl: bool = True,
        use_llm: bool = True,
        firecrawl_limit: int = 10,
        firecrawl_country: str = "US",
    ) -> HybridIntentResult:
        """
        Perform comprehensive hybrid intent analysis.

        Args:
            keyword: Search keyword to analyze
            use_firecrawl: Whether to fetch SERP via Firecrawl
            use_llm: Whether to use Ollama LLM reasoning
            firecrawl_limit: Number of Firecrawl results (max 20)
            firecrawl_country: Country code for Firecrawl search

        Returns:
            HybridIntentResult with complete analysis
        """
        # 1. Keyword pattern analysis (always run - fast and free)
        keyword_scores = self.keyword_analyzer.analyze(keyword)

        # 2. Firecrawl SERP analysis (if enabled and API key provided)
        firecrawl_scores = None
        firecrawl_used = False
        firecrawl_count = 0
        serp_features = []

        if use_firecrawl and self.firecrawl:
            try:
                fc_results = self.firecrawl.search(
                    keyword, limit=firecrawl_limit, country=firecrawl_country
                )

                if fc_results:
                    serp_features, firecrawl_scores = (
                        self.serp_analyzer.analyze_serp_features(fc_results)
                    )
                    firecrawl_used = True
                    firecrawl_count = len(fc_results)
                    print(f"✅ Firecrawl: Retrieved {firecrawl_count} results")
                else:
                    print(f"⚠️  Firecrawl: No results returned (check API key or query)")

            except Exception as e:
                print(f"⚠️  Firecrawl analysis failed: {str(e)}")

        # 3. LLM reasoning (if enabled)
        llm_scores = None
        llm_reasoning = ""
        llm_confidence = 0.0
        llm_primary = ""

        if use_llm:
            try:
                self._init_llm()
                if self.llm_analyzer:
                    llm_result = self.llm_analyzer.analyze(keyword)
                    llm_scores = llm_result.all_scores
                    llm_reasoning = llm_result.reasoning
                    llm_confidence = llm_result.confidence
                    llm_primary = llm_result.primary_intent
            except Exception as e:
                print(f"Warning: LLM analysis failed: {str(e)}")

        # 4. Aggregate all scores with weighted averaging
        final_scores = self.aggregate_scores(
            keyword_scores, firecrawl_scores, llm_scores
        )

        # 5. Determine primary/secondary intents
        sorted_intents = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
        primary, primary_score = sorted_intents[0]
        secondary, secondary_score = sorted_intents[1]

        # Check for mixed intent (more than 2 intents above 30%)
        is_mixed = sum(1 for score in final_scores.values() if score > 30) > 2

        # 6. Calculate confidence based on score gap
        confidence = min(
            100.0, primary_score + ((primary_score - secondary_score) * 0.5)
        )

        # Determine confidence level using threshold mapping
        if confidence >= 85:
            confidence_level = IntentConfidence.VERY_HIGH
        elif confidence >= 70:
            confidence_level = IntentConfidence.HIGH
        elif confidence >= 50:
            confidence_level = IntentConfidence.MEDIUM
        else:
            confidence_level = IntentConfidence.LOW

        # 7. Generate reasoning with compact list comprehension
        reasons = (
            [f"LLM: {llm_reasoning[:80]}" for _ in [1] if use_llm and llm_reasoning]
            + [
                f"analyzed {firecrawl_count} SERP results"
                for _ in [1]
                if firecrawl_used
            ]
            + [
                f"SERP features: {', '.join(serp_features[:3])}"
                for _ in [1]
                if serp_features
            ]
        )

        reasoning = f"Hybrid analysis classified as '{primary}'. " + (
            "; ".join(reasons) if reasons else "Based on keyword patterns."
        )

        # 8. Build result
        return HybridIntentResult(
            keyword=keyword,
            primary_intent=primary,
            secondary_intent=secondary,
            confidence_score=round(confidence, 1),
            confidence_level=confidence_level,
            all_intent_scores=final_scores,
            llm_reasoning=llm_reasoning,
            llm_confidence=llm_confidence,
            llm_primary_intent=llm_primary,
            firecrawl_used=firecrawl_used,
            firecrawl_results_count=firecrawl_count,
            serp_features=serp_features,
            keyword_scores=keyword_scores,
            is_mixed_intent=is_mixed,
            reasoning=reasoning,
        )


# Quick test function
def quick_test():
    """Test hybrid analyzer."""
    import os
    from dotenv import load_dotenv

    load_dotenv()

    api_key = os.getenv("FIRECRAWL_API_KEY", "")

    test_keyword = "best noise cancelling headphones 2024"

    if not api_key:
        print("⚠️  FIRECRAWL_API_KEY not found")
        print(f"Testing keyword + LLM only for: '{test_keyword}'\n")

        analyzer = HybridIntentAnalyzer()
        result = analyzer.analyze(test_keyword, use_firecrawl=False, use_llm=True)
    else:
        print(f"✅ Testing full hybrid analysis for: '{test_keyword}'\n")

        analyzer = HybridIntentAnalyzer(firecrawl_api_key=api_key)
        result = analyzer.analyze(test_keyword, use_firecrawl=True, use_llm=True)

    print("=" * 60)
    print("🎯 Hybrid Intent Analyzer - Test Results")
    print("=" * 60)
    print(f"Keyword: {result.keyword}")
    print(f"Primary Intent: {result.primary_intent}")
    print(f"Confidence: {result.confidence_score}% ({result.confidence_level.value})")
    print(f"Secondary: {result.secondary_intent}")

    print(f"\n📊 Signal Sources:")
    fc_status = (
        f"✅ Used ({result.firecrawl_results_count} results)"
        if result.firecrawl_used
        else "❌ Not used"
    )
    print(f"  Firecrawl: {fc_status}")

    llm_status = (
        f"✅ {result.llm_primary_intent} ({result.llm_confidence:.1f}%)"
        if result.llm_reasoning
        else "❌ Not used"
    )
    print(f"  LLM: {llm_status}")

    print(f"\n💡 Reasoning:")
    print(f"  {result.reasoning}")

    if result.llm_reasoning:
        print(f"\n🤖 LLM Analysis:")
        print(f"  {result.llm_reasoning}")

    if result.serp_features:
        print(f"\n🔍 SERP Features: {', '.join(result.serp_features)}")

    print(f"\n📈 Intent Scores:")
    for intent, score in sorted(
        result.all_intent_scores.items(), key=lambda x: x[1], reverse=True
    ):
        print(f"  {intent}: {score:.1f}%")

    print("=" * 60)
    print("✅ Test complete!")


if __name__ == "__main__":
    quick_test()
