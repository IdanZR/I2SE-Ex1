
import numpy as np
from projection import project_trapezoid


# Create a 3D volume filled with the value 100.
volume = np.full((10, 10, 10), 100, dtype=np.int16)


# Define an isosceles trapezoid in the plane X = 2.
a1 = (2, 3, 2)
a2 = (2, 5, 2)

b = (2, 2, 4)
c = (2, 6, 4)


# Run the trapezoid projection algorithm.
result = project_trapezoid(volume, a1, a2, b, c)


# Print the actual result.
print("Output shape:", result.shape)
print("Projected trapezoid:")
print(result)


# Define the expected output matrix.
expected = np.array([
    [0,   100, 100, 100,   0],
    [100, 100, 100, 100,   0],
    [100, 100, 100, 100, 100],
    [100, 100, 100, 100, 100]
], dtype=np.int16)


# Verify the output dimensions.
assert result.shape == (4, 5)


# Verify that every pixel matches the expected result.
np.testing.assert_array_equal(result, expected)


print("\nAll trapezoid tests passed!")
