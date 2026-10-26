# Ex1 – Experiment and Results

## 1. Objective

Implement and evaluate a 3D volume projection algorithm for isosceles triangular and trapezoidal regions.

The program reads NRRD volume data and CSV plane definitions and generates an MP4 video containing one projection frame per CSV row.

## 2. Datasets

### MRI Dataset

- File: `MRHead_1.nrrd`
- Shape: 256 × 256 × 130
- Data type: int16
- Intensity range: 0–279
- Encoding: gzip

The MRI was successfully loaded in Python and visualized using 3D Slicer.

### Performance Dataset

- Shape: 500 × 500 × 500
- Data type: uint8
- Total voxels: 125,000,000
- All voxel values: 100

This synthetic dataset was used for reproducible timing measurements.

## 3. Benchmark Methodology

Each benchmark performed one warm-up projection followed by 20 timed projections.

Timing used `time.perf_counter()`.

The reported FPS represents projection computation throughput and excludes NRRD loading, CSV parsing, video encoding, and display.

$$
FPS = \frac{1}{\text{Average Runtime in Seconds}}
$$

The triangle and trapezoid benchmarks used different projection geometries, so their FPS values are not a direct comparison of algorithm efficiency under identical workloads.

## 4. Triangle Performance

| Implementation | Average Time | FPS |
|---|---:|---:|
| Original Python loops | 236.14 ms | 4.23 |
| Vectorized per scanline | 12.23 ms | 81.78 |
| Fully vectorized NumPy | 6.54 ms | **152.92** |

The final triangle implementation achieved approximately **36.2×** the throughput of the original version.

For the fully vectorized implementation:

- Minimum time: 4.97 ms
- Maximum time: 10.94 ms
- Projection dimensions: 150 × 214

## 5. Trapezoid Performance

| Implementation | Average Time | FPS |
|---|---:|---:|
| Original Python loops | 285.59 ms | 3.50 |
| Vectorized per scanline | 9.59 ms | 104.26 |
| Fully vectorized NumPy | 7.01 ms | **142.59** |

The final trapezoid implementation achieved approximately **40.7×** the throughput of the original version.

For the fully vectorized implementation:

- Minimum time: 5.89 ms
- Maximum time: 9.74 ms
- Projection dimensions: 154 × 161

## 6. Functional Testing

The following automated tests were reported as passing:

| Test | Result |
|---|---|
| Basic triangle projection | Passed |
| Triangle coordinate sampling | Passed on the scanline-vectorized implementation |
| Trapezoid projection | Passed on the scanline-vectorized implementation |
| Out-of-bounds voxel sampling | Passed |
| Valid boundary voxel | Passed |
| Degenerate triangle rejection | Passed |
| Non-isosceles triangle rejection | Passed |

The automated tests should be rerun after the final full-vectorization changes to both projection functions.

## 7. Integration Demonstration

The application was executed using:

```bash
python Ex0.py data/MRHead_1.nrrd planes.csv output.mp4
```

The CSV contained three entries:

1. Triangle
2. Trapezoid
3. Triangle

The program successfully generated `output.mp4`.

The video uses a display frame rate of 2 FPS. This value is unrelated to the projection throughput measured in the benchmarks.

Each CSV row produces one unique output frame.

## 8. Limitations

- Nearest-neighbor sampling may produce repeated voxel values and visible aliasing.
- The benchmarks cover specific plane geometries rather than every possible input.
- Additional geometric and malformed-input tests would improve robustness.
- Python and library versions, CPU specifications, and operating-system details should be recorded for reproducibility.
- MP4 generation time was not included in the FPS measurements.

## 9. Conclusion

NumPy vectorization substantially improved the performance of both projection algorithms.

The final measured results were:

- **Triangle: 152.92 FPS**
- **Trapezoid: 142.59 FPS**

Both exceeded the assignment's minimum 30 FPS requirement and the approximate 100 FPS performance target in their respective benchmark scenarios.

The results demonstrate that batch-oriented NumPy operations can significantly reduce Python-loop overhead while preserving the intended projection design.

## 10. Final Verification

Before submission:

- Rerun all automated tests.
- Regenerate and inspect the MP4 using the final code.
- Confirm the README and algorithm documentation match the implementation.
- Record the benchmark environment.
- Commit the final source files and documentation.