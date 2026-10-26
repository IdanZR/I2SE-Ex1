
import numpy as np

from projection import project_triangle, project_trapezoid


volume = np.full((10, 10, 10), 100, dtype=np.uint8)


def should_reject(function, *points):
    try:
        function(volume, *points)
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def test_triangle_epsilon():
    a = (2, 2, 2)
    b = (2, 6, 2)

    # Difference in leg lengths: 0.0005 < EPS.
    result = project_triangle(
        volume, a, b, (2, 2, 6.0005)
    )
    assert result.size > 0

    # Difference in leg lengths: 0.002 > EPS.
    should_reject(
        project_triangle,
        a, b, (2, 2, 6.002)
    )


def test_equal_trapezoid_bases():
    # A rectangle satisfies the Q&A conditions:
    # equal legs and first base <= second base.
    result = project_trapezoid(
        volume,
        (2, 3, 2), (2, 5, 2),
        (2, 3, 4), (2, 5, 4)
    )

    assert result.size > 0
    assert np.all(result == 100)


def test_reversed_trapezoid_bases():
    # First base length = 4, second = 2.
    should_reject(
        project_trapezoid,
        (2, 2, 2), (2, 6, 2),
        (2, 3, 4), (2, 5, 4)
    )




def test_trapezoid_epsilon():
    a1 = (2, 3, 2)
    a2 = (2, 5, 2)

    # Bottom base is translated in the z direction.
    # Changing its width preserves base parallelism.
    b = (2, 2, 4)
    c = (2, 6, 4)

    # Both legs are equal in the valid case.
    result = project_trapezoid(volume, a1, a2, b, c)
    assert result.size > 0

    # A clearly unequal leg length must be rejected.
    should_reject(
        project_trapezoid,
        a1, a2,
        (2, 2, 4),
        (2, 6.01, 4)
    )


if __name__ == "__main__":
    test_triangle_epsilon()
    test_equal_trapezoid_bases()
    test_reversed_trapezoid_bases()
    test_trapezoid_epsilon()
    print("All assignment geometry tests passed!")
