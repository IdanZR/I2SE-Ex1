# Testing Strategy – Ex1

## Objective

Verify that the projection algorithm produces geometrically correct 2D images from 3D volumes and meets the assignment's performance requirements.

## 1. Unit Tests

| Test | Input | Expected Result |
|---|---|---|
| Constant volume | Every voxel contains 100 | All in-bounds sampled pixels contain 100 |
| Coordinate-encoded volume | `M[x,y,z] = x + 10*y + 100*z` | Sampled values match the expected voxel indices |
| Out-of-bounds sample | Sampling point outside the volume | Return 0 |
| Triangle endpoint sampling | Known triangle coordinates | Last scanline reaches vertices `b` and `c` |
| Degenerate triangle | Three collinear points | Reject with a descriptive error |
| Non-integer coordinates | Fractional 3D points | Correct interpolation of sampling positions and nearest-neighbor lookup |

## 2. Geometry Tests

- Test an axis-aligned triangle with manually calculated sampling locations.
- Test a triangle on an oblique plane.
- Verify that scanlines remain between their endpoints.
- Verify that output rows are centered correctly.
- Test triangles near volume boundaries.

## 3. Real Dataset Tests

Use the provided MRI dataset:

- Shape: 256 × 256 × 130
- Data type: int16
- Intensity range: 0–279

Compare selected output slices visually against reference views from 3D Slicer.

The comparison should use the same geometric plane and coordinate system.

## 4. Performance Tests

Measure:

- Projection runtime per image.
- Frames per second (FPS).
- Performance with a synthetic 500 × 500 × 500 byte volume.
- The impact of different triangle sizes and orientations.

The assignment requires more than 30 FPS and sets approximately 100 FPS as an expected performance target for the large-volume case.

Record hardware specifications and timing conditions.

## 5. Integration Tests

Verify the complete pipeline:

1. Read an NRRD volume.
2. Read plane definitions from CSV.
3. Generate the corresponding projection for each row.
4. Produce an MP4 containing frames in CSV order.
5. Validate frame count, dimensions, and successful video playback.

## 6. Demo

Prepare a reproducible demonstration using the required command-line structure:

```bash
python Ex0.py file.nrrd file.csv file.mp4
```

The demonstration should include both successful and invalid-input cases.

## 7. Results

Record:

- Tests passed and failed.
- Sample output images.
- Any known limitations.
- Runtime and FPS measurements.
- The generated MP4 video.

**Status:** Testing strategy defined; tests have not yet been implemented or executed.