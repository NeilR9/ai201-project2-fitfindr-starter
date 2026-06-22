"""
tools.py

The three required FitFindr tools. Each tool is a standalone function that
can be called and tested independently before being wired into the agent loop.

Complete and test each tool before moving to agent.py.

Tools:
    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)              → str
    create_fit_card(outfit, new_item)               → str
"""

import os

from dotenv import load_dotenv
from groq import Groq

from utils.data_loader import load_listings

load_dotenv()


# ── Groq client ───────────────────────────────────────────────────────────────

def _get_groq_client():
    """Initialize and return a Groq client using GROQ_API_KEY from .env."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not set. Add it to a .env file in the project root."
        )
    return Groq(api_key=api_key)


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the mock listings dataset for items matching the description,
    optional size, and optional price ceiling.

    Args:
        description: Keywords describing what the user is looking for
                     (e.g., "vintage graphic tee").
        size:        Size string to filter by, or None to skip size filtering.
                     Matching is case-insensitive (e.g., "M" matches "S/M").
        max_price:   Maximum price (inclusive), or None to skip price filtering.

    Returns:
        A list of matching listing dicts, sorted by relevance (best match first).
        Returns an empty list if nothing matches — does NOT raise an exception.

    Each listing dict has the following fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand, platform

    TODO:
        1. Load all listings with load_listings().
        2. Filter by max_price and size (if provided).
        3. Score each remaining listing by keyword overlap with `description`.
        4. Drop any listings with a score of 0 (no relevant matches).
        5. Sort by score, highest first, and return the listing dicts.

    Before writing code, fill in the Tool 1 section of planning.md.
    """
    # Step 1: Load all listings
    listings = load_listings()

    # Step 2: Filter by max_price and size
    filtered = []
    for listing in listings:
        if max_price is not None and listing["price"] > max_price:
            continue
        if size is not None and size.lower() not in listing["size"].lower():
            continue
        filtered.append(listing)

    # Step 3: Score each listing by keyword overlap with description
    keywords = description.lower().split()

    def score_listing(listing):
        searchable = " ".join([
            listing.get("title", "") or "",
            listing.get("description", "") or "",
            listing.get("category", "") or "",
            listing.get("brand", "") or "",
            " ".join(listing.get("style_tags", []) or []),
            " ".join(listing.get("colors", []) or []),
        ]).lower()

        return sum(1 for keyword in keywords if keyword in searchable)

    scored = [(listing, score_listing(listing)) for listing in filtered]

    # Step 4: Drop listings with a score of 0
    scored = [(listing, score) for listing, score in scored if score > 0]

    # Step 5: Sort by score highest first and return just the listing dicts
    scored.sort(key=lambda x: x[1], reverse=True)

    return [listing for listing, score in scored]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest 1–2 complete outfits.

    Args:
        new_item: A listing dict (the item the user is considering buying).
        wardrobe: A wardrobe dict with an 'items' key containing a list of
                  wardrobe item dicts. May be empty — handle this gracefully.

    Returns:
        A non-empty string with outfit suggestions.
        If the wardrobe is empty, offer general styling advice for the item
        rather than raising an exception or returning an empty string.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If empty: call the LLM with a prompt for general styling ideas
           (what kinds of items pair well, what vibe it suits, etc.).
        3. If not empty: format the wardrobe items into a prompt and ask
           the LLM to suggest specific outfit combinations using the new item
           and named pieces from the wardrobe.
        4. Return the LLM's response as a string.

    Before writing code, fill in the Tool 2 section of planning.md.
    """
    new_item_details = (
        f"Title: {new_item.get('title', 'Unknown')}\n"
        f"Category: {new_item.get('category', 'Unknown')}\n"
        f"Style Tags: {', '.join(new_item.get('style_tags', []))}\n"
        f"Colors: {', '.join(new_item.get('colors', []))}\n"
        f"Brand: {new_item.get('brand', 'Unknown')}\n"
        f"Condition: {new_item.get('condition', 'Unknown')}\n"
        f"Description: {new_item.get('description', 'No description available')}\n"
    )

    # Step 1: Check if wardrobe is empty
    wardrobe_items = wardrobe.get("items", [])

    # Step 2: Empty wardrobe — general styling advice
    if not wardrobe_items:
        prompt = (
            f"A user is considering buying the following thrifted item:\n\n"
            f"{new_item_details}\n"
            f"Their wardrobe is currently empty. Suggest 1-2 complete outfit ideas "
            f"for this item, describing what types of pieces would pair well with it, "
            f"what vibe or aesthetic it suits, and how they might style it. "
            f"Be specific and conversational."
        )

    # Step 3: Wardrobe has items — suggest specific combinations
    else:
        wardrobe_formatted = "\n".join([
            f"- {item.get('name', 'Unknown')} "
            f"({item.get('category', 'Unknown')}, "
            f"colors: {', '.join(item.get('colors', []))}, "
            f"style: {', '.join(item.get('style_tags', []))}, "
            f"notes: {item.get('notes', 'none')})"
            for item in wardrobe_items
        ])

        prompt = (
            f"A user is considering buying the following thrifted item:\n\n"
            f"{new_item_details}\n"
            f"Here is their current wardrobe:\n{wardrobe_formatted}\n\n"
            f"Suggest 1-2 complete outfit combinations using the new item and "
            f"specific pieces from their wardrobe. Reference the wardrobe items "
            f"by name. Be specific, practical, and conversational."
        )

    # Step 4: Call the LLM and return the response
    try:
        client = _get_groq_client()
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        result = response.choices[0].message.content.strip()
        return result if result else ""

    except Exception as e:
        return ""
    


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Generate a short, shareable outfit caption for the thrifted find.

    Args:
        outfit:   The outfit suggestion string from suggest_outfit().
        new_item: The listing dict for the thrifted item.

    Returns:
        A 2–4 sentence string usable as an Instagram/TikTok caption.
        If outfit is empty or missing, return a descriptive error message
        string — do NOT raise an exception.

    The caption should:
    - Feel casual and authentic (like a real OOTD post, not a product description)
    - Mention the item name, price, and platform naturally (once each)
    - Capture the outfit vibe in specific terms
    - Sound different each time for different inputs (use higher LLM temperature)

    TODO:
        1. Guard against an empty or whitespace-only outfit string.
        2. Build a prompt that gives the LLM the item details and the outfit,
           and asks for a caption matching the style guidelines above.
        3. Call the LLM and return the response.

    Before writing code, fill in the Tool 3 section of planning.md.
    """
    # Step 1: Guard against empty or whitespace-only outfit string
    if not outfit or not outfit.strip():
        return (
            "Could not generate a fit card: insufficient outfit information was "
            "available. Please try again with a valid outfit suggestion."
        )

    # Step 2: Build the prompt
    item_name = new_item.get("title", "thrifted item")
    item_price = new_item.get("price", "unknown price")
    item_platform = new_item.get("platform", "a thrift platform")
    item_style_tags = ", ".join(new_item.get("style_tags", []))
    item_colors = ", ".join(new_item.get("colors", []))

    prompt = (
        f"You are writing an Instagram caption for a thrift outfit post.\n\n"
        f"The thrifted item is: {item_name}, bought for ${item_price} on {item_platform}.\n"
        f"Style tags: {item_style_tags}\n"
        f"Colors: {item_colors}\n\n"
        f"The outfit suggestion is:\n{outfit}\n\n"
        f"Write a 2-4 sentence Instagram caption for this outfit. The caption should:\n"
        f"- Feel casual and authentic, like a real person's OOTD post\n"
        f"- Mention the item name, price, and platform naturally, once each\n"
        f"- Capture the specific vibe of the outfit\n"
        f"- NOT sound like a product description or advertisement\n"
        f"- Optionally include 1-2 relevant hashtags at the end\n"
        f"Write only the caption, nothing else."
    )

    # Step 3: Call the LLM and return the response
    try:
        client = _get_groq_client()
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
        )
        result = response.choices[0].message.content.strip()
        return result if result else ""

    except Exception as e:
        return ""

