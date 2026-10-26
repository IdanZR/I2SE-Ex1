# Software Requirements Specification (SRS)
## I2SE Ex1 – 3D Volume Plane Projection

**Version:** 0.1 – Initial Draft  
**Programming Language:** Python  
**Status:** Requirements Definition

---

## 1. Introduction

### 1.1 Purpose

The purpose of this document is to define the functional and non-functional requirements of a software system that generates 2D plane projections from 3D volumetric data.

The project emphasizes software design, correctness, robustness, and runtime efficiency.

### 1.2 Scope

The system shall:

- Load 3D volumetric data in NRRD format.
- Accept a sequence of planes specified by 3 or 4 points.
- Generate a 2D image for each specified plane.
- Produce an MP4 video containing the generated frames in the input order.
- Support triangular and isosceles trapezoidal projection regions.

## 2. Functional Requirements

**FR-01 – NRRD Input**

The system shall read a 3D volumetric matrix from an NRRD file.

**FR-02 – Supported Data Types**

The system shall support unsigned integer voxel values of 8, 16, and 32 bits.

**FR-03 – Volume Dimensions**

The system shall support dimensions satisfying:

`1 ≤ sx, sy, sz < 1024`

**FR-04 – Plane Definition**

The system shall accept plane regions defined by 3 or 4 points in 3D space.

**FR-05 – Triangular Projection**

The system shall support an isosceles triangle defined by points `a`, `b`, and `c`, satisfying:

`dist(a,b) = dist(a,c)`

**FR-06 – Trapezoidal Projection**

The system shall support an isosceles trapezoid represented by four points, consistent with the assignment's geometric definition.

**FR-07 – Projection Output**

The system shall calculate a 2D matrix of sampled voxel values corresponding to the specified projection region.

**FR-08 – Out-of-Bounds Sampling**

Sampling a point outside the input volume shall return a value of zero.

**FR-09 – CSV Input**

The system shall read an ordered list of plane coordinate definitions from a CSV file.

**FR-10 – MP4 Generation**

The system shall generate an MP4 file containing one frame per input plane, preserving the CSV order.

**FR-11 – Command-Line Interface**

The system shall provide a command-line entry point accepting the input NRRD path, input CSV path, and output MP4 path.

Example:

`python main.py input.nrrd planes.csv output.mp4`

## 3. Non-Functional Requirements

**NFR-01 – Runtime Performance**

For a volume of size 500 × 500 × 500 bytes:

- More than 30 projection frames per second is mandatory.
- Approximately 100 FPS or higher is the expected performance target.

**NFR-02 – Correctness**

The implementation shall be tested against known synthetic data and expected projection values.

**NFR-03 – Robustness**

The system shall handle invalid input and unsupported configurations without unexpected crashes.

**NFR-04 – Maintainability**

The implementation shall separate data loading, projection computation, and video generation into clearly defined components.

**NFR-05 – Version Control**

The project shall be managed using Git, with frequent meaningful commits.

## 4. Input and Output

### 4.1 Input Files

- `input.nrrd`: a 3D volumetric dataset.
- `planes.csv`: an ordered sequence of coordinate definitions.

### 4.2 Output

- `output.mp4`: a video containing the resulting plane images in the specified order.

## 5. Error Handling

The implementation shall define consistent behavior for:

- Missing or unreadable files.
- Invalid NRRD headers or unsupported data types.
- Invalid CSV records.
- Degenerate geometric configurations.
- Invalid sampling coordinates.
- Failures during video generation.

Invalid input shall produce informative error messages.

## 6. Testing and Acceptance

The testing strategy shall include:

- Synthetic volumes with predictable voxel values.
- Triangular projection correctness tests.
- Trapezoidal projection correctness tests.
- Out-of-bounds sampling tests.
- File input validation tests.
- CSV ordering and MP4 frame-count tests.
- Performance benchmarks using a 500³-byte volume.

## 7. Design Decisions Pending

The following details are not fully specified by the assignment and require explicit design decisions:

1. Exact CSV column structure and four-point ordering.
2. Floating-point sampling policy.
3. Conversion of geometric distances into image dimensions.
4. Treatment of degenerate triangles and trapezoids.
5. Consistent video frame dimensions and output pixel format.
6. Video playback frame rate.
7. Exact benchmarking methodology and hardware environment.

These decisions shall be documented before or during the detailed algorithm design stage.