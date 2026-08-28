"""Registry behaviour. Owner: Min."""
import pytest

from src.registry.registry import DuplicateExperimentId, ExperimentRegistry
from src.registry.schema import ExperimentRecord, ExperimentStatus


def _rec(eid, primary=None, status=ExperimentStatus.SUCCESS):
    kw = {}
    if primary is not None:
        kw = dict(
            validation_gauc=primary, validation_ndcg5=primary, validation_primary=primary
        )
    return ExperimentRecord(experiment_id=eid, owner="test", status=status, **kw)


def test_roundtrip(tmp_path):
    r = ExperimentRegistry(tmp_path)
    r.save(_rec("EXP-0001", 0.6100), area="models")
    got = r.get("EXP-0001")
    assert got is not None
    assert got.validation_primary == pytest.approx(0.6100)


def test_primary_must_be_mean_of_components():
    with pytest.raises(ValueError):
        ExperimentRecord(
            experiment_id="EXP-9999",
            owner="test",
            validation_gauc=0.60,
            validation_ndcg5=0.50,
            validation_primary=0.99,  # not the mean
        )


def test_ids_are_not_reused(tmp_path):
    r = ExperimentRegistry(tmp_path)
    r.save(_rec("EXP-0001", 0.61), area="models")
    with pytest.raises(DuplicateExperimentId):
        r.save(_rec("EXP-0001", 0.62), area="features")


def test_next_id_increments(tmp_path):
    r = ExperimentRegistry(tmp_path)
    assert r.next_id() == "EXP-0001"
    r.save(_rec("EXP-0001", 0.61))
    r.save(_rec("EXP-0007", 0.62))
    assert r.next_id() == "EXP-0008"


def test_validation_best_is_not_the_latest(tmp_path):
    """The most recent experiment is not automatically the best one."""
    r = ExperimentRegistry(tmp_path)
    r.save(_rec("EXP-0001", 0.6016))
    r.save(_rec("EXP-0002", 0.6300))
    r.save(_rec("EXP-0003", 0.5900))
    best = r.validation_best()
    assert best.experiment_id == "EXP-0002"
    assert r.get("EXP-0002").is_validation_best is True
    assert r.get("EXP-0003").is_validation_best is False


def test_failed_experiments_are_not_eligible(tmp_path):
    r = ExperimentRegistry(tmp_path)
    r.save(_rec("EXP-0001", 0.6016))
    r.save(_rec("EXP-0002", 0.9999, status=ExperimentStatus.FAILED))
    assert r.validation_best().experiment_id == "EXP-0001"


def test_delta_vs_official_baseline_is_computed(tmp_path):
    r = ExperimentRegistry(tmp_path)
    r.save(_rec("EXP-0001", 0.6116))
    assert r.get("EXP-0001").delta_vs_official_baseline == pytest.approx(0.01, abs=1e-6)
