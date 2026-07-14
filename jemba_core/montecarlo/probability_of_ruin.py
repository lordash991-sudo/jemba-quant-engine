from math import log


def probability_of_ruin(
    win_rate: float,
    payoff_ratio: float,
    risk_per_trade: float,
    ruin_threshold: float,
) -> float:
    """
    Approximate probability of ruin.

    Parameters
    ----------
    win_rate : float
    payoff_ratio : float
    risk_per_trade : float
    ruin_threshold : float

    Returns
    -------
    float
    """

    edge = win_rate * payoff_ratio - (1 - win_rate)

    if edge <= 0:
        return 1.0

    capital_steps = ruin_threshold / risk_per_trade

    return max(0.0, min(1.0, (1 - edge) ** capital_steps))