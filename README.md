# I2SE Ex1 – 3D Volume Plane Projection

## 1. Project Overview

This project is part of the Introduction to Software Engineering course.

The objective is to design and implement an efficient algorithm that generates 2D images from arbitrary plane sections of 3D volumetric data.

The project focuses on software design, correctness, robustness, testing, and runtime performance.

**Programming Language:** Python

## 2. Problem Definition

Given:

- A 3D matrix `M` of dimensions `sx × sy × sz`, containing unsigned integer values of 8, 16, or 32 bits.
- A plane defined by three or four points in 3D space.

The system should generate a 2D matrix representing the sampled volumetric data on the specified plane.

The initial implementation will focus on an isosceles triangle defined by three points `a`, `b`, and `c`, satisfying:

`dist(a,b) = dist(a,c)`

The implementation will later be extended to support an isosceles trapezoid defined by four points.

## 3. Project Scope

The planned system will:

- Load volumetric data from NRRD files.
- Read plane coordinates from CSV files.
- Compute 2D projections for triangular and trapezoidal regions.
- Handle sampling points outside the volume.
- Generate an MP4 video containing one frame for each plane specified in the CSV file, preserving their order.
- Measure runtime performance and evaluate correctness.

## 4. Requirements

The system will be implemented in Python.

The required volume dimensions satisfy:

`1 ≤ sx, sy, sz < 1024`

Performance goals for a volume of size `500 × 500 × 500`:

- Minimum required performance: more than 30 FPS.
- Expected performance target: approximately 100 FPS or higher.

The implementation should be correct, stable, and efficient.

## 5. Development Plan

1. Define software requirements (SRS).
2. Design and document the projection algorithm.
3. Select NRRD test datasets.
4. Define a testing strategy.
5. Implement triangular projection.
6. Extend the implementation to trapezoidal projection.
7. Implement CSV input and MP4 generation.
8. Evaluate performance and document experiment results.

## 6. Project Status

**Current status:** Initial project setup and requirements definition.

Implementation and performance testing have not yet been completed.