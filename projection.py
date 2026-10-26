
import numpy as np
GEOMETRY_EPS = 0.001

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
    """Fast triangle projection with fully vectorized NumPy sampling."""

    if volume.ndim != 3:
        raise ValueError("Volume must be 3-dimensional")

    a, b, c = [
        np.asarray(p, dtype=float)
        for p in (a, b, c)
    ]

    if any(
        p.shape != (3,) or not np.all(np.isfinite(p))
        for p in (a, b, c)
    ):
        raise ValueError("Vertices must be finite 3D points")

    # Triangle geometry.
    ab = b - a
    ac = c - a

    Dab = np.linalg.norm(ab)
    Dac = np.linalg.norm(ac)
    Dbc = np.linalg.norm(c - b)

    if min(Dab, Dac, Dbc) <= 0:
        raise ValueError("Degenerate triangle")

    if abs(Dab - Dac) >= GEOMETRY_EPS:
        raise ValueError("Triangle must be isosceles")

    if np.linalg.norm(np.cross(ab, ac)) <= 1e-10 * Dab * Dac:
        raise ValueError("Triangle vertices are collinear")

    # Output dimensions.
    N = int(np.ceil(Dab))
    H = N
    W = int(np.ceil(Dbc)) + 1

    E = np.zeros((H, W), dtype=volume.dtype)

    # Calculate endpoints for ALL scanlines at once.
    ty = (np.arange(H) + 1) / N

    a1 = a + ty[:, None] * ab
    a2 = a + ty[:, None] * ac

    # Calculate the length and sample count of every scanline.
    differences = a2 - a1

    d12 = np.linalg.norm(differences, axis=1)
    K = np.maximum(1, np.ceil(d12).astype(np.intp))

    # Calculate horizontal offsets for all rows.
    starts = (W - (K + 1)) // 2

    # Create a grid of output pixel positions.
    rows = np.arange(H)[:, None]
    columns = np.arange(W)[None, :]

    # Local sample index for every output pixel.
    j = columns - starts[:, None]

    # Only columns inside each scanline are sampled.
    inside_triangle = (j >= 0) & (j <= K[:, None])

    # Get the actual row and column of every sample.
    sample_rows, sample_columns = np.nonzero(inside_triangle)

    sample_j = j[sample_rows, sample_columns]

    # Progress along each scanline.
    tx = sample_j / K[sample_rows]

    # Calculate all 3D sample positions at once.
    points = (
        a1[sample_rows]
        + tx[:, None] * differences[sample_rows]
    )

    # Keep the same continuous-coordinate boundary policy.
    bounds = np.asarray(volume.shape) - 1

    valid = np.all(
        (points >= 0) & (points <= bounds),
        axis=1
    )

    valid_points = points[valid]

    # Nearest-neighbor sampling.
    indices = np.floor(
        valid_points + 0.5
    ).astype(np.intp)

    values = volume[
        indices[:, 0],
        indices[:, 1],
        indices[:, 2]
    ]

    # Store the samples in their original output positions.
    E[
        sample_rows[valid],
        sample_columns[valid]
    ] = values

    return E




def project_trapezoid(volume, a1, a2, b, c):
    """Fully vectorized isosceles trapezoid projection."""

    if volume.ndim != 3:
        raise ValueError("Volume must be 3-dimensional")

    # Convert vertices to NumPy arrays.
    a1, a2, b, c = [
        np.asarray(p, dtype=float)
        for p in (a1, a2, b, c)
    ]

    if any(
        p.shape != (3,) or not np.all(np.isfinite(p))
        for p in (a1, a2, b, c)
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

    if abs(left_length - right_length) >= GEOMETRY_EPS:
        raise ValueError("Trapezoid legs must have equal length")

    # Bases must be parallel and point in the same direction.
    if (
        np.linalg.norm(np.cross(top, bottom))
        > 1e-6 * top_length * bottom_length
        or np.dot(top, bottom) <= 0
    ):
        raise ValueError("Trapezoid bases must be parallel")

    # Validate nonzero area.
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

     # The first base must not be longer than the second base.
    # Equal-length bases are allowed by the assignment.
    if top_length > bottom_length:
        raise ValueError(
            "First trapezoid base must not exceed second base"
        )

    # Calculate output dimensions.
    N = int(np.ceil(left_length))
    H = N + 1
    W = int(np.ceil(max(top_length, bottom_length))) + 1

    E = np.zeros((H, W), dtype=volume.dtype)

    # Calculate ALL scanline endpoints simultaneously.
    ty = np.arange(H) / N

    p1 = a1 + ty[:, None] * left_leg
    p2 = a2 + ty[:, None] * right_leg

    # Calculate every scanline's length and sample count.
    differences = p2 - p1

    d12 = np.linalg.norm(differences, axis=1)
    K = np.maximum(1, np.ceil(d12).astype(np.intp))

    # Center all scanlines.
    starts = (W - (K + 1)) // 2

    # Create a grid of output pixel positions.
    columns = np.arange(W)[None, :]

    # Calculate local sample indices for every row.
    j = columns - starts[:, None]

    # Identify the pixels belonging to the trapezoid.
    inside_trapezoid = (j >= 0) & (j <= K[:, None])

    # Get row/column indices of all sampling locations.
    sample_rows, sample_columns = np.nonzero(inside_trapezoid)

    sample_j = j[sample_rows, sample_columns]

    # Calculate progress across each scanline.
    tx = sample_j / K[sample_rows]

    # Generate ALL 3D sampling positions at once.
    sample_points = (
        p1[sample_rows]
        + tx[:, None] * differences[sample_rows]
    )

    # Identify samples inside the volume.
    bounds = np.asarray(volume.shape) - 1

    valid = np.all(
        (sample_points >= 0)
        & (sample_points <= bounds),
        axis=1
    )

    valid_points = sample_points[valid]

    # Convert continuous positions to voxel indices.
    indices = np.floor(
        valid_points + 0.5
    ).astype(np.intp)

    # Read voxel values in one NumPy operation.
    values = volume[
        indices[:, 0],
        indices[:, 1],
        indices[:, 2]
    ]

    # Store the values at the correct 2D positions.
    E[
        sample_rows[valid],
        sample_columns[valid]
    ] = values

    return E
