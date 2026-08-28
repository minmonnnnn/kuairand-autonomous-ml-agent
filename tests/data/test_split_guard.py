"""The test split must not be readable by accident. Owner: Rishi."""
import pytest

from src.data.guard import (
    SPLIT_CLASS,
    FinalSubmissionToken,
    Split,
    SplitAccessError,
    check_access,
)


def test_dev_splits_are_open():
    check_access(Split.TRAIN)
    check_access(Split.VALID)


def test_test_split_is_blocked_without_a_token():
    with pytest.raises(SplitAccessError):
        check_access(Split.TEST)


def test_test_split_opens_with_a_token(tmp_path, monkeypatch):
    import src.data.guard as g

    monkeypatch.setattr(g, "ERROR_LOGS", tmp_path)
    token = FinalSubmissionToken.issue("EXP-0031", "final submission")
    check_access(Split.TEST, token)
    assert (tmp_path / "split_access.log").exists()


def test_issuing_a_token_is_audited(tmp_path, monkeypatch):
    import json

    import src.data.guard as g

    monkeypatch.setattr(g, "ERROR_LOGS", tmp_path)
    FinalSubmissionToken.issue("EXP-0031", "final submission")
    line = json.loads((tmp_path / "split_access.log").read_text().strip())
    assert line["experiment_id"] == "EXP-0031"
    assert line["issued_at"]


def test_split_classification_matches_the_spec():
    assert SPLIT_CLASS[Split.TRAIN] == "DEVELOPMENT"
    assert SPLIT_CLASS[Split.VALID] == "VALIDATION"
    assert SPLIT_CLASS[Split.TEST] == "FINAL-ONLY"
