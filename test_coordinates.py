
import numpy as np
from projection import project_triangle

# Each voxel gets a value based on its coordinates.
volume = np.zeros((10, 10, 10), dtype=np.int16)

for x in range(10):
    for y in range(10):
        for z in range(10):
            volume[x, y, z] = x + 10*y + 100*z

a = (2, 2, 2)
b = (2, 6, 2)
c = (2, 2, 6)

result = project_triangle(volume, a, b, c)

print("Projected image:")
print(result)

# The final row samples the base from b to c.
expected_last_row = np.array(
    [262, 352, 442, 532, 622, 622, 622],
    dtype=np.int16
)

print("\nLast row:", result[-1])

expected_last_row = np.array(
    [262, 352, 352, 442, 532, 532, 622],
    dtype=np.int16
)

np.testing.assert_array_equal(result[-1], expected_last_row)
print("Coordinate test passed!")