# Ex1 – Experiment and Results

## 1. Experiment Objective

The objective was to implement a 3D volume projection algorithm supporting triangular and trapezoidal regions, generate 2D images from NRRD data, and evaluate the runtime performance of the implementation.

The initial triangle implementation was compared with an optimized NumPy-vectorized implementation.

## 2. Dataset

### Real MRI Volume

The dataset used for functional demonstrations was `MRHead_1.nrrd`.

| Property | Value |
|---|---|
| Dimensions | 256 × 256 × 130 |
| Number of voxels | 8,519,680 |
| Data type | int16 |
| Minimum intensity | 0 |
| Maximum intensity | 279 |
| Encoding | gzip |

The volume was successfully loaded using `pynrrd` and inspected in 3D Slicer.

### Synthetic Benchmark Volume

A synthetic 3D volume was generated with the following properties:

| Property | Value |
|---|---|
| Dimensions | 500 × 500 × 500 |
| Data type | uint8 |
| Number of voxels | 125,000,000 |
| Voxel intensity | 100 |

The benchmark used a triangular plane with vertices:

```text
a = (250, 180, 100)
b = (250, 330, 100)
c = (250, 180, 250)
```

The output projection dimensions were 150 × 214.

## 3. Benchmark Methodology

The program executed one warm-up projection followed by 20 timed projections.

Runtime was measured using Python's `time.perf_counter()`.

Only projection computation was measured. NRRD loading, CSV parsing, image normalization, and MP4 encoding were excluded.

FPS was calculated as:

$$
FPS=\frac{1}{\text{average projection time in seconds}}
$$

## 4. Benchmark Results

| Metric | Original Python | NumPy Vectorized |
|---|---:|---:|
| Average runtime | 236.14 ms | 12.23 ms |
| Minimum runtime | 153.25 ms | 9.22 ms |
| Maximum runtime | 287.82 ms | 17.24 ms |
| Average FPS | 4.23 | 81.78 |
| Above 30 FPS | No | Yes |
| At least 100 FPS | No | No |

The optimized triangle implementation achieved approximately **19.3× higher FPS** than the original implementation.

The improvement was obtained by processing all sampling locations along each scanline with NumPy arrays instead of executing a Python loop for every sample.

## Additional Trapezoid Benchmark

| Metric | NumPy Vectorized |
|---|---:|
| Average runtime | 9.59 ms |
| Minimum runtime | 6.23 ms |
| Maximum runtime | 21.12 ms |
| Average FPS | 104.26 |
| Above 30 FPS | Yes |
| At least 100 FPS | Yes |

The optimized trapezoid implementation achieved 104.26 FPS in the measured benchmark scenario, exceeding both the minimum 30 FPS requirement and the approximate 100 FPS target.

## 5. Functional Test Results

The following tests passed:

| Test | Result |
|---|---|
| Constant-volume triangle projection | Passed |
| Coordinate-encoded triangle projection | Passed |
| Constant-volume trapezoid projection | Passed |
| NRRD loading and inspection | Passed |
| CSV parsing of three plane definitions | Passed |
| MP4 file generation | Passed |

The full application generated an MP4 containing three frames: two triangular projections and one trapezoidal projection.

Visual inspection and broader edge-case validation should be documented separately before final submission.

## 6. Limitations

- The optimized implementation currently applies only to triangle projection; trapezoid projection still uses per-sample Python loops.
- Nearest-neighbor sampling may introduce aliasing and repeated voxel values.
- The benchmark used one fixed triangular geometry and a constant synthetic volume.
- The benchmark was not performed on multiple hardware platforms.
- MP4 output uses a fixed display frame rate, independently of the measured projection FPS.
- More automated tests are required for malformed inputs, boundary coordinates, and additional geometric cases.

## 7. Conclusion

NumPy vectorization substantially improved the performance of the triangle projection algorithm.

In the measured scenario, throughput increased from 4.23 FPS to 81.78 FPS, exceeding the assignment's minimum 30 FPS threshold for that scenario.

The results do not yet establish that all supported shapes and input configurations meet the performance requirement.

## 8. Remaining Work

- Run additional boundary and invalid-input tests.
- Verify video playback and frame ordering.
- Benchmark and optionally optimize trapezoid projection.
- Record hardware information and additional benchmark scenarios.
- Finalize the demonstration and repository documentation.