
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
    """Vectorized triangle projection using nearest-neighbor sampling."""

    if volume.ndim != 3:
        raise ValueError("Volume must be 3-dimensional")

    a, b, c = [
        np.asarray(p, dtype=float)
        for p in (a, b, c)
    ]

    if any(p.shape != (3,) or not np.all(np.isfinite(p))
           for p in (a, b, c)):
        raise ValueError("Vertices must be finite 3D points")

    ab = b - a
    ac = c - a

    Dab = np.linalg.norm(ab)
    Dac = np.linalg.norm(ac)
    Dbc = np.linalg.norm(c - b)

    if min(Dab, Dac, Dbc) <= 0:
        raise ValueError("Degenerate triangle")

    if not np.isclose(Dab, Dac, rtol=1e-6):
        raise ValueError("Triangle must be isosceles")

    if np.linalg.norm(np.cross(ab, ac)) <= 1e-10 * Dab * Dac:
        raise ValueError("Triangle vertices are collinear")

    N = int(np.ceil(Dab))
    H = N
    W = int(np.ceil(Dbc)) + 1

    E = np.zeros((H, W), dtype=volume.dtype)

    # Process one scanline at a time.
    for y in range(H):
        ty = (y + 1) / N

        a1 = a + ty * ab
        a2 = a + ty * ac

        d12 = np.linalg.norm(a2 - a1)
        K = max(1, int(np.ceil(d12)))

        start = (W - (K + 1)) // 2

        # Generate ALL sample positions for this row.
        tx = np.arange(K + 1) / K
        points = a1 + tx[:, None] * (a2 - a1)

        # Check which continuous positions lie inside the volume.
        bounds = np.asarray(volume.shape) - 1

        valid = np.all(
            (points >= 0) & (points <= bounds),
            axis=1
        )

        # Process only valid points.
        valid_points = points[valid]

        indices = np.floor(
            valid_points + 0.5
        ).astype(np.intp)

        # Read all valid voxels in a single NumPy operation.
        values = volume[
            indices[:, 0],
            indices[:, 1],
            indices[:, 2]
        ]

        # Write sampled values into the corresponding output columns.
        columns = start + np.flatnonzero(valid)

        E[y, columns] = values

    return E



def project_trapezoid(volume, a1, a2, b, c):
    """Project an isosceles trapezoid using NumPy vectorization."""

    if volume.ndim != 3:
        raise ValueError("Volume must be 3-dimensional")

    # Convert vertices to NumPy arrays.
    a1, a2, b, c = [
        np.asarray(p, dtype=float)
        for p in (a1, a2, b, c)
    ]

    points = (a1, a2, b, c)

    if any(
        p.shape != (3,) or not np.all(np.isfinite(p))
        for p in points
    ):
        raise ValueError("Vertices must be finite 3D points")

    # Calculate the two legs.
    left_leg = b - a1
    right_leg = c - a2

    left_length = np.linalg.norm(left_leg)
    right_length = np.linalg.norm(right_leg)

    # Calculate the two bases.
    top = a2 - a1
    bottom = c - b

    top_length = np.linalg.norm(top)
    bottom_length = np.linalg.norm(bottom)

    # Validate geometry.
    if min(
        left_length,
        right_length,
        top_length,
        bottom_length
    ) <= 0:
        raise ValueError("Degenerate trapezoid")

    if not np.isclose(left_length, right_length, rtol=1e-6):
        raise ValueError("Trapezoid legs must have equal length")

    # Bases must be parallel and point in the same direction.
    if (
        np.linalg.norm(np.cross(top, bottom))
        > 1e-6 * top_length * bottom_length
        or np.dot(top, bottom) <= 0
    ):
        raise ValueError("Trapezoid bases must be parallel")

    # Validate that the trapezoid has nonzero area.
    normal = np.cross(top, left_leg)
    normal_length = np.linalg.norm(normal)

    if normal_length <= 1e-10 * top_length * left_length:
        raise ValueError("Degenerate trapezoid area")

    # All vertices must lie on the same plane.
    if abs(np.dot(c - a1, normal)) > (
        1e-6
        * normal_length
        * max(top_length, bottom_length, left_length)
    ):
        raise ValueError("Trapezoid vertices must be coplanar")

    # Reject equal-length bases in our current design.
    if np.isclose(top_length, bottom_length, rtol=1e-6):
        raise ValueError("Trapezoid bases must have different lengths")

    # Calculate output dimensions.
    N = int(np.ceil(left_length))

    H = N + 1
    W = int(np.ceil(max(top_length, bottom_length))) + 1

    E = np.zeros((H, W), dtype=volume.dtype)

    # Volume boundaries.
    bounds = np.asarray(volume.shape) - 1

    # Process each scanline.
    for y in range(H):

        ty = y / N

        # Calculate scanline endpoints.
        p1 = a1 + ty * left_leg
        p2 = a2 + ty * right_leg

        # Calculate scanline length.
        d12 = np.linalg.norm(p2 - p1)
        K = max(1, int(np.ceil(d12)))

        # Center the scanline.
        start = (W - (K + 1)) // 2

        # Generate all sampling points simultaneously.
        tx = np.arange(K + 1) / K
        sample_points = p1 + tx[:, None] * (p2 - p1)

        # Check which points are inside the volume.
        valid = np.all(
            (sample_points >= 0)
            & (sample_points <= bounds),
            axis=1
        )

        # Keep only valid sampling points.
        valid_points = sample_points[valid]

        # Convert continuous coordinates to voxel indices.
        indices = np.floor(
            valid_points + 0.5
        ).astype(np.intp)

        # Read all voxel values in one NumPy operation.
        values = volume[
            indices[:, 0],
            indices[:, 1],
            indices[:, 2]
        ]

        # Calculate corresponding output columns.
        columns = start + np.flatnonzero(valid)

        # Write values into the output image.
        E[y, columns] = values

    return E
