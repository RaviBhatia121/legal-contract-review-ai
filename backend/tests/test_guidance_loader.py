import pytest

from app.playbook.guidance_loader import GuidanceCorpus, GuidanceItem, GuidanceLoadError, _validate, load_guidance
from app.playbook.loader import load_playbook


def test_loads_all_items():
    corpus = load_guidance()
    assert corpus.guidance_id == "guidance-v1"
    assert corpus.playbook_id == "defense-services-v1"
    assert len(corpus.items) == 27


def test_every_playbook_rule_id_has_guidance():
    corpus = load_guidance()
    playbook = load_playbook()
    covered = {item.rule_id for item in corpus.items}
    assert covered == {r.rule_id for r in playbook.rules}


def test_items_for_rule():
    corpus = load_guidance()
    items = corpus.items_for_rule("DATA-001")
    assert len(items) == 1
    assert items[0].rule_id == "DATA-001"
    assert items[0].category in ("negotiation_tip", "approved_example", "playbook_reference")


def test_cached_instance_is_reused():
    assert load_guidance() is load_guidance()


def _corpus(items: tuple[GuidanceItem, ...]) -> GuidanceCorpus:
    return GuidanceCorpus(
        guidance_id="test",
        guidance_version="1.0-draft",
        playbook_id="defense-services-v1",
        disclaimer="illustrative only",
        items=items,
    )


def test_rejects_unknown_rule_id():
    corpus = _corpus(
        (GuidanceItem(id="G-X", rule_id="NOT-A-RULE", clause_type="unknown", category="negotiation_tip", text="t", source_note="n"),)
    )
    with pytest.raises(GuidanceLoadError, match="unknown rule_id"):
        _validate(corpus)


def test_rejects_invalid_category():
    corpus = _corpus(
        (
            GuidanceItem(
                id="G-X", rule_id="DATA-001", clause_type="data_handling", category="not_a_category", text="t", source_note="n"
            ),
        )
    )
    with pytest.raises(GuidanceLoadError, match="invalid category"):
        _validate(corpus)


def test_rejects_unknown_clause_type():
    corpus = _corpus(
        (
            GuidanceItem(
                id="G-X", rule_id="DATA-001", clause_type="not_a_clause_type", category="negotiation_tip", text="t", source_note="n"
            ),
        )
    )
    with pytest.raises(GuidanceLoadError, match="unknown clause_type"):
        _validate(corpus)


def test_rejects_duplicate_ids():
    item = GuidanceItem(
        id="G-X", rule_id="DATA-001", clause_type="data_handling", category="negotiation_tip", text="t", source_note="n"
    )
    corpus = _corpus((item, item))
    with pytest.raises(GuidanceLoadError, match="Duplicate guidance id"):
        _validate(corpus)
