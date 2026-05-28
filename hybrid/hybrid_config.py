# =========================================================
# Hybrid ML Configuration
# =========================================================

# =========================================================
# Exploration configuration
# =========================================================

# 🔥 Used ONLY during stagnation
EXPLORATION_EPSILON = 0.2

# 🔥 Number of consecutive no-gain tests
# before exploration activates
STAGNATION_THRESHOLD = 10

# =========================================================
# Coverage-aware control
# =========================================================

# Stop simulation once all bins are covered
ENABLE_EARLY_STOP = True

# =========================================================
# Safety limits
# =========================================================

MAX_TESTS = 500

# =========================================================
# Debug / logging
# =========================================================

LOG_MODE_ENABLED = True

DEBUG_PRINT = False