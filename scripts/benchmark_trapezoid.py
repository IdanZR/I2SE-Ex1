
import time
import numpy as np

from projection import project_trapezoid


def main():
    # Same volume size and data type as the triangle benchmark.
    volume = np.full(
        (500, 500, 500),
        100,
        dtype=np.uint8
    )

    # Valid isosceles trapezoid.
    a1 = (250, 200, 100)
    a2 = (250, 300, 100)
    b = (250, 170, 250)
    c = (250, 330, 250)

    print("Warming up...")
    project_trapezoid(volume, a1, a2, b, c)

    repetitions = 20
    times = []

    for i in range(repetitions):
        start = time.perf_counter()

        result = project_trapezoid(volume, a1, a2, b, c)

        elapsed = time.perf_counter() - start
        times.append(elapsed)

    average = np.mean(times)
    fps = 1.0 / average

    print("\n=== TRAPEZOID BENCHMARK ===")
    print("Volume shape:", volume.shape)
    print("Projection shape:", result.shape)
    print(f"Average time: {average * 1000:.2f} ms")
    print(f"Minimum time: {min(times) * 1000:.2f} ms")
    print(f"Maximum time: {max(times) * 1000:.2f} ms")
    print(f"Average FPS: {fps:.2f}")

    if fps > 30:
        print("PASS: Above 30 FPS")
    else:
        print("FAIL: Below 30 FPS")


if __name__ == "__main__":
    main()
