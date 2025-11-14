import re
from typing import List, Dict, Tuple
from collections import Counter
from enum import Enum

class Intent(Enum):
    INFORMATIONAL = "informational"
    COMMERCIAL = "commercial"
    TRANSACTIONAL = "transactional"
    NAVIGATIONAL = "navigational"
    PROBLEM_SOLVING = "problem_solving"

class SearchIntentClassifier:
    def __init__(self):
        # Define patterns for each intent type
        self.intent_patterns = {
            Intent.INFORMATIONAL: {
                "urls": [r"wikipedia\.org", r"blog", r"guide", r"how-to", r"tutorial"],
                "keywords": ["what is", "what are", "explain", "definition", "how does", "overview"],
                "sources": ["wikipedia", "medium", "blog", "educational"]
            },
            Intent.PROBLEM_SOLVING: {
                "urls": [r"reddit\.com", r"stackoverflow", r"github", r"forum"],
                "keywords": ["how to", "can i", "how do i", "fix", "solve", "error", "issue"],
                "sources": ["reddit", "stackoverflow", "github", "community"]
            },
            Intent.COMMERCIAL: {
                "urls": [r"vs", r"comparison", r"best", r"review"],
                "keywords": ["vs", "comparison", "best", "better", "pros and cons"],
                "sources": ["review", "comparison", "g2", "capterra", "trustpilot"]
            },
            Intent.TRANSACTIONAL: {
                "urls": [r"shop|store|amazon|ebay|buy"],
                "keywords": ["buy", "price", "purchase", "deal", "discount", "coupon"],
                "sources": ["amazon", "ebay", "shop", "store", "ecommerce"]
            },
            Intent.NAVIGATIONAL: {
                "urls": [r"official|\.com$", r"app store"],
                "keywords": ["login", "sign in", "official", "app"],
                "sources": ["official website", "app store"]
            }
        }

    def extract_url_features(self, urls: List[str]) -> Dict[str, int]:
        """Extract features from URLs"""
        features = {}
        
        for url in urls:
            # Extract domain type
            if "reddit.com" in url:
                features["reddit"] = features.get("reddit", 0) + 1
            elif "github.com" in url:
                features["github"] = features.get("github", 0) + 1
            elif "youtube.com" in url:
                features["youtube"] = features.get("youtube", 0) + 1
            elif "wikipedia.org" in url:
                features["wikipedia"] = features.get("wikipedia", 0) + 1
            elif any(x in url for x in ["blog", "medium", "hashnode"]):
                features["blog"] = features.get("blog", 0) + 1
            elif any(x in url for x in ["amazon", "shop", "store", "ebay"]):
                features["ecommerce"] = features.get("ecommerce", 0) + 1
            
            # Extract path keywords
            if "comparison" in url or "vs" in url:
                features["comparison"] = features.get("comparison", 0) + 1
            if "how-to" in url or "tutorial" in url or "guide" in url:
                features["tutorial"] = features.get("tutorial", 0) + 1
        
        return features

    def extract_title_features(self, titles: List[str]) -> Dict[str, int]:
        """Extract intent signals from result titles"""
        features = {}
        all_text = " ".join(titles).lower()
        
        # Problem-solving indicators
        problem_keywords = ["how to", "can i", "error", "fix", "solve", "issue", "guide", "tutorial"]
        for keyword in problem_keywords:
            count = len(re.findall(rf"\b{keyword}\b", all_text))
            if count > 0:
                features[f"problem_{keyword}"] = count
        
        # Comparison indicators
        comparison_keywords = ["vs", "comparison", "best", "vs.", "compared to"]
        for keyword in comparison_keywords:
            count = len(re.findall(rf"\b{keyword}\b", all_text))
            if count > 0:
                features[f"comparison_{keyword}"] = count
        
        # Informational indicators
        info_keywords = ["what is", "explain", "overview", "introduction", "definition"]
        for keyword in info_keywords:
            count = len(re.findall(rf"\b{keyword}\b", all_text))
            if count > 0:
                features[f"info_{keyword}"] = count
        
        return features

    def classify_intent(self, urls: List[str], titles: List[str] = None) -> Tuple[Intent, Dict]:
        """
        Classify search intent based on SERP results
        
        Args:
            urls: List of URLs from SERP results
            titles: Optional list of page titles
        
        Returns:
            Tuple of (primary_intent, detailed_scores)
        """
        scores = {intent: 0 for intent in Intent}
        
        # Extract URL features
        url_features = self.extract_url_features(urls)
        
        # Score based on domain types
        if url_features.get("reddit", 0) > 0 or url_features.get("github", 0) > 0:
            scores[Intent.PROBLEM_SOLVING] += 3
        
        if url_features.get("blog", 0) > 0 or url_features.get("wikipedia", 0) > 0:
            scores[Intent.INFORMATIONAL] += 2
        
        if url_features.get("youtube", 0) > 0:
            scores[Intent.PROBLEM_SOLVING] += 1
            scores[Intent.INFORMATIONAL] += 1
        
        if url_features.get("ecommerce", 0) > 0:
            scores[Intent.TRANSACTIONAL] += 3
        
        if url_features.get("comparison", 0) > 0:
            scores[Intent.COMMERCIAL] += 3
        
        if url_features.get("tutorial", 0) > 0:
            scores[Intent.PROBLEM_SOLVING] += 2
        
        # Extract and score title features if provided
        if titles:
            title_features = self.extract_title_features(titles)
            
            problem_count = sum(v for k, v in title_features.items() if k.startswith("problem_"))
            comparison_count = sum(v for k, v in title_features.items() if k.startswith("comparison_"))
            info_count = sum(v for k, v in title_features.items() if k.startswith("info_"))
            
            scores[Intent.PROBLEM_SOLVING] += problem_count * 2
            scores[Intent.COMMERCIAL] += comparison_count * 2
            scores[Intent.INFORMATIONAL] += info_count * 2
        
        # Determine primary intent
        primary_intent = max(scores, key=scores.get)
        
        # Normalize scores
        total_score = sum(scores.values())
        if total_score > 0:
            normalized_scores = {intent: (score/total_score)*100 for intent, score in scores.items()}
        else:
            normalized_scores = {intent: 0 for intent in Intent}
        
        return primary_intent, normalized_scores

# Example usage
if __name__ == "__main__":
    classifier = SearchIntentClassifier()
    
    # Test with "Alexa Homekit" SERP results
    urls = [
        "https://www.reddit.com/r/smarthome/comments/146on7c/can_i_use_apple_homekit_and_amazon_alexa_at_the/",
        "https://www.addtohomekit.com/blog/alexa-homekit/",
        "https://www.youtube.com/watch?v=IbW4-Q4GBqk",
        "https://github.com/joeyhage/homebridge-alexa-smarthome",
        "https://www.cnet.com/home/smart-home/smart-home-guide-get-the-most-out-of-your-amazon-alexa-google-home-and-apple-homekit/"
    ]
    
    titles = [
        "Can I use Apple HomeKit and Amazon Alexa at the same time?",
        "Complete Guide: Alexa with HomeKit Integration",
        "How to Connect Alexa with HomeKit - Tutorial",
        "Homebridge Alexa SmartHome GitHub",
        "Smart Home Guide: Amazon Alexa vs Apple HomeKit vs Google Home"
    ]
    
    # Classify intent
    primary_intent, scores = classifier.classify_intent(urls, titles)
    
    print(f"\n{'='*60}")
    print(f"Search Query: 'Alexa Homekit'")
    print(f"{'='*60}\n")
    print(f"Primary Intent: {primary_intent.value.upper()}")
    print(f"\nIntent Scores:")
    for intent, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        print(f"  {intent.value.capitalize():20} : {score:.1f}%")
    
    print(f"\n{'='*60}\n")
