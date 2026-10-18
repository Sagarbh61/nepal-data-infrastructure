import math

import pandas as pd


VALID_RATINGS = {0, 1, 2, 3, 4}


def calculate_obstacle_share(
    dataframe,
    obstacle_column,
    weight_column="wmedian",
):
    """
    Calculate the weighted share of valid responses rating an
    obstacle as major or very severe.

    Ratings:
        0 = No obstacle
        1 = Minor obstacle
        2 = Moderate obstacle
        3 = Major obstacle
        4 = Very severe obstacle

    Other codes, such as -7 and -9, are excluded from the
    valid-response denominator.
    """
    required_columns = {obstacle_column, weight_column}
    missing_columns = required_columns - set(dataframe.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    ratings = dataframe[obstacle_column]
    weights = dataframe[weight_column]

    # Missing ratings are excluded. Known special response codes
    # are also excluded, but unexpected codes indicate a data issue.
    observed_ratings = ratings.dropna()
    unexpected_ratings = set(observed_ratings.unique()) - (
        VALID_RATINGS | {-7, -9}
    )

    if unexpected_ratings:
        raise ValueError(
            f"Unexpected ratings in {obstacle_column}: "
            f"{sorted(unexpected_ratings)}"
        )

    valid = ratings.isin(VALID_RATINGS)

    if not valid.any():
        raise ValueError(
            f"No valid responses found for {obstacle_column}"
        )

    valid_weights = weights.loc[valid]

    if valid_weights.isna().any():
        raise ValueError(
            f"Missing weights among valid responses in {weight_column}"
        )

    if not valid_weights.map(
        lambda value: math.isfinite(float(value))
    ).all():
        raise ValueError(
            f"Non-finite weights among valid responses in {weight_column}"
        )

    if (valid_weights <= 0).any():
        raise ValueError(
            f"Weights must be positive in {weight_column}"
        )

    valid_ratings = ratings.loc[valid]
    total_weight = valid_weights.sum()

    major_or_severe = valid_ratings >= 3

    weighted_share = (
        valid_weights.loc[major_or_severe].sum() / total_weight
    )

    return {
        "obstacle": obstacle_column,
        "weight": weight_column,
        "total_records": len(dataframe),
        "valid_responses": int(valid.sum()),
        "excluded_responses": int((~valid).sum()),
        "major_or_severe_responses": int(major_or_severe.sum()),
        "unweighted_share": float(major_or_severe.mean()),
        "weighted_share": float(weighted_share),
    }
