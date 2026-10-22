# I2SE Ex1 – Projection Algorithm: Detailed Design

**Course:** Introduction to Software Engineering  
**Implementation language:** Python  
**Document version:** 0.2  
**Status:** Detailed design proposal – not yet implemented or tested

---

# 1. Introduction

## 1.1 The Problem We Are Solving

We are given a three-dimensional matrix (volume) containing numerical voxel values.

Our goal is to extract a two-dimensional image representing a specified region of a plane passing through that volume.

The volume is represented by:

$$
M[x][y][z]
$$

Each voxel contains a numerical intensity value.

For example:

```python
value = M[10, 20, 30]
```

This retrieves the value at the three-dimensional index `(10, 20, 30)`.

Our output will be a two-dimensional matrix:

$$
E[y][x]
$$

Each element of `E` represents a pixel in the generated image.

### The core idea

Instead of searching through the entire 3D volume for voxels that belong to the plane, we calculate sampling locations directly on the desired plane.

For each sampling location:

1. Calculate its three-dimensional coordinates.
2. Retrieve the corresponding voxel intensity.
3. Determine where this value belongs in the 2D output.
4. Write the value to the output matrix.

This process is called **plane sampling** or **reslicing**.

## 1.2 Important Terminology

| Term | Meaning |
|---|---|
| Voxel | A volumetric data element with three spatial indices |
| Pixel | An element of the resulting 2D image |
| Plane | An infinite two-dimensional geometric surface in 3D |
| Triangle | The bounded region of the plane that we currently sample |
| Scanline | A line segment inside the triangle that becomes one output image row |
| Sampling point | A 3D coordinate at which we retrieve a volume value |
| Intensity | The numerical value stored in the volume |
| Nearest-neighbor sampling | Retrieving the value of the nearest voxel |
| Normalized vector | A vector whose Euclidean length is one |

**Important distinction:** The geometric plane is infinite, but the current algorithm samples only the triangular region specified by the input vertices.

---

# 2. Understanding the Original Assignment

The assignment provides a scanline algorithm for an isosceles triangle.

It receives three 3D points:

$$
a,b,c\in\mathbb{R}^3
$$

The two legs must have equal length:

$$
\|b-a\|=\|c-a\|
$$

The original algorithm:

1. Calculates the triangle's edge lengths.
2. Normalizes the direction vectors from `a` toward `b` and `c`.
3. Moves two points along the triangle's legs.
4. Connects these points to obtain a scanline.
5. Samples the volume along that scanline.
6. Centers the sampled values in the output image.
7. Repeats for subsequent rows.

The assignment also describes an extension to an isosceles trapezoid, where the two scanning legs start at different points.

## 2.1 Why Our Implementation Is Slightly Different

The assignment uses incremental steps of approximately one geometric unit.

However, real distances are not necessarily integers.

For example, a triangle leg might have length:

$$
D_{ab}=4.3
$$

If we take five steps, each of length one, the last step passes the endpoint.

Therefore, we propose a modification:

**Divide the original segment into an integer number of equal intervals, instead of always advancing by exactly one unit.**

This guarantees that the calculated sampling positions stay between the specified endpoints.

This modification preserves the scanline approach, but it is not a verbatim translation of the assignment pseudocode.

---

# 3. Mathematical Preparation

## 3.1 Defining the Triangle

Let:

$$
a=(a_x,a_y,a_z)
$$

$$
b=(b_x,b_y,b_z)
$$

$$
c=(c_x,c_y,c_z)
$$

The vectors along the legs are:

$$
\vec{v}_{ab}=b-a
$$

$$
\vec{v}_{ac}=c-a
$$

### Why subtract the points?

The difference `b - a` gives the displacement required to travel from point `a` to point `b`.

It tells us both the direction and the total displacement.

For example:

$$
a=(1,2,3),\quad b=(4,6,3)
$$

Then:

$$
b-a=(3,4,0)
$$

This means traveling 3 units along X and 4 units along Y, with no movement along Z.

The vector's length is:

$$
\|b-a\|=\sqrt{3^2+4^2}=5
$$

Therefore, dividing by 5 would create a unit vector in the same direction.

## 3.2 Calculating Edge Lengths

Define:

$$
D_{ab}=\|b-a\|
$$

$$
D_{ac}=\|c-a\|
$$

$$
D_{bc}=\|c-b\|
$$

For a valid isosceles triangle:

$$
D_{ab}\approx D_{ac}>0
$$

The vertices must also be non-collinear.

This can be checked using the cross product:

$$
(b-a)\times(c-a)\ne 0
$$

In floating-point computation, these geometric conditions should be checked using suitable numerical tolerances rather than exact equality.

---

# 4. Sampling Along the Triangle Legs

This section explains how we create the two endpoints of every scanline.

## 4.1 Why We Need Two Moving Points

Imagine an isosceles triangle with vertex `a` at the top and base `bc` at the bottom.

We want to scan the triangle one row at a time.

To create each row, we need:

- `a1`: a point on the segment from `a` to `b`.
- `a2`: a point on the segment from `a` to `c`.

The segment connecting `a1` and `a2` is our current scanline.

Near the vertex, this segment is short.

As we approach the base, the segment becomes longer.

At the base:

$$
a_1=b,\qquad a_2=c
$$

## 4.2 Choosing the Number of Intervals

Let the length of a leg be:

$$
L=D_{ab}
$$

Define:

$$
N=\lceil L\rceil
$$

Here, `ceil` means rounding upward to the nearest integer.

**Crucial distinction:**

`N` is the number of intervals into which we divide the leg.

It is NOT the new length of the leg.

### Example

Suppose:

$$
L=4.3
$$

We choose:

$$
N=\lceil4.3\rceil=5
$$

The geometric leg still has length 4.3.

We have simply divided it into five equal intervals.

Each interval has length:

$$
\Delta L=\frac{4.3}{5}=0.86
$$

The distances from the starting point are:

| Step | Distance from the start |
|---|---|
| 0 | 0 |
| 1 | 0.86 |
| 2 | 1.72 |
| 3 | 2.58 |
| 4 | 3.44 |
| 5 | 4.30 |

We reach the endpoint exactly, without extending the original segment.

This is the main reason for introducing the normalized progress parameter in the next section.

---

# 5. Understanding the Parameter ty

## 5.1 What Does ty Represent?

For every output row indexed by `y`, define:

$$
t_y=\frac{y+1}{N}
$$

where:

$$
y=0,1,\ldots,N-1
$$

The value `ty` tells us **what fraction of the complete leg has been traveled**.

It is not the distance itself.

For example:

| `ty` | Meaning |
|---|---|
| 0.2 | 20% of the total displacement |
| 0.4 | 40% of the total displacement |
| 0.6 | 60% of the total displacement |
| 0.8 | 80% of the total displacement |
| 1.0 | 100% – the endpoint |

When `N = 5`, the rows correspond to:

$$
\frac15,\frac25,\frac35,\frac45,\frac55
$$

We start at `1/N` because the original algorithm advances its endpoints before generating the first row.

Thus, in this design, the vertex `a` is not an additional output row.

## 5.2 Calculating the First Endpoint

We define:

$$
a_1=a+t_y(b-a)
$$

This formula is extremely important.

Let's understand every part.

### Part A: The vector b - a

$$
b-a
$$

This represents the entire displacement from `a` to `b`.

### Part B: Multiplication by ty

$$
t_y(b-a)
$$

This scales the complete displacement by the required fraction.

For example, if `ty = 0.4`, the resulting vector represents 40% of the original displacement.

### Part C: Adding the starting point

$$
a+t_y(b-a)
$$

This means:

**Start at the original point `a`, then travel the calculated fraction of the way toward `b`.**

## 5.3 Complete Numerical Example

Suppose:

$$
a=(0,0,0)
$$

$$
b=(0,4.3,0)
$$

And:

$$
N=5
$$

For the second row, `y = 1`:

$$
t_y=\frac{1+1}{5}=0.4
$$

Calculate the displacement:

$$
b-a=(0,4.3,0)
$$

Multiply:

$$
0.4(b-a)=(0,1.72,0)
$$

Finally, add the starting point:

$$
a_1=(0,0,0)+(0,1.72,0)
$$

Therefore:

$$
a_1=(0,1.72,0)
$$

We have reached exactly 40% of the leg.

## 5.4 Why We Must Recalculate from a

A common mistake would be:

```text
a1 = a1 + ty * (b - a)
```

This is wrong for our chosen formula.

Why?

Because `ty` already represents the **total progress from the original point**.

Adding it to the previously updated `a1` would repeatedly accumulate growing displacements.

Instead, for every row, calculate:

```text
a1 = a + ty * (b - a)
```

Always calculate the position from the original point `a`.

## 5.5 Connection to Linear Algebra

We can rewrite:

$$
a_1=a+t_y(b-a)
$$

by expanding the parentheses:

$$
a_1=a+t_yb-t_ya
$$

Collect terms:

$$
a_1=(1-t_y)a+t_yb
$$

This is an **affine combination**.

Because:

$$
0\le t_y\le1
$$

it is also a convex combination.

A convex combination of two points always lies on the segment connecting them.

This explains mathematically why our calculated point stays between `a` and `b`.

## 5.6 Calculating the Second Endpoint

Exactly the same reasoning applies to the other leg:

$$
a_2=a+t_y(c-a)
$$

We use the SAME value of `ty` for both endpoints.

Therefore:

- `a1` is 40% of the way from `a` to `b`.
- `a2` is 40% of the way from `a` to `c`.

The segment connecting these points becomes the current scanline.

At the final row:

$$
t_y=1
$$

Therefore:

$$
a_1=b
$$

$$
a_2=c
$$

We have reached the triangle's base.

---

# 6. Why Scanlines Become Wider

The triangle's base is the segment connecting `b` and `c`.

Its length is:

$$
D_{bc}=\|c-b\|
$$

At progress `ty`, the scanline connects:

$$
a_1=a+t_y(b-a)
$$

and:

$$
a_2=a+t_y(c-a)
$$

Subtract:

$$
a_2-a_1
$$

Substituting both expressions:

$$
a_2-a_1=t_y(c-a)-t_y(b-a)
$$

Factor out `ty`:

$$
a_2-a_1=t_y(c-b)
$$

Now take the Euclidean norm:

$$
\|a_2-a_1\|=t_y\|c-b\|
$$

because `ty` is nonnegative.

Therefore:

$$
d_{12}=t_yD_{bc}
$$

This is also a result of similar triangles.

**Meaning:** When we advance to 40% of the way along the triangle's legs, the current scanline is 40% as long as the base.

### Example

If:

$$
D_{bc}=10
$$

and:

$$
t_y=0.4
$$

then:

$$
d_{12}=4
$$

This is a geometric distance.

It does NOT necessarily mean that the output row contains exactly four pixels.

The number of pixels depends on the sampling policy.

---

# 7. Sampling Across a Scanline

We now understand how to calculate `a1` and `a2`.

The next task is to sample the segment between them.

## 7.1 What Is a Scanline?

A scanline is the segment from `a1` to `a2` in the 3D volume.

We sample several locations on this segment.

For each location, we retrieve an intensity value from the volume.

Those values are placed into one row of the output image.

Therefore:

- The scanline is a geometric object in 3D.
- Its samples become pixels in the 2D output image.

## 7.2 Calculating the Number of Intervals

Let:

$$
d_{12}=\|a_2-a_1\|
$$

Define:

$$
K=\lceil d_{12}\rceil
$$

Here, `K` is the number of sampling intervals across the scanline.

We use:

$$
j=0,1,\ldots,K
$$

This produces `K + 1` sampling locations, including both endpoints.

For a non-degenerate triangle and our selected rows, `d12` is positive, so `K` is at least one.

## 7.3 Introducing tx

Define:

$$
t_x=\frac{j}{K}
$$

This is the same principle we used for `ty`.

The difference:

- `ty` represents progress along the triangle's legs.
- `tx` represents progress across the current scanline.

The sampling location is:

$$
p_j=a_1+t_x(a_2-a_1)
$$

This means:

Start at `a1`, and move a fraction `tx` of the complete displacement toward `a2`.

## 7.4 Example

Suppose:

$$
a_1=(0,2,0)
$$

$$
a_2=(0,0,2)
$$

The segment length is:

$$
d_{12}=\sqrt8\approx2.828
$$

Therefore:

$$
K=3
$$

Our sampling indices are:

$$
j=0,1,2,3
$$

The corresponding progress values are:

$$
t_x=0,\frac13,\frac23,1
$$

For `j = 1`:

$$
t_x=\frac13
$$

The displacement is:

$$
a_2-a_1=(0,-2,2)
$$

Therefore:

$$
p_1=(0,2,0)+\frac13(0,-2,2)
$$

Giving:

$$
p_1=\left(0,\frac43,\frac23\right)
$$

Approximately:

$$
p_1=(0,1.333,0.667)
$$

The complete sampling sequence is:

| j | tx | Sampling position p |
|---|---|---|
| 0 | 0 | (0, 2, 0) |
| 1 | 1/3 | (0, 1.333, 0.667) |
| 2 | 2/3 | (0, 0.667, 1.333) |
| 3 | 1 | (0, 0, 2) |

Notice that the final sampling position is exactly `a2`.

This is why we chose interpolation rather than unrestricted unit-step advancement.

---

# 8. Sampling Voxel Intensities

We now have a three-dimensional sampling point:

$$
p=(p_x,p_y,p_z)
$$

However, NumPy array indices must be integers.

A location such as:

$$
p=(0,1.333,0.667)
$$

cannot be accessed directly as an array index.

## 8.1 Initial Sampling Method: Nearest Neighbor

Our initial design uses nearest-neighbor sampling.

For example:

$$
(0,1.333,0.667)\longrightarrow(0,1,1)
$$

We then retrieve:

```python
value = volume[0, 1, 1]
```

This is an intentionally simple initial approach.

Later, if necessary, we may investigate trilinear interpolation.

## 8.2 Out-of-Bounds Sampling

The assignment specifies that sampling outside the volume returns zero.

For a volume with dimensions:

$$
(s_x,s_y,s_z)
$$

a legal voxel index must satisfy:

$$
0\le x<s_x
$$

$$
0\le y<s_y
$$

$$
0\le z<s_z
$$

If the sampling location is outside the supported volume, return zero.

### Important implementation details

The following choices must be consistent and tested:

- Use the volume's documented axis ordering.
- Reject NaN or infinite coordinates.
- Check whether the continuous position lies within the valid volume bounds before rounding.
- Define a consistent rule for exact half-integer ties.
- Use a floating-point tolerance only where justified.

**NRRD coordinates:** This initial algorithm assumes the supplied points are expressed in volume-index coordinates. If a dataset or CSV uses physical or world coordinates, they must be transformed into voxel-index coordinates first.

---

# 9. Understanding Output Row Centering

This section explains why the original assignment uses a centering formula.

## 9.1 Why Is Centering Necessary?

Our output is a rectangular 2D matrix.

However, the region being sampled is triangular.

Near the top of the triangle, scanlines are short.

Near the bottom, scanlines become longer.

If every scanline starts at output column zero, the result will be shifted toward one side.

To preserve the intended triangular shape, each row must be centered within the output image.

## 9.2 Understanding the Original Formula

The assignment uses:

$$
x=\frac{D_{bc}}2-\frac{d_{12}}2+x_1
$$

Here:

- `Dbc` is the geometric length of the full base.
- `d12` is the current scanline length.
- `x1` is the inner-loop counter.
- `x` is the horizontal output position.

The formula can be rewritten:

$$
x=\frac{D_{bc}-d_{12}}2+x_1
$$

The first part:

$$
\frac{D_{bc}-d_{12}}2
$$

is the amount of empty space needed on each side of the scanline.

The second part, `x1`, advances across the current row.

### Example

Suppose:

$$
D_{bc}=12
$$

and:

$$
d_{12}=6
$$

There are:

$$
12-6=6
$$

units of unused width.

To center the scanline, we divide this space equally:

$$
\frac62=3
$$

Therefore, the scanline should start three units from the left boundary.

The original formula becomes:

$$
x=3+x_1
$$

This is a geometric centering expression.

It must be adapted when working with integer pixel indices.

## 9.3 Our Discrete Centering Method

Our proposed implementation works with integer sample counts.

Define the output dimensions:

$$
H=N
$$

$$
W=\lceil D_{bc}\rceil+1
$$

For a scanline containing `K + 1` samples, the number of unused output columns is:

$$
W-(K+1)
$$

To center these samples, calculate:

$$
start=\left\lfloor\frac{W-(K+1)}2\right\rfloor
$$

The output column for sample `j` becomes:

$$
x=start+j
$$

### Numerical Example

Suppose:

- Output width: `W = 11`
- Current scanline samples: `K + 1 = 5`

The number of unused columns is:

$$
11-5=6
$$

Divide equally:

$$
start=\frac62=3
$$

Therefore:

| j | Output column x |
|---|---|
| 0 | 3 |
| 1 | 4 |
| 2 | 5 |
| 3 | 6 |
| 4 | 7 |

Columns 0, 1 and 2 remain empty.

Columns 8, 9 and 10 also remain empty.

The scanline is centered.

## 9.4 Understanding x, j and p

These variables have different roles.

| Variable | Meaning |
|---|---|
| `j` | Current sample index within the scanline |
| `p` | Current 3D sampling location |
| `x` | Output image column |
| `y` | Output image row |
| `d12` | Geometric length of the scanline |
| `K` | Number of intervals across the scanline |
| `start` | Horizontal offset used for centering |

**A useful mental model:**

`j` tells us which sample we are processing.

`p` tells us where to read the value in 3D.

`x` and `y` tell us where to write that value in 2D.

This distinction is fundamental to understanding the implementation.

---

# 10. Complete Proposed Algorithm

## 10.1 Mathematical Summary

For the triangle's legs:

$$
N=\lceil\|b-a\|\rceil
$$

$$
t_y=\frac{y+1}{N}
$$

$$
a_1=a+t_y(b-a)
$$

$$
a_2=a+t_y(c-a)
$$

For each scanline:

$$
d_{12}=\|a_2-a_1\|
$$

$$
K=\lceil d_{12}\rceil
$$

$$
t_x=\frac{j}{K}
$$

$$
p_j=a_1+t_x(a_2-a_1)
$$

For the output:

$$
H=N
$$

$$
W=\lceil D_{bc}\rceil+1
$$

$$
start=\left\lfloor\frac{W-(K+1)}2\right\rfloor
$$

$$
x=start+j
$$

Finally:

$$
E[y,x]=\operatorname{sample}(M,p_j)
$$

## 10.2 Detailed Pseudocode

```text
FUNCTION project_triangle(M, a, b, c):

    validate_volume(M)
    validate_triangle(a, b, c)

    Dab = distance(a, b)
    Dac = distance(a, c)
    Dbc = distance(b, c)

    N = ceil(Dab)

    H = N
    W = ceil(Dbc) + 1

    E = zero_matrix(H, W)

    FOR y FROM 0 TO N-1:

        # Fraction of progress along the legs
        ty = (y + 1) / N

        # Two endpoints of the current scanline
        a1 = a + ty * (b - a)
        a2 = a + ty * (c - a)

        # Geometric length of the scanline
        d12 = distance(a1, a2)

        # Number of intervals
        K = ceil(d12)

        # Number of samples = K + 1
        sample_count = K + 1

        # Discrete horizontal centering
        start = floor((W - sample_count) / 2)

        FOR j FROM 0 TO K:

            # Fraction across the scanline
            tx = j / K

            # 3D sampling position
            p = a1 + tx * (a2 - a1)

            # Read intensity from the 3D volume
            intensity = sample_volume(M, p)

            # Calculate 2D output column
            x = start + j

            # Store sampled value
            E[y, x] = intensity

    RETURN E
```

This is the proposed algorithm for implementation.

It is not yet tested against actual NRRD data.

---

# 11. Design Decisions and Edge Cases

## 11.1 Degenerate Triangles

A triangle is invalid if two of its required vertices coincide or if the three vertices are collinear.

The implementation should validate the geometry before calculating scanlines.

## 11.2 Non-Isosceles Triangles

The initial algorithm expects equal-length legs.

We will reject triangles that violate this requirement beyond an appropriate numerical tolerance.

## 11.3 Non-Integer Distances

Distances are real numbers.

We use `ceil` only to determine how many intervals or output positions are required.

The actual geometric endpoints are not moved.

## 11.4 Very Small Triangles

A non-degenerate triangle may have leg lengths smaller than one.

Our proposed algorithm still creates at least one output row, but the resulting image may be too small to represent its shape meaningfully.

This should be documented and tested.

## 11.5 Sampling Precision

Nearest-neighbor sampling may produce repeated pixel values or aliasing.

This is a limitation of the initial design, not necessarily a programming error.

Higher-quality interpolation may be considered later.

## 11.6 Output Data Type

The volume may contain 8-, 16-, or 32-bit unsigned integers.

We should preserve the original voxel values during projection.

Conversion to an 8-bit format suitable for MP4 video encoding should occur in a separate visualization or video-output stage.

## 11.7 Different Image Sizes

Different planes may produce images of different dimensions.

Since the final MP4 should use a consistent video frame size, we will need a separate frame normalization or padding policy.

That decision belongs to the video-output design.

---

# 12. Correctness Considerations

Some useful mathematical properties can already be established.

### Property 1 – Leg endpoints remain inside their segments

Because:

$$
0<t_y\le1
$$

each calculated endpoint is a convex combination of the original segment endpoints.

### Property 2 – The final row reaches the triangle base

At:

$$
y=N-1
$$

we obtain:

$$
t_y=1
$$

Therefore:

$$
a_1=b,\qquad a_2=c
$$

### Property 3 – Scanline samples stay between their endpoints

Because:

$$
0\le t_x\le1
$$

each sampling location is a convex combination of `a1` and `a2`.

### Property 4 – Output indices remain within the allocated width

Since every scanline has length no greater than `Dbc`, we obtain:

$$
K\le\lceil D_{bc}\rceil
$$

Thus:

$$
K+1\le W
$$

The discrete centering calculation therefore provides nonnegative output column indices within the allocated row.

These mathematical properties do not replace implementation testing.

---

# 13. Time and Space Complexity

Let:

- `H` be the number of output rows.
- `W` be the maximum number of samples in one output row.

The outer loop processes `H` rows.

For each row, the inner loop processes at most `W` samples.

Assuming constant-time sampling:

$$
T(H,W)=O(HW)
$$

The output matrix uses:

$$
S(H,W)=O(HW)
$$

additional memory.

This excludes the input volume itself, which has:

$$
s_xs_ys_z
$$

elements.

The implementation will later be benchmarked against the assignment's performance requirements.

A mathematically efficient algorithm does not automatically guarantee the required FPS in Python. Vectorization, memory access patterns, and implementation overhead will also matter.

---

# 14. Planned Testing Strategy

Before using real MRI files, the algorithm should be tested with small synthetic volumes.

## Test A – Constant Volume

Create a volume where every voxel equals 100.

Every valid sample should return 100.

This helps verify basic sampling behavior.

## Test B – Coordinate-Encoded Volume

Define:

```python
M[x, y, z] = x + 10*y + 100*z
```

for a sufficiently small integer-valued synthetic volume.

This lets us identify which voxel was sampled by inspecting its value.

## Test C – Axis-Aligned Triangle

Use a triangle that lies in a coordinate plane, such as the YZ plane.

The expected geometry is easy to calculate manually.

## Test D – Oblique Triangle

Use a triangle that is not aligned with the coordinate planes.

This verifies that the algorithm genuinely works in three dimensions.

## Test E – Boundary Behavior

Test scanlines containing points:

- At the volume boundary.
- Outside the volume.
- Near half-integer voxel coordinates.

## Test F – Numerical and Shape Validation

Test:

- Zero-length legs.
- Collinear points.
- Unequal legs.
- Very small triangles.
- Non-integer edge lengths.

## Test G – Performance

Measure projection computation time using controlled synthetic and NRRD datasets.

The assignment requires more than 30 FPS and expects approximately 100 FPS or higher for the specified large-volume workload.

Record the tested hardware, volume type, plane dimensions, and timing methodology.

---

# 15. Planned Trapezoid Extension

The initial triangle uses a single starting point:

$$
a_1=a_2=a
$$

For an isosceles trapezoid, the two scanlines' starting endpoints are distinct:

$$
a_1=a'
$$

$$
a_2=a''
$$

The two endpoints progress along equal-length legs toward `b` and `c`.

A potential extension using our interpolation method is:

$$
a_1=a'+t_y(b-a')
$$

$$
a_2=a''+t_y(c-a'')
$$

The current scanline connects those two points.

Unlike the triangle case, the initial scanline may already have nonzero length.

Therefore, output sizing and horizontal centering must be adapted.

We will complete and test that extension only after the triangle implementation is validated.

---

# 16. Final Mental Model

The entire algorithm can be understood as two nested movements.

### Outer movement – Down the triangle

The outer loop selects the current scanline by moving its endpoints along the triangle's two legs.

The parameter `ty` controls that progress.

### Inner movement – Across the scanline

The inner loop visits several sampling locations between the current endpoints.

The parameter `tx` controls that progress.

For every sampled point:

1. Calculate its 3D location.
2. Retrieve its voxel intensity.
3. Calculate its centered 2D output column.
4. Write the intensity into the output image.

**The most important distinction:**

- `ty` decides WHICH scanline we are processing.
- `tx` decides WHERE we are along that scanline.
- `p` is the 3D point being sampled.
- `(y, x)` is the 2D pixel being written.

---

# 17. Current Development Status

The algorithm has been mathematically designed and documented.

Still pending:

- Implementation in Python.
- Validation against synthetic datasets.
- Verification of the sampling and rounding policies.
- Real NRRD tests.
- Trapezoid extension.
- CSV input.
- MP4 output.
- Performance benchmarks.

The next assignment step is to define a dataset of NRRD files and prepare a testing strategy before implementation.