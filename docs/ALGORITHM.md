# Ex1 – 3D Volume Plane Projection Algorithm

**Course:** Introduction to Software Engineering (OOP/OOD)  
**Language:** Python  
**Implementation:** Fully vectorized NumPy  
**Version:** 1.0

---

## 1. Algorithm Overview

The goal of this project is to extract a two-dimensional image from a specified region of a three-dimensional volume.

The input volume is a 3D matrix:

$$
M[x,y,z]
$$

Each element represents a voxel containing an intensity value.

The output is a 2D matrix:

$$
E[y,x]
$$

Each output pixel is assigned an intensity sampled from a corresponding 3D location.

The implementation supports:

- Isosceles triangular regions defined by three points.
- Isosceles trapezoidal regions defined by four points.
- Nearest-neighbor voxel sampling.
- Sampling positions outside the volume, which produce zero.
- Full NumPy vectorization for efficient projection computation.

The geometric algorithm follows the scanline approach described in the assignment, with adaptations for non-integer distances, discrete output coordinates, and batch processing.

---

## 2. The Main Idea: Scanlines

A scanline is a line segment connecting two endpoints within the desired geometric region.

For each scanline, the algorithm determines multiple 3D sampling positions and copies the corresponding voxel values into a row of the output image.

There are two important movements:

**Movement 1: Along the region's sides.**

This determines which scanline we are processing.

**Movement 2: Across the current scanline.**

This determines which 3D points we sample.

A useful mental model:

- `ty` determines which scanline is being processed.
- `tx` determines progress along that scanline.
- `p` represents a 3D sampling position.
- `(y, x)` represents the corresponding output pixel.

A scanline's geometric length is not necessarily equal to its number of sampled pixels.

---

## 3. Triangle Geometry

### 3.1 Input Points

The isosceles triangle is defined by three 3D points:

$$
a,b,c\in\mathbb{R}^3
$$

The two legs must have approximately equal lengths:

$$
D_{ab}=\|b-a\|
$$

$$
D_{ac}=\|c-a\|
$$

$$
D_{bc}=\|c-b\|
$$

The isosceles condition is:

$$
D_{ab}\approx D_{ac}
$$

The triangle must also have nonzero area.

The implementation checks this using the cross product of its two leg vectors.

### 3.2 Calculating Displacement Vectors

Define:

$$
ab=b-a
$$

$$
ac=c-a
$$

The vector `ab` represents the complete displacement from `a` to `b`.

Similarly, `ac` represents the complete displacement from `a` to `c`.

These vectors contain both direction and distance information.

---

## 4. Choosing the Number of Triangle Rows

The number of sampling intervals along the legs is:

$$
N=\lceil D_{ab}\rceil
$$

The output height is:

$$
H=N
$$

The output width is:

$$
W=\lceil D_{bc}\rceil+1
$$

**Why do we use `ceil`?**

Suppose a leg has length 4.3.

If we advance exactly one geometric unit per step, five steps would extend beyond the endpoint.

Instead, we divide the original segment into five equal intervals:

$$
N=5
$$

Each interval has length:

$$
\frac{4.3}{5}=0.86
$$

Thus, rounding upward determines the number of intervals without increasing the original geometric length.

---

## 5. Sampling Along the Triangle Legs

For each row:

$$
y=0,1,\ldots,N-1
$$

define normalized progress:

$$
t_y=\frac{y+1}{N}
$$

The two endpoints of the current scanline are:

$$
a_1=a+t_y(b-a)
$$

$$
a_2=a+t_y(c-a)
$$

### 5.1 Why These Formulas Work

The expression:

$$
b-a
$$

represents the complete displacement from `a` to `b`.

Multiplication by `ty` gives the required fraction of that displacement.

Adding `a` gives the resulting position.

For example, if:

$$
t_y=0.4
$$

then `a1` lies 40% of the way from `a` to `b`.

The same progress value is used for `a2`, so both endpoints remain at corresponding positions on the triangle's legs.

### 5.2 Connection to Linear Algebra

The formula can be rewritten:

$$
a_1=a+t_y(b-a)
$$

$$
a_1=(1-t_y)a+t_yb
$$

Because:

$$
0<t_y\le1
$$

this is a convex combination.

Consequently, `a1` stays on the segment connecting `a` and `b`.

The same reasoning applies to `a2`.

### 5.3 Why We Calculate From the Original Vertices

We calculate every row's endpoints using the original point `a`.

We do not repeatedly add the cumulative progress value to the previous endpoint.

This avoids incorrect accumulation and ensures that the final row reaches the original vertices:

$$
a_1=b,\qquad a_2=c
$$

---

## 6. Why Triangle Scanlines Become Wider

The current scanline length is:

$$
d_{12}=\|a_2-a_1\|
$$

Substituting the endpoint definitions:

$$
a_2-a_1=t_y(c-b)
$$

Therefore:

$$
d_{12}=t_yD_{bc}
$$

This also follows from similar triangles.

For example, if the base length is 10 and progress is 40%:

$$
d_{12}=0.4\cdot10=4
$$

This means the current scanline has a geometric length of four units.

It does not necessarily mean it contains exactly four pixels.

---

## 7. Sampling Across a Triangle Scanline

For the current scanline, define:

$$
K=\max(1,\lceil d_{12}\rceil)
$$

The sampling indices are:

$$
j=0,1,\ldots,K
$$

Thus, each scanline contains `K + 1` sampling positions.

For each sample:

$$
t_x=\frac{j}{K}
$$

The corresponding 3D sampling position is:

$$
p_j=a_1+t_x(a_2-a_1)
$$

### Why Do We Use tx?

`tx` represents normalized progress across the scanline.

- `tx = 0` produces the first endpoint.
- `tx = 0.5` produces the midpoint.
- `tx = 1` produces the second endpoint.

This is the same interpolation principle used for `ty`.

The difference is that `ty` selects a scanline, while `tx` selects a point within the scanline.

---

## 8. Centering Output Scanlines

A triangle occupies a triangular region, but the output matrix is rectangular.

If every sampled row started at output column zero, the region would appear incorrectly aligned.

Therefore, the sampled values must be centered within the output width.

### 8.1 Original Assignment Formula

The assignment uses geometric centering:

$$
x=\frac{D_{bc}-d_{12}}{2}+x_1
$$

The expression:

$$
\frac{D_{bc}-d_{12}}{2}
$$

represents half the unused geometric width.

The loop counter `x1` then advances across the scanline.

### 8.2 Our Discrete Adaptation

Our implementation works with actual numbers of output pixels.

Each scanline has:

$$
K+1
$$

sampling positions.

The left offset is:

$$
start=\left\lfloor\frac{W-(K+1)}{2}\right\rfloor
$$

The output column for sampling index `j` is:

$$
x=start+j
$$

### Example

Suppose the image width is 11 pixels and the current scanline contains five samples.

There are six unused columns.

Three columns remain empty on the left, and three on the right.

The five samples are stored in columns 3 through 7.

For odd numbers of unused columns, the implementation permits a one-pixel imbalance between the two sides.

---

## 9. Trapezoid Geometry

### 9.1 Four Input Points

The trapezoid is defined by:

$$
a_1,a_2,b,c\in\mathbb{R}^3
$$

The upper base connects `a1` to `a2`.

The lower base connects `b` to `c`.

The two legs connect:

- `a1` to `b`.
- `a2` to `c`.

Unlike the triangle, the first scanline already has nonzero length.

### 9.2 Geometric Validation

The implementation validates:

1. All vertices contain three finite coordinates.
2. All required edges have positive length.
3. The two legs have approximately equal lengths.
4. The two bases are parallel and point in the same direction.
5. The four vertices are coplanar.
6. The trapezoid has nonzero area.
7. The bases have different lengths.

The final restriction excludes parallelograms in the current implementation.

This is a project-specific geometric validation decision.

---

## 10. Sampling Across the Trapezoid

Define the leg vectors:

$$
L=b-a_1
$$

$$
R=c-a_2
$$

Let:

$$
N=\lceil\|L\|\rceil
$$

The output includes the starting and ending bases:

$$
H=N+1
$$

For every row:

$$
y=0,1,\ldots,N
$$

define:

$$
t_y=\frac{y}{N}
$$

The scanline endpoints are:

$$
p_1=a_1+t_yL
$$

$$
p_2=a_2+t_yR
$$

At `ty = 0`, the scanline is the first base.

At `ty = 1`, it is the second base.

### 10.1 Scanline Sampling

Calculate:

$$
d_{12}=\|p_2-p_1\|
$$

$$
K=\max(1,\lceil d_{12}\rceil)
$$

Then:

$$
t_x=\frac{j}{K}
$$

$$
p=p_1+t_x(p_2-p_1)
$$

### 10.2 Output Size and Centering

The trapezoid's output width is based on the longer base:

$$
W=\lceil\max(D_{top},D_{bottom})\rceil+1
$$

Each scanline is centered using:

$$
start=\left\lfloor\frac{W-(K+1)}{2}\right\rfloor
$$

The output column is:

$$
x=start+j
$$

The triangle and trapezoid therefore share the same basic sampling and centering principles.

---

## 11. Nearest-Neighbor Volume Sampling

The algorithm produces sampling points containing real-valued coordinates:

$$
p=(p_x,p_y,p_z)
$$

NumPy array indices must be integers.

Therefore, the implementation uses nearest-neighbor sampling.

For each coordinate, it calculates the index using the equivalent of:

```python
index = floor(coordinate + 0.5)
```

For example:

```text
(2.2, 3.7, 1.1) -> (2, 4, 1)
```

The voxel value is then obtained from:

```python
volume[2, 4, 1]
```

If the original continuous sampling position lies outside the volume-index boundaries, the output value remains zero.

The current implementation uses voxel-index coordinates and does not automatically transform physical MRI coordinates into array indices.

---

# 12. Full NumPy Vectorization

## 12.1 The Original Performance Problem

The first implementation used two nested Python loops:

```python
for y in range(H):
    for j in range(K + 1):
        # Calculate a point
        # Sample one voxel
        # Write one pixel
```

Although this approach is easy to understand, it performs many Python operations for every pixel.

Our initial benchmarks showed that this implementation was too slow for the assignment's minimum performance requirement.

## 12.2 Vectorization Per Scanline

The first optimization retained the outer row loop but removed the inner sample loop.

Instead of computing one sample at a time, NumPy generated all sampling positions for one row together.

For example:

```python
tx = np.arange(K + 1) / K
points = a1 + tx[:, None] * (a2 - a1)
```

This significantly reduced Python-loop overhead.

## 12.3 Full Vectorization

The final version also removes the outer row loop.

It generates the endpoints of every scanline simultaneously.

For triangles:

```python
ty = (np.arange(H) + 1) / N

a1 = a + ty[:, None] * ab
a2 = a + ty[:, None] * ac
```

For trapezoids:

```python
ty = np.arange(H) / N

p1 = a1 + ty[:, None] * left_leg
p2 = a2 + ty[:, None] * right_leg
```

Each array now contains the endpoints for all output rows.

---

## 13. How the Final Vectorized Sampling Works

### Step 1 – Calculate Scanline Lengths

For each row, calculate the displacement between its two endpoints.

Then calculate all lengths:

```python
differences = end_points - start_points

d12 = np.linalg.norm(differences, axis=1)
K = np.maximum(1, np.ceil(d12).astype(np.intp))
```

`axis=1` tells NumPy to calculate a separate vector length for each row.

### Step 2 – Calculate Row Offsets

Calculate the centering offset of every scanline:

```python
starts = (W - (K + 1)) // 2
```

`starts[y]` is the output column where row `y` begins.

### Step 3 – Build an Output Coordinate Grid

Create output column coordinates:

```python
columns = np.arange(W)[None, :]
```

Subtract each row's starting offset:

```python
j = columns - starts[:, None]
```

This produces the local sample index associated with each potential output pixel.

### Step 4 – Identify Pixels Inside the Shape

Not every location in the rectangular output belongs to the triangle or trapezoid.

The condition:

```python
inside = (j >= 0) & (j <= K[:, None])
```

creates a Boolean mask.

A value of `True` means the output location belongs to the sampled geometric region.

A value of `False` means it should remain zero.

### Step 5 – Extract Active Pixel Positions

Use:

```python
sample_rows, sample_columns = np.nonzero(inside)
```

This returns the row and column of every active output pixel.

We avoid processing unused background pixels.

### Step 6 – Calculate Every Sampling Point

For each active pixel, calculate its local progress:

```python
sample_j = j[sample_rows, sample_columns]
tx = sample_j / K[sample_rows]
```

Then calculate the corresponding 3D positions:

```python
points = (
    start_points[sample_rows]
    + tx[:, None] * differences[sample_rows]
)
```

The result is one array containing all sampling points for the projection.

### Step 7 – Apply the Volume Boundary Mask

Each point must lie within the volume.

```python
bounds = np.asarray(volume.shape) - 1

valid = np.all(
    (points >= 0) & (points <= bounds),
    axis=1
)
```

Invalid points are excluded from voxel reads.

Their output pixels remain zero.

### Step 8 – Sample the Volume

Convert valid sampling positions to integer indices:

```python
indices = np.floor(
    points[valid] + 0.5
).astype(np.intp)
```

Then sample all voxel values:

```python
values = volume[
    indices[:, 0],
    indices[:, 1],
    indices[:, 2]
]
```

This performs batch indexing through NumPy rather than explicitly calling a Python function for each voxel.

### Step 9 – Populate the Output Image

For triangles, the final implementation writes:

```python
E[
    sample_rows[valid],
    sample_columns[valid]
] = values
```

The trapezoid implementation uses the same principle.

The result is a two-dimensional matrix containing the projection values in their centered positions.

---

## 14. Important NumPy Syntax

### `[:, None]`

Adds an extra array dimension.

For example, an array of shape:

```text
(100,)
```

becomes:

```text
(100, 1)
```

This allows NumPy broadcasting to combine the values with three-component vectors.

### `np.arange(n)`

Creates an array of integer values:

```text
[0, 1, 2, ..., n-1]
```

### `np.nonzero(mask)`

Returns the indices at which a Boolean array is true.

### `np.linalg.norm(..., axis=1)`

Calculates the lengths of multiple vectors in a single operation.

### Boolean Masking

A Boolean mask selects elements according to a condition.

For example:

```python
values = np.array([10, 20, 30])
mask = np.array([True, False, True])

print(values[mask])
```

Output:

```text
[10 30]
```

This is the technique used to skip out-of-volume sampling points.

---

## 15. Algorithm Pseudocode

### 15.1 Triangle Projection

```text
FUNCTION project_triangle(volume, a, b, c):

    Validate volume and triangle

    Calculate ab, ac and edge lengths

    N = ceil(length(ab))
    H = N
    W = ceil(length(c - b)) + 1

    Initialize E as an H x W zero matrix

    Calculate progress ty for every row

    Calculate all scanline endpoints a1 and a2

    Calculate all scanline lengths
    Calculate all interval counts K
    Calculate all centering offsets

    Build the rectangular output coordinate grid

    Identify all pixels inside the triangular region

    Calculate tx for all active pixels

    Calculate all corresponding 3D sampling positions

    Identify positions inside the volume

    Round valid positions to voxel indices

    Retrieve voxel values using NumPy batch indexing

    Store values in their corresponding output pixels

    RETURN E
```

### 15.2 Trapezoid Projection

```text
FUNCTION project_trapezoid(volume, a1, a2, b, c):

    Validate volume and trapezoid geometry

    Calculate the two legs and bases

    N = ceil(length(left_leg))
    H = N + 1
    W = ceil(longest_base_length) + 1

    Initialize E as an H x W zero matrix

    Calculate progress ty for every row

    Calculate all scanline endpoints

    Calculate all scanline lengths
    Calculate all interval counts K
    Calculate all centering offsets

    Build the rectangular output coordinate grid

    Identify all pixels inside the trapezoid

    Calculate tx for all active pixels

    Calculate all corresponding 3D sampling positions

    Identify positions inside the volume

    Round valid positions to voxel indices

    Retrieve voxel values using NumPy batch indexing

    Store values in their corresponding output pixels

    RETURN E
```

---

## 16. Time and Space Complexity

Let:

- `H` be the output height.
- `W` be the output width.
- `P` be the number of active sampling positions.

The vectorized implementation constructs an output coordinate mask of size `H × W` and processes up to `P` sampling positions.

Its overall computational complexity is:

$$
O(HW)
$$

The output image uses:

$$
O(HW)
$$

memory.

The fully vectorized implementation also requires temporary arrays for masks, coordinates, and sampled indices.

Therefore, its total auxiliary memory usage is also bounded by:

$$
O(HW)
$$

excluding the input volume.

**Important:** Vectorization improves execution efficiency by reducing Python overhead. It does not change the overall asymptotic time complexity.

---

## 17. Testing and Validation

The implementation was tested using synthetic volumes and real MRI data.

The tests cover:

- Constant-value volume sampling.
- Triangle projection output dimensions.
- Coordinate-encoded triangle sampling.
- Trapezoid projection output dimensions.
- Out-of-bounds sampling.
- Valid boundary voxels.
- Degenerate triangles.
- Non-isosceles triangles.
- NRRD loading.
- CSV parsing and MP4 generation.

The detailed testing strategy is described in `TESTING.md`.

Additional randomized geometric tests and comparisons against independently calculated reference projections would improve confidence in the implementation.

---

## 18. Performance Results

Performance measurements were performed using a synthetic volume of size:

```text
500 x 500 x 500
```

with `uint8` voxel values.

Each benchmark included a warm-up projection and 20 timed iterations.

### Triangle

| Implementation | FPS |
|---|---:|
| Original Python loops | 4.23 |
| Vectorized per scanline | 81.78 |
| Fully vectorized | **152.92** |

### Trapezoid

| Implementation | FPS |
|---|---:|
| Original Python loops | 3.50 |
| Vectorized per scanline | 104.26 |
| Fully vectorized | **142.59** |

Both final versions exceeded 100 FPS in the measured test scenarios.

Detailed timing results and limitations are documented in `RESULTS.md`.

---

## 19. Integration with the Application

The main program is `Ex0.py`.

Its command-line interface is:

```bash
python Ex0.py file.nrrd file.csv file.mp4
```

The application:

1. Loads the NRRD volume.
2. Reads plane definitions from the CSV.
3. Runs either triangle or trapezoid projection.
4. Normalizes the projected intensities for visualization.
5. Centers the resulting image within a fixed-size video frame.
6. Encodes the sequence to MP4.

The CSV format uses one row per plane.

The video uses one frame per CSV definition, preserving the original row order.

The display FPS of the MP4 is independent of the computational projection FPS.

---

## 20. Differences from the Original Assignment Pseudocode

The main differences are:

| Aspect | Assignment Approach | Our Implementation |
|---|---|---|
| Movement along legs | Incremental normalized steps | Fractional interpolation |
| Handling non-integer lengths | Unit-step iteration | `ceil` number of equal intervals |
| Position computation | Incremental updates | Direct interpolation from original vertices |
| Row centering | Geometric offset | Discrete pixel-count offset |
| Voxel sampling | Individual samples | Vectorized NumPy batch indexing |
| Trapezoid support | Similar scanline approach | Separate validated function |
| Runtime implementation | Nested loops | Fully vectorized coordinate arrays |

The mathematical intent remains the same: produce centered output rows from sampled line segments in a 3D volume.

However, the exact discrete sampling grid is a design choice of our implementation and should not be assumed to be pixel-for-pixel identical to the original assignment pseudocode.

---

## 21. Known Limitations

- Nearest-neighbor sampling can introduce aliasing.
- The implementation operates in voxel-index coordinates, not physical MRI coordinates.
- The trapezoid implementation rejects equal-length bases.
- Full vectorization uses temporary arrays proportional to the output image size.
- The benchmark measurements cover specific projection geometries.
- Performance on different hardware and larger output planes may vary.
- The geometry validation uses numerical tolerances and is not an exhaustive guarantee of robustness for every possible floating-point input.

---

## 22. Final Mental Model

The full algorithm can be summarized using five steps:

**1. Select the shape.**  
Determine whether the requested region is a triangle or trapezoid.

**2. Determine all scanlines.**  
Interpolate along the region's two legs.

**3. Determine all sampling positions.**  
Interpolate across each scanline.

**4. Retrieve voxel values.**  
Use nearest-neighbor sampling and return zero outside the volume.

**5. Construct the output image.**  
Store the sampled values at centered 2D coordinates.

The optimized implementation calculates these operations using NumPy arrays rather than Python loops over individual sampling points.

The algorithm is therefore both mathematically understandable and efficient in the measured workloads.