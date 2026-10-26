
import numpy as np
from projection import sample_volume, project_triangle

volume = np.full((10, 10, 10), 100, dtype=np.uint8)

# Out-of-bounds sampling
assert sample_volume(volume, (-1, 3, 3)) == 0
assert sample_volume(volume, (10, 3, 3)) == 0

# Valid boundary point
assert sample_volume(volume, (9, 9, 9)) == 100

# Degenerate triangle must be rejected
try:
    project_triangle(
        volume,
        (1, 1, 1),
        (2, 2, 2),
        (3, 3, 3)
    )
except ValueError:
    print("Degenerate triangle correctly rejected")
else:
    raise AssertionError("Degenerate triangle was accepted")

# Unequal triangle legs must be rejected
try:
    project_triangle(
        volume,
        (1, 1, 1),
        (1, 5, 1),
        (1, 1, 3)
    )
except ValueError:
    print("Non-isosceles triangle correctly rejected")
else:
    raise AssertionError("Invalid triangle was accepted")

print("All edge-case tests passed!")
