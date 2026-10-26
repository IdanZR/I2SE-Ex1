# Ex1 – Experiment and Results

## 1. Experiment Objective

The objective of this experiment was to implement, validate, and optimize a 3D volume projection algorithm supporting isosceles triangular and trapezoidal regions.

The implementation reads NRRD medical imaging data, extracts 2D projections according to plane definitions supplied in a CSV file, and generates an MP4 video.

The experiment also evaluates the performance improvements achieved by replacing Python sampling loops with NumPy vectorized operations.

## 2. Datasets

### 2.1 Real MRI Dataset

The medical imaging dataset used for functional testing was `MRHead_1.nrrd`, referenced in the assignment.

| Property | Value |
|---|---|
| Volume dimensions | 256 × 256 × 130 |
| Total voxels | 8,519,680 |
| Data type | int16 |
| Minimum intensity | 0 |
| Maximum intensity | 279 |
| Encoding | gzip |

The MRI volume was successfully loaded using `pynrrd` and visualized in 3D Slicer.

### 2.2 Synthetic Performance Dataset

For performance measurements, a synthetic volume was generated directly in memory.

| Property | Value |
|---|---|
| Volume dimensions | 500 × 500 × 500 |
| Total voxels | 125,000,000 |
| Data type | uint8 |
| Voxel intensity | 100 |
| Approximate voxel storage | 125 MB |

The constant intensity allowed the benchmark to focus on projection computation rather than image complexity.

## 3. Benchmark Methodology

Each benchmark consisted of:

1. Creating the synthetic 3D volume.
2. Executing one warm-up projection.
3. Executing 20 timed projections.
4. Measuring runtime with `time.perf_counter()`.
5. Calculating average runtime and projection throughput in FPS.

FPS was calculated as:

$$
FPS = \frac{1}{\text{Average Runtime in Seconds}}
$$

Timing included the projection function itself, including its geometric validation and output allocation.

NRRD loading, CSV parsing, MP4 encoding, and video playback were excluded.

The triangle and trapezoid benchmarks used different plane geometries, so their throughput values should not be interpreted as a direct comparison under identical workloads.

## 4. Triangle Performance

The triangle benchmark used the following vertices:

```text
a = (250, 180, 100)
b = (250, 330, 100)
c = (250, 180, 250)
```

The resulting projection dimensions were 150 × 214.

### 4.1 Optimization Stages

| Implementation | Average Runtime | Average FPS |
|---|---:|---:|
| Original Python loops | 236.14 ms | 4.23 |
| NumPy vectorization per scanline | 12.23 ms | 81.78 |
| Fully vectorized NumPy | **6.54 ms** | **152.92** |

### 4.2 Final Triangle Benchmark

| Metric | Result |
|---|---:|
| Average runtime | 6.54 ms |
| Minimum runtime | 4.97 ms |
| Maximum runtime | 10.94 ms |
| Average FPS | 152.92 |
| Above 30 FPS | Yes |
| Above 100 FPS | Yes |

The final triangle implementation achieved approximately **36.2× higher projection throughput** than the original implementation.

## 5. Trapezoid Performance

The trapezoid benchmark used the following vertices:

```text
a1 = (250, 200, 100)
a2 = (250, 300, 100)
b  = (250, 170, 250)
c  = (250, 330, 250)
```

The resulting projection dimensions were 154 × 161.

### 5.1 Optimization Stages

| Implementation | Average Runtime | Average FPS |
|---|---:|---:|
| Original Python loops | 285.59 ms | 3.50 |
| NumPy vectorization per scanline | 9.59 ms | 104.26 |
| Fully vectorized NumPy | **7.01 ms** | **142.59** |

### 5.2 Final Trapezoid Benchmark

| Metric | Result |
|---|---:|
| Average runtime | 7.01 ms |
| Minimum runtime | 5.89 ms |
| Maximum runtime | 9.74 ms |
| Average FPS | 142.59 |
| Above 30 FPS | Yes |
| Above 100 FPS | Yes |

The final trapezoid implementation achieved approximately **40.7× higher projection throughput** than the original implementation.

## 6. Optimization Approach

The original implementation used nested Python loops to calculate sampling positions and retrieve individual voxel values.

Two optimization stages were applied.

### Stage 1 – Scanline Vectorization

The inner Python loop was replaced with NumPy array operations that processed all sampling points of a scanline together.

### Stage 2 – Full Vectorization

The outer Python loop was also removed.

The final implementation computes scanline endpoints, sampling positions, validity masks, and voxel indices through NumPy batch operations.

This significantly reduces Python interpreter overhead while preserving the intended mathematical sampling procedure.

Full vectorization increases temporary memory usage, but provided better runtime performance in the measured scenarios.

## 7. Functional Test Results

The following tests were executed successfully during development.

| Test | Result |
|---|---|
| Constant-volume triangle projection | Passed |
| Coordinate-encoded triangle projection | Passed |
| Constant-volume trapezoid projection | Passed |
| Out-of-bounds voxel sampling | Passed |
| Valid boundary voxel sampling | Passed |
| Degenerate triangle rejection | Passed |
| Non-isosceles triangle rejection | Passed |
| NRRD loading and metadata inspection | Passed |
| CSV parsing | Passed |
| MP4 generation | Passed |

The application successfully generated an MP4 containing three projection frames in CSV order:

1. Triangle
2. Trapezoid
3. Triangle

The automated tests were confirmed during development. Final benchmark measurements were also completed for the fully vectorized versions.

## 8. Integration Demonstration

The application was executed using:

```bash
python Ex0.py data/MRHead_1.nrrd planes.csv output.mp4
```

The application successfully:

- Loaded the NRRD volume.
- Read three plane definitions from the CSV.
- Generated triangle and trapezoid projections.
- Converted the output matrices into video-compatible image frames.
- Created an MP4 file.

The MP4 uses a display frame rate of 2 FPS.

This display rate is independent of the projection throughput measured in the benchmarks.

Each CSV row produces one output frame.

## 9. Known Limitations

- Nearest-neighbor voxel sampling may cause aliasing and repeated pixel values.
- Projection coordinates are specified in voxel-index space rather than physical MRI coordinates.
- The current trapezoid validation excludes parallelograms.
- Full vectorization requires additional temporary memory proportional to the output image dimensions.
- Benchmark measurements were performed using specific geometries and a synthetic constant-value volume.
- Performance may differ across hardware, volume layouts, projection sizes, and orientations.
- File-loading and video-encoding times were excluded from the performance benchmark.
- The available tests do not exhaustively cover every possible malformed input or geometric configuration.

## 10. Conclusion

The project successfully implemented triangular and trapezoidal projection algorithms for 3D medical imaging volumes.

Both algorithms were optimized using NumPy vectorization.

The final measured performance was:

| Algorithm | Average Runtime | Average FPS |
|---|---:|---:|
| Triangle | 6.54 ms | **152.92** |
| Trapezoid | 7.01 ms | **142.59** |

Both implementations exceeded the assignment's minimum 30 FPS requirement and the approximate 100 FPS performance target in the tested benchmark scenarios.

The experiment demonstrates that full NumPy vectorization can substantially improve projection performance without changing the underlying geometric sampling approach.

## 11. Reproducing the Experiment

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run functional tests:

```bash
python test_projection.py
python test_coordinates.py
python test_trapezoid.py
python test_edge_cases.py
```

Run performance benchmarks:

```bash
python benchmark.py
python benchmark_trapezoid.py
```

Generate the demonstration video:

```bash
python Ex0.py data/MRHead_1.nrrd planes.csv output.mp4
```

The MRI dataset must be obtained separately and placed in the `data` directory.