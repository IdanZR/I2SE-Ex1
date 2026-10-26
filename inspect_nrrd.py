from pathlib import Path
import numpy as np
import nrrd

file_path = Path("./data/MRHead_1.nrrd")

volume, header = nrrd.read(str(file_path), index_order="F")
print("=== VOLUME INFORMATION ===")
print("Shape:", volume.shape)
print("Dimensions:", volume.ndim)
print("Data type:", volume.dtype)
print("Total voxels:", volume.size)

print("\n=== INTENSITY VALUES ===")
print("Minimum:", np.min(volume))
print("Maximum:", np.max(volume))

print("\n=== NRRD HEADER ===")
for key, value in header.items():
    print(f"{key}: {value}")

# Example: sample one voxel near the center.
x, y, z = [size // 2 for size in volume.shape]

print("\n=== SAMPLE VOXEL ===")
print(f"M[{x}, {y}, {z}] =", volume[x, y, z])
