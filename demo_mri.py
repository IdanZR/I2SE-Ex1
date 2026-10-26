
from pathlib import Path

import numpy as np
import nrrd
from PIL import Image

from projection import project_triangle

# Use the same filename as in inspect_nrrd.py
mri_path = Path("data") / "MRHead_1.nrrd"

volume, header = nrrd.read(
    str(mri_path),
    index_order="F"
)

print("MRI shape:", volume.shape)

# A right-isosceles triangle within the volume.
# All coordinates are voxel indices.
a = (128, 70, 25)
b = (128, 170, 25)
c = (128, 70, 125)

result = project_triangle(volume, a, b, c)

print("Projection shape:", result.shape)
print("Minimum intensity:", result.min())
print("Maximum intensity:", result.max())

# Normalize MRI intensities for an 8-bit PNG.
image = result.astype(np.float32)

if image.max() > image.min():
    image = (
        (image - image.min())
        / (image.max() - image.min())
        * 255
    )

image = np.clip(image, 0, 255).astype(np.uint8)

# Save as a grayscale image.
output_path = Path("mri_projection.png")
Image.fromarray(image, mode="L").save(output_path)

print("Saved image:", output_path.resolve())
