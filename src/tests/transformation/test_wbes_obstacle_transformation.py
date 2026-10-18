import pandas as pd
import pytest

from ndi.transformation.transform_wbes_obstacles import (
    OBSTACLES,
    build_obstacle_summary,
    validate_summary,
)


def sample_dataframe():
    return pd.DataFrame({
        "c30a": [3, 4, 2, 1],
        "d30a": [0, 1, 2, 3],
        "d30b": [4, 4, 1, 0],
        "e30": [0, 1, -7, 3],
        "g30a": [0, 1, 2, 3],
        "j30a": [3, 3, 2, 1],
        "j30b": [0, 1, 2, 3],
        "j30c": [0, 0, 1, 2],
        "j30e": [3, 4, 2, 1],
        "j30f": [0, 1, 2, 3],
        "h30": [0, 0, 1, 2],
        "i30": [0, 1, 2, 3],
        "k30": [3, 4, 2, -7],
        "l30a": [0, 1, 2, 3],
        "wmedian": [1.0, 2.0, 1.0, 2.0],
    })


def test_builds_all_obstacle_indicators():
    dataframe = sample_dataframe()
    labels = {column: f"Label for {column}" for column in OBSTACLES}

    results = build_obstacle_summary(dataframe, labels)

    assert len(results) == len(OBSTACLES)
    assert {result["obstacle"] for result in results} == set(OBSTACLES)
    assert all(result["weight"] == "wmedian" for result in results)


def test_results_are_sorted_by_weighted_share():
    dataframe = sample_dataframe()
    results = build_obstacle_summary(dataframe, {})

    shares = [result["weighted_share"] for result in results]

    assert shares == sorted(shares, reverse=True)


def test_summary_validation_accepts_valid_results():
    dataframe = sample_dataframe()
    results = build_obstacle_summary(dataframe, {})

    validate_summary(results, len(dataframe))


def test_summary_validation_rejects_duplicate_indicators():
    dataframe = sample_dataframe()
    results = build_obstacle_summary(dataframe, {})
    results.append(results[0].copy())

    with pytest.raises(ValueError, match="Expected 14 indicators"):
        validate_summary(results, len(dataframe))


def test_summary_validation_rejects_invalid_share():
    dataframe = sample_dataframe()
    results = build_obstacle_summary(dataframe, {})
    results[0]["weighted_share"] = 1.5

    with pytest.raises(ValueError, match="outside 0 to 1"):
        validate_summary(results, len(dataframe))
