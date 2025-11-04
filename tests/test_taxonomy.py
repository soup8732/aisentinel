from __future__ import annotations

from src.utils.taxonomy import tools_by_category, Category


def test_tools_by_category_nonempty() -> None:
    mapping = tools_by_category()
    assert set(mapping.keys()) == set(Category)
    # At least one category should have tools listed
    assert any(len(v) > 0 for v in mapping.values())
