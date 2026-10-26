# Dataset Documentation – Ex1

**Project:** Introduction to Software Engineering – 3D Volume Plane Projection  
**Status:** Dataset definition and initial validation completed

## 1. Purpose

This document describes the datasets used to develop, test, and benchmark the triangle and trapezoid projection algorithms.

We use two categories of data:

1. **Real MRI data** to demonstrate the projection algorithms on a medical volume.
2. **Synthetic volumes** to verify correctness and measure runtime performance.

## 2. Real MRI Dataset

The primary medical dataset is `MRHead_1.nrrd`, obtained from the sample MRI resource referenced in the assignment.

The file was successfully opened in 3D Slicer and loaded into Python using the `pynrrd` library.

### 2.1 Volume Properties

The following values were obtained by reading the actual NRRD header and inspecting the NumPy array.

| Property | Value |
|---|---|
| Filename | `MRHead_1.nrrd` |
| Format | NRRD |
| Dimensions | 3 |
| Shape | 256 × 256 × 130 |
| Total voxels | 8,519,680 |
| Data type | `int16` |
| NRRD type | `short` |
| Minimum intensity | 0 |
| Maximum intensity | 279 |
| Byte order | Little-endian |
| Encoding | gzip |
| Coordinate space | Left-Posterior-Superior (LPS) |

Although the assignment describes unsigned 8-, 16- and 32-bit values, this sample dataset uses signed 16-bit storage. All observed intensities are nonnegative.

The implementation preserves the source data type during projection.

### 2.2 Spatial Metadata

The NRRD header reports the following space directions:

```text
( 0.000000, 1.000000,  0.000000)
( 0.000000, 0.000000, -1.000000)
(-1.299995, 0.000000, 0.000000)
```

The space origin is:

```text
(86.644897, -133.928604, 116.785698)
```

The directions describe the physical displacement associated with moving by one index along each volume axis.

In this dataset:

- Axis 0 increases toward Posterior by approximately 1 mm.
- Axis 1 increases toward Inferior by approximately 1 mm.
- Axis 2 increases toward Right by approximately 1.3 mm.

The origin specifies the physical position of the voxel at array index `(0, 0, 0)`.

### 2.3 Coordinate Convention

The current implementation reads the NRRD using:

```python
volume, header = nrrd.read(
    file_path,
    index_order="F"
)
```

Projection points are expressed in **voxel-index coordinates**, not physical millimeters.

The volume is accessed as:

```python
volume[x, y, z]
```

CSV plane coordinates must use the same voxel-index convention.

The current application does not automatically convert physical LPS coordinates into array indices.

## 3. Synthetic Correctness Datasets

### 3.1 Constant Volume

A small constant volume is used to test basic output structure.

Example:

```python
volume = np.full(
    (10, 10, 10),
    100,
    dtype=np.int16
)
```

Every valid sample must return 100.

Points outside the volume return zero.

This dataset was used to test both triangle and trapezoid projection.

### 3.2 Coordinate-Encoded Volume

A second synthetic dataset assigns different voxel values according to their coordinates:

```python
volume[x, y, z] = x + 10*y + 100*z
```

For example:

```text
M[2, 3, 1] = 132
```

This makes it possible to verify which voxel was sampled.

The formula is intended for small volumes whose axis indices are below 10.

The coordinate-based triangle test was executed successfully.

## 4. Synthetic Performance Dataset

A larger volume was generated for benchmarking.

| Property | Value |
|---|---|
| Shape | 500 × 500 × 500 |
| Data type | `uint8` |
| Total voxels | 125,000,000 |
| Value of every voxel | 100 |
| Uncompressed voxel storage | Approximately 125 MB |

The volume was generated directly in memory:

```python
volume = np.full(
    (500, 500, 500),
    100,
    dtype=np.uint8
)
```

This dataset was used for triangle and trapezoid performance measurements.

The benchmarks measured projection runtime separately from file loading and video encoding.

## 5. CSV Plane Definitions

The demonstration uses a CSV file named `planes.csv`.

Its columns are:

```csv
type,ax,ay,az,bx,by,bz,cx,cy,cz,dx,dy,dz
```

For a triangle, three vertices are supplied.

For a trapezoid, four vertices are supplied in the order expected by `project_trapezoid`.

The current CSV convention uses:

- `triangle`: A, B, C
- `trapezoid`: A1, A2, B, C

Each CSV row defines one projection frame, and frames are generated in CSV order.

This CSV layout is a project-level design choice.

## 6. Dataset Validation

The following checks were performed:

| Validation | Result |
|---|---|
| Load MRI in 3D Slicer | Passed |
| Read MRI with `pynrrd` | Passed |
| Verify 3D dimensions | Passed |
| Inspect MRI intensity range | Passed |
| Read sample voxel `M[128,128,65]` | Value: 51 |
| Run constant-volume triangle test | Passed |
| Run coordinate-encoded triangle test | Passed |
| Run constant-volume trapezoid test | Passed |
| Generate MP4 from MRI and CSV | Passed |
| Create and benchmark 500³ synthetic volume | Passed |

## 7. Dataset Storage

The MRI dataset is stored locally under:

```text
data/MRHead_1.nrrd
```

Large NRRD files are excluded from normal Git tracking through `.gitignore`.

The synthetic datasets are generated programmatically, so separate large binary files do not need to be committed.

The project repository should contain the source code, CSV examples, test scripts and documentation.

## 8. Known Limitations

- The MRI data uses anisotropic physical spacing: approximately 1 × 1 × 1.3 mm.
- The current sampling algorithm operates in voxel-index coordinates.
- Nearest-neighbor sampling can introduce visible aliasing.
- The synthetic correctness datasets do not reproduce all properties of medical images.
- Benchmark results depend on the computer hardware and selected plane geometry.
- Additional datasets with other voxel data types and coordinate orientations would improve test coverage.

## 9. Summary

The project uses a real MRI volume for demonstration, small synthetic volumes for correctness testing, and a large synthetic volume for performance evaluation.

This combination allows the projection algorithm to be evaluated for both functional correctness and runtime efficiency.