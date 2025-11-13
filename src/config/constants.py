import os

__version__ = "1.4.0"
AUTHOR = "Knovik Engineering Team"
FIRECRAWL_KEY = os.getenv("FIRECRAWL_API_KEY", "")

FIRECRAWL_SEARCH_URL = "https://api.firecrawl.dev/v2/search"

INTENTS = ["Informational", "Transactional", "Navigational", "Commercial Investigation"]

INTEGRATION_VERBS = [
    "connect",
    "pair",
    "link",
    "use",
    "enable",
    "setup",
    "set up",
    "add",
    "integrate",
    "bridge",
    "work with",
    "works with",
]

BRAND_LEXICON = [
    "alexa",
    "amazon",
    "apple",
    "homekit",
    "siri",
    "homepod",
    "google",
    "nest",
    "assistant",
    "smartthings",
    "ikea",
    "philips hue",
]
