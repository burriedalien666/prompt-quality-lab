import pytest

from prompt_ops.core.quality import (
    character_f1,
    compare_evaluations,
    evaluate_records,
    load_records,
    normalize_text,
    token_f1,
)


def test_normalize_text_collapses_case_and_whitespace():
    assert normalize_text("  Hello   WORLD ") == "hello world"


def test_token_f1_scores_partial_overlap():
    assert token_f1("red green blue", "green blue yellow") == 2 / 3


def test_token_f1_returns_zero_when_both_outputs_are_empty():
    assert token_f1("", "") == 0.0


def test_character_f1_scores_chinese_text_without_spaces():
    assert character_f1("退款申请已通过", "退款申请通过") == pytest.approx(12 / 13)


def test_load_records_reports_the_line_number_for_invalid_json(tmp_path):
    source = tmp_path / "outputs.jsonl"
    source.write_text(
        '{"id": "a", "expected": "yes", "actual": "yes"}\nnot-json\n',
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match=r"line 2"):
        load_records(str(source))


def test_evaluate_records_returns_exact_match_and_token_f1_rates():
    records = [
        {"id": "a", "expected": "blue car", "actual": "blue car"},
        {"id": "b", "expected": "red car", "actual": "blue car"},
    ]

    report = evaluate_records(records)

    assert report["samples"] == 2
    assert report["exact_match"] == 0.5
    assert report["token_f1"] == 0.75
    assert report["character_f1"] == pytest.approx(21 / 26)
    assert report["records"][0]["id"] == "a"


def test_compare_evaluations_rejects_a_token_f1_regression():
    result = compare_evaluations(
        {
            "samples": 2,
            "exact_match": 0.5,
            "token_f1": 0.6,
            "character_f1": 0.7,
        },
        {
            "samples": 2,
            "exact_match": 0.5,
            "token_f1": 0.8,
            "character_f1": 0.7,
        },
    )

    assert result["passed"] is False
    assert result["delta"]["token_f1"] == -0.2
    assert "regressed" in result["failures"][0]


def test_compare_evaluations_applies_absolute_and_relative_gates():
    result = compare_evaluations(
        {
            "samples": 2,
            "exact_match": 0.75,
            "token_f1": 0.85,
            "character_f1": 0.9,
        },
        {
            "samples": 2,
            "exact_match": 0.5,
            "token_f1": 0.8,
            "character_f1": 0.88,
        },
        min_score=0.9,
        min_improvement=0.1,
    )

    assert result["passed"] is False
    assert len(result["failures"]) == 2


def test_compare_evaluations_can_gate_on_character_f1():
    result = compare_evaluations(
        {
            "samples": 1,
            "exact_match": 0.0,
            "token_f1": 0.0,
            "character_f1": 0.8,
        },
        {
            "samples": 1,
            "exact_match": 0.0,
            "token_f1": 0.0,
            "character_f1": 0.9,
        },
        gate_metric="character_f1",
    )

    assert result["passed"] is False
    assert result["delta"]["character_f1"] == -0.1
    assert "character_f1 regressed" in result["failures"][0]
    assert result["gate"]["metric"] == "character_f1"


def test_compare_evaluations_rejects_different_sample_counts():
    with pytest.raises(ValueError, match="sample counts differ"):
        compare_evaluations(
            {
                "samples": 2,
                "exact_match": 0.5,
                "token_f1": 0.5,
                "character_f1": 0.5,
            },
            {
                "samples": 1,
                "exact_match": 0.5,
                "token_f1": 0.5,
                "character_f1": 0.5,
            },
        )
