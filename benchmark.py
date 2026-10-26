
import time
import numpy as np

from projection import project_triangle


def main():
    print("Creating 500x500x500 volume...")

    # 125 million voxels, 1 byte per voxel (~125 MB)
    volume = np.full(
        (500, 500, 500),
        100,
        dtype=np.uint8
    )

    # A valid isosceles triangle within the volume.
    a = (250, 180, 100)
    b = (250, 330, 100)
    c = (250, 180, 250)

    print("Warming up...")
    project_triangle(volume, a, b, c)

    repetitions = 20
    times = []

    print(f"Running {repetitions} projections...")

    for i in range(repetitions):
        start = time.perf_counter()

        result = project_triangle(volume, a, b, c)

        elapsed = time.perf_counter() - start
        times.append(elapsed)

    average = sum(times) / len(times)
    fps = 1.0 / average

    print("\n=== BENCHMARK RESULTS ===")
    print("Volume shape:", volume.shape)
    print("Volume dtype:", volume.dtype)
    print("Projection shape:", result.shape)
    print(f"Average time: {average * 1000:.2f} ms")
    print(f"Minimum time: {min(times) * 1000:.2f} ms")
    print(f"Maximum time: {max(times) * 1000:.2f} ms")
    print(f"Average FPS: {fps:.2f}")

    if fps > 100:
        print("Performance: Above 100 FPS target")
    elif fps > 30:
        print("Performance: Passes minimum 30 FPS requirement")
    else:
        print("Performance: Below required 30 FPS")


if __name__ == "__main__":
    main()
