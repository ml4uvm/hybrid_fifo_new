import random

from hybrid.hybrid_config import (
    EXPLORATION_EPSILON,
    DEBUG_PRINT
)


# =========================================================
# Adaptive hybrid selector
# =========================================================

def select_mode(stagnated=False):

    """
    Hybrid selection policy

    Behavior:
    -----------------------------------------
    - No stagnation  -> pure ML
    - Stagnation     -> epsilon exploration
    """

    # =====================================================
    # Pure ML phase
    # =====================================================

    if not stagnated:

        mode = "ml"

        if DEBUG_PRINT:
            print(
                "[HYBRID] "
                "Pure ML exploitation"
            )

        return mode

    # =====================================================
    # Exploration phase
    # =====================================================

    eps = EXPLORATION_EPSILON

    if random.random() < eps:

        mode = "random"

    else:

        mode = "ml"

    if DEBUG_PRINT:

        print(
            f"[HYBRID] "
            f"Stagnation detected | "
            f"epsilon={eps:.3f} | "
            f"mode={mode}"
        )

    return mode