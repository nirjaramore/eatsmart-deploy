"""EatSmartly Agents Package."""

from agents.data_collection import DataCollectionAgent
from agents.web_scraping import WebScrapingAgent
from agents.personalization import PersonalizationAgent

__all__ = [
    "DataCollectionAgent",
    "WebScrapingAgent",
    "PersonalizationAgent"
]
