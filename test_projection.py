
import numpy as np
from projection import sample_volume, project_triangle


# Create a simple 10x10x10 volume.
volume = np.full((10, 10, 10), 100, dtype=np.int16)

# Test individual voxel sampling.
assert sample_volume(volume, (2, 3, 4)) == 100
assert sample_volume(volume, (-1, 3, 4)) == 0

# Define an isosceles triangle in 3D.
a = (2, 2, 2)
b = (2, 6, 2)
c = (2, 2, 6)

result = project_triangle(volume, a, b, c)

print("Output shape:", result.shape)
print("Projected image:")
print(result)

# Verify dimensions and sampled values.
assert result.shape == (4, 7)
assert np.all(np.isin(result, [0, 100]))
assert result[0, 3] == 100
assert np.count_nonzero(result[-1]) == 7

print("\nAll initial tests passed!")
