import json

from click.testing import CliRunner

from prompt_ops.interfaces.cli import cli


def test_cli_help_uses_prompt_quality_lab_name():
    result = CliRunner().invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "Prompt Quality Lab" in result.output


def test_evaluate_emits_json_and_writes_the_report(tmp_path):
    outputs = tmp_path / "candidate.jsonl"
    outputs.write_text(
        '{"id":"1","expected":"green","actual":"green"}\n'
        '{"id":"2","expected":"blue","actual":"red"}\n',
        encoding="utf-8",
    )
    report_path = tmp_path / "report.json"

    result = CliRunner().invoke(
        cli,
        ["evaluate", str(outputs), "--format", "json", "--output", str(report_path)],
    )

    assert result.exit_code == 0
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["samples"] == 2
    assert report["passed"] is True
    assert '"token_f1"' in result.output
    assert '"character_f1"' in result.output


def test_evaluate_returns_nonzero_when_baseline_regresses(tmp_path):
    baseline = tmp_path / "baseline.jsonl"
    candidate = tmp_path / "candidate.jsonl"
    baseline.write_text('{"expected":"blue car","actual":"blue car"}\n')
    candidate.write_text('{"expected":"blue car","actual":"red truck"}\n')

    result = CliRunner().invoke(
        cli, ["evaluate", str(candidate), "--baseline", str(baseline)]
    )

    assert result.exit_code == 1
    assert "regressed" in result.output


def test_evaluate_reports_the_input_line_for_invalid_json(tmp_path):
    outputs = tmp_path / "invalid.jsonl"
    outputs.write_text('{"expected":"yes","actual":"yes"}\nnot-json\n')

    result = CliRunner().invoke(cli, ["evaluate", str(outputs)])

    assert result.exit_code == 1
    assert "line 2" in result.output


def test_evaluate_can_use_character_f1_as_the_regression_gate(tmp_path):
    baseline = tmp_path / "baseline.jsonl"
    candidate = tmp_path / "candidate.jsonl"
    baseline.write_text(
        '{"id":"zh-1","expected":"退款申请已通过","actual":"退款申请已通过"}\n',
        encoding="utf-8",
    )
    candidate.write_text(
        '{"id":"zh-1","expected":"退款申请已通过","actual":"退款申请通过"}\n',
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        cli,
        [
            "evaluate",
            str(candidate),
            "--baseline",
            str(baseline),
            "--gate-metric",
            "character_f1",
        ],
    )

    assert result.exit_code == 1
    assert "Character F1" in result.output
    assert "character_f1 regressed" in result.output
