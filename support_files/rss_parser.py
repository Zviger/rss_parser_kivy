"""
This module contains class for parsing RSS.
"""
from typing import Dict, Any

from bs4 import BeautifulSoup
import feedparser

from .dtos import Item, Feed

FEED_FIELD_MAPPING = {"title": "title",
                      "link": "link"}

ITEM_FIELD_MAPPING = {"title": "title",
                      "link": "link",
                      "author": "author",
                      "description": "description",
                      "published_parsed": "published_parsed",
                      "media_content": "img_links"}


def apply_field_mapping(field_mapping: Dict[str, str], source: Dict[str, str]) -> Dict[str, Any]:
    return {v: source.get(k) for k, v in field_mapping.items() if source.get(k)}


class Parser:
    """
    This class provides methods to parse RSS.
    """

    @staticmethod
    def parse_feed(url: str, items_limit: int = -1) -> Feed:
        """
        Parse the RSS file.
        :param items_limit: Limit count of returned items.
        :param url:
        """
        if not url:
            return Feed()
        data = feedparser.parse(url)
        if data.bozo != 0:
            raise ConnectionError("Some problems with connection")
        if data.status != 200:
            raise ConnectionError("Invalid url")
        feed = data.get("feed", {})
        feed_data = apply_field_mapping(FEED_FIELD_MAPPING, feed)
        feed_data["rss_link"] = url
        entries = data.get("entries", [])
        if items_limit > 0:
            entries = entries[:items_limit]
        items_data = [apply_field_mapping(ITEM_FIELD_MAPPING, item)
                      for item in entries]
        for item_data in items_data:
            soup = BeautifulSoup(item_data.get("description", ""), 'html.parser')
            item_data["description"] = soup.text
            item_data["img_links"] = [item["url"] for item in item_data.get("img_links", [])]

        feed = Feed(**feed_data)
        feed.items = [Item(**item_data) for item_data in items_data]
        return feed

