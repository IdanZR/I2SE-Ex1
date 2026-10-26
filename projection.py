
import numpy as np


def sample_volume(volume, point):
    """Sample a 3D volume using nearest-neighbor sampling."""

    point = np.asarray(point, dtype=float)

    if point.shape != (3,) or not np.all(np.isfinite(point)):
        raise ValueError("Sampling point must contain 3 finite coordinates")

    # Outside the volume? Return zero.
    for coordinate, size in zip(point, volume.shape):
        if coordinate < 0 or coordinate > size - 1:
            return 0

    # Round to the nearest voxel (ties toward the higher index).
    indices = np.floor(point + 0.5).astype(int)

    return volume[tuple(indices)]


def project_triangle(volume, a, b, c):
    """Project an isosceles triangular region from a 3D volume."""

    if volume.ndim != 3:
        raise ValueError("Volume must be 3-dimensional")

    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    c = np.asarray(c, dtype=float)

    if any(p.shape != (3,) or not np.all(np.isfinite(p))
           for p in (a, b, c)):
        raise ValueError("Triangle vertices must be finite 3D points")

    # Triangle geometry
    ab = b - a
    ac = c - a

    Dab = np.linalg.norm(ab)
    Dac = np.linalg.norm(ac)
    Dbc = np.linalg.norm(c - b)

    if Dab == 0 or Dac == 0 or Dbc == 0:
        raise ValueError("Degenerate triangle")

    if not np.isclose(Dab, Dac, rtol=1e-6):
        raise ValueError("Triangle must be isosceles")

    if np.linalg.norm(np.cross(ab, ac)) <= 1e-10 * Dab * Dac:
        raise ValueError("Triangle vertices are collinear")

    # Output dimensions
    N = int(np.ceil(Dab))
    H = N
    W = int(np.ceil(Dbc)) + 1

    E = np.zeros((H, W), dtype=volume.dtype)

    # Outer loop: move down the triangle
    for y in range(H):
        ty = (y + 1) / N

        a1 = a + ty * ab
        a2 = a + ty * ac

        # Current scanline
        d12 = np.linalg.norm(a2 - a1)
        K = max(1, int(np.ceil(d12)))

        start = (W - (K + 1)) // 2

        # Inner loop: sample across the scanline
        for j in range(K + 1):
            tx = j / K

            p = a1 + tx * (a2 - a1)

            value = sample_volume(volume, p)

            x = start + j

            E[y, x] = value

    return E
