from tools import search_listings, suggest_outfit, create_fit_card
from utils.data_loader import get_example_wardrobe, get_empty_wardrobe

def test_search_returns_results():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    assert isinstance(results, list)
    assert len(results) > 0

def test_search_empty_results():
    results = search_listings("designer ballgown", size="XXS", max_price=5)
    assert results == []   # empty list, no exception

def test_search_price_filter():
    results = search_listings("jacket", size=None, max_price=10)
    assert all(item["price"] <= 10 for item in results)

def test_suggest_outfit_with_wardrobe():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    suggestion = suggest_outfit(results[0], get_example_wardrobe())
    assert isinstance(suggestion, str)
    assert len(suggestion) > 0

def test_suggest_outfit_empty_wardrobe():
    suggestion = suggest_outfit({"title": "Black Tee"}, get_empty_wardrobe())
    assert isinstance(suggestion, str)
    assert len(suggestion) > 0

def test_create_fit_card_returns_caption():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    outfit = suggest_outfit(results[0], get_example_wardrobe())
    fit_card = create_fit_card(outfit, results[0])
    assert isinstance(fit_card, str)
    assert len(fit_card) > 0

def test_create_fit_card_empty_outfit():
    fit_card = create_fit_card("", {"title": "Black Tee", "price": 20, "platform": "Depop"})
    assert isinstance(fit_card, str)
    assert "Could not generate" in fit_card