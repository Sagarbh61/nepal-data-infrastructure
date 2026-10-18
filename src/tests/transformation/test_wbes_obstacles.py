import pandas as pd
import pytest

from ndi.transformation.wbes_obstacles import (
    calculate_obstacle_share,
)


def test_calculates_weighted_and_unweighted_shares():
    dataframe = pd.DataFrame({
        "j30e": [3, 4, 2, 1, -7, -9],
        "wmedian": [2, 3, 1, 2, 5, 5],
    })

    result = calculate_obstacle_share(dataframe, "j30e")

    assert result["total_records"] == 6
    assert result["valid_responses"] == 4
    assert result["excluded_responses"] == 2
    assert result["major_or_severe_responses"] == 2

    # 2 of 4 valid responses are major or very severe.
    assert result["unweighted_share"] == pytest.approx(0.5)

    # The two qualifying responses have weights 2 and 3.
    # All valid responses have weights 2 + 3 + 1 + 2 = 8.
    assert result["weighted_share"] == pytest.approx(5 / 8)


def test_rejects_unexpected_rating_codes():
    dataframe = pd.DataFrame({
        "j30e": [3, 8],
        "wmedian": [2, 3],
    })

    with pytest.raises(ValueError, match="Unexpected ratings"):
        calculate_obstacle_share(dataframe, "j30e")


def test_rejects_missing_weights_for_valid_responses():
    dataframe = pd.DataFrame({
        "j30e": [3, 2],
        "wmedian": [None, 3],
    })

    with pytest.raises(ValueError, match="Missing weights"):
        calculate_obstacle_share(dataframe, "j30e")


def test_rejects_nonpositive_weights():
    dataframe = pd.DataFrame({
        "j30e": [3, 2],
        "wmedian": [0, 3],
    })

    with pytest.raises(ValueError, match="must be positive"):
        calculate_obstacle_share(dataframe, "j30e")
