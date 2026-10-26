# 3D Volume Plane Projection – I2SE Ex1

A Python implementation of a 3D medical volume projection algorithm, developed for the Introduction to Software Engineering (OOP/OOD) course.

The application extracts 2D projections from NRRD volumes using triangular and trapezoidal regions, then combines them into an MP4 video.

Both projection algorithms use fully vectorized NumPy operations for efficient computation.

## Features

- Read 3D medical imaging volumes in NRRD format.
- Generate 2D projections of isosceles triangles and trapezoids.
- Support arbitrary valid orientations in 3D voxel-index space.
- Perform nearest-neighbor voxel sampling.
- Assign zero to samples outside the volume.
- Read projection definitions from CSV.
- Produce an MP4 video with one frame per CSV row.
- Validate geometric inputs.
- Benchmark projection throughput on synthetic 3D data.

## Requirements

- Python 3
- NumPy
- pynrrd
- Pillow (used by the standalone MRI PNG demonstration)
- imageio
- imageio-ffmpeg

Install the dependencies using:

```bash
python -m pip install -r requirements.txt
```

A virtual environment is recommended.

On Windows:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Quick Start

### 1. Obtain the MRI Dataset

Download the NRRD sample dataset referenced in the assignment.

The implementation was tested using `MRHead_1.nrrd`, with dimensions `256 × 256 × 130`.

Place the file at:

```text
data/MRHead_1.nrrd
```

The MRI file is not included in the Git repository.

Additional dataset information is available in [DATASET.md](DATASET.md).

### 2. Prepare the CSV

The repository includes an example file named `planes.csv`.

Its header is:

```csv
type,ax,ay,az,bx,by,bz,cx,cy,cz,dx,dy,dz
```

A triangle uses three points: `a`, `b`, `c`.

A trapezoid uses four points in the order `a1`, `a2`, `b`, `c`. In the CSV, these correspond to the `a`, `b`, `c`, `d` fields, respectively.

Example:

```csv
type,ax,ay,az,bx,by,bz,cx,cy,cz,dx,dy,dz
triangle,128,70,25,128,170,25,128,70,125,,,
trapezoid,128,80,40,128,120,40,128,60,100,128,140,100
```

All coordinates are expressed in **voxel-index coordinates**, not physical MRI coordinates in millimeters.

Each CSV row generates one projection frame.

### 3. Generate the MP4

Run:

```bash
python Ex0.py data/MRHead_1.nrrd planes.csv output.mp4
```

Or using the Windows virtual environment:

```powershell
.\.venv\Scripts\python.exe Ex0.py .\data\MRHead_1.nrrd planes.csv output.mp4
```

The application reads the volume, computes projections in CSV order, normalizes their intensities for grayscale display, and encodes an MP4.

The example video is encoded at 2 FPS for playback. This is separate from the computational performance measurements.

## Project Structure

| File | Description |
|---|---|
| `Ex0.py` | Main command-line application and MP4 generation |
| `projection.py` | Triangle and trapezoid projection algorithms |
| `planes.csv` | Example input plane definitions |
| `inspect_nrrd.py` | Inspect NRRD volume data and metadata |
| `demo_mri.py` | Create a standalone PNG demonstration |
| `benchmark.py` | Triangle performance benchmark |
| `benchmark_trapezoid.py` | Trapezoid performance benchmark |
| `test_projection.py` | Basic triangle tests |
| `test_coordinates.py` | Coordinate-based sampling test |
| `test_trapezoid.py` | Basic trapezoid tests |
| `test_edge_cases.py` | Boundary and invalid triangle tests |
| `requirements.txt` | Python dependencies |

## Algorithm

The algorithm uses a scanline-based method:

1. Validate the input shape and its geometry.
2. Interpolate the endpoints of the scanlines along the region's sides.
3. Calculate sampling positions across each scanline.
4. Retrieve voxel intensities using nearest-neighbor sampling.
5. Center the sampled values in a rectangular 2D output matrix.

The triangle and trapezoid implementations use full NumPy vectorization to process all active sampling points without nested Python sampling loops.

For mathematical derivations, implementation decisions, complexity analysis and limitations, see [ALGORITHM.md](ALGORITHM.md).

## Testing

Run the functional tests:

```bash
python test_projection.py
python test_coordinates.py
python test_trapezoid.py
python test_edge_cases.py
```

The tests verify basic output geometry, selected voxel values, boundary behavior, and invalid triangle inputs.

For the detailed testing plan, see [TESTING.md](TESTING.md).

## Performance

Benchmarks were performed using a synthetic `500 × 500 × 500` uint8 volume, with one warm-up projection and 20 timed projections per test.

| Algorithm | Original Python | Fully Vectorized NumPy |
|---|---:|---:|
| Triangle | 4.23 FPS | **152.92 FPS** |
| Trapezoid | 3.50 FPS | **142.59 FPS** |

Both final implementations exceeded 100 FPS in the measured benchmark scenarios.

The performance figures measure projection computation only, excluding file loading and MP4 encoding. The triangle and trapezoid tests used different projection geometries.

Reproduce the benchmarks using:

```bash
python benchmark.py
python benchmark_trapezoid.py
```

For full experimental results, see [RESULTS.md](RESULTS.md).

## Documentation

- [SRS.md](SRS.md) – Software requirements specification
- [ALGORITHM.md](ALGORITHM.md) – Mathematical and implementation design
- [DATASET.md](DATASET.md) – MRI and synthetic datasets
- [TESTING.md](TESTING.md) – Testing strategy
- [RESULTS.md](RESULTS.md) – Benchmarks and experiment results

## Known Limitations

- Nearest-neighbor sampling may introduce aliasing and repeated voxel values.
- Plane coordinates must be provided in voxel-index space.
- The current trapezoid validation excludes parallelograms.
- Very large projections may require substantial temporary memory because of full vectorization.
- Benchmarked throughput depends on hardware and the selected plane geometry.
- The CSV format is a project-defined convention and is not automatically compatible with other formats.

## Summary

This project demonstrates the complete workflow of loading a medical volume, computing geometric 2D projections, validating results, optimizing performance through NumPy vectorization, and exporting the resulting frames to MP4.