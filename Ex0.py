
import argparse
import csv
from pathlib import Path

import imageio.v2 as imageio
import numpy as np
import nrrd

from projection import project_triangle, project_trapezoid


def read_planes(csv_path):
    """Read triangle and trapezoid definitions from CSV."""
    planes = []

    with open(csv_path, "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file, skipinitialspace=True)

        print("CSV columns:", reader.fieldnames)

        if reader.fieldnames:
            reader.fieldnames = [
                name.strip().lstrip("\ufeff")
                for name in reader.fieldnames
            ]

        required = [
            "type",
            "ax", "ay", "az",
            "bx", "by", "bz",
            "cx", "cy", "cz",
            "dx", "dy", "dz"
        ]

        missing = [
            column for column in required
            if column not in (reader.fieldnames or [])
        ]

        if missing:
            raise ValueError(
                f"Missing CSV columns: {missing}. "
                f"Found: {reader.fieldnames}"
            )

        for line_number, row in enumerate(reader, start=2):
            kind = (row["type"] or "").strip().lower()

            if not kind:
                continue

            def point(prefix):
                return (
                    float(row[f"{prefix}x"]),
                    float(row[f"{prefix}y"]),
                    float(row[f"{prefix}z"])
                )

            try:
                a = point("a")
                b = point("b")
                c = point("c")

                if kind == "triangle":
                    planes.append(("triangle", (a, b, c)))

                elif kind == "trapezoid":
                    d = point("d")
                    planes.append(("trapezoid", (a, b, c, d)))

                else:
                    raise ValueError(f"Unknown shape type: {kind}")

            except (ValueError, TypeError, KeyError) as error:
                raise ValueError(
                    f"Invalid CSV row {line_number}: {error}"
                ) from error

    if not planes:
        raise ValueError("CSV does not contain any valid planes")

    return planes


def normalize_image(image, volume_min, volume_max):
    """Convert intensities into 8-bit grayscale."""
    image = image.astype(np.float32)

    if volume_max > volume_min:
        image = (
            (image - volume_min)
            / (volume_max - volume_min)
            * 255.0
        )
    else:
        image = np.zeros_like(image)

    return np.clip(image, 0, 255).astype(np.uint8)


def center_frame(image, height, width):
    """Center a 2D image inside a fixed-size RGB frame."""
    frame = np.zeros((height, width), dtype=np.uint8)

    h, w = image.shape

    top = (height - h) // 2
    left = (width - w) // 2

    frame[top:top + h, left:left + w] = image

    return np.repeat(frame[:, :, None], 3, axis=2)


def main():
    parser = argparse.ArgumentParser(
        description="Convert 3D NRRD plane projections to MP4"
    )

    parser.add_argument("nrrd_file", help="Input NRRD volume")
    parser.add_argument("csv_file", help="Input CSV plane definitions")
    parser.add_argument("mp4_file", help="Output MP4 video")

    args = parser.parse_args()

    # 1. Load the MRI volume.
    volume, header = nrrd.read(
        args.nrrd_file,
        index_order="F"
    )

    if volume.ndim != 3:
        raise ValueError("NRRD must contain a 3D volume")

    print("Volume shape:", volume.shape)
    print("Volume dtype:", volume.dtype)

    # 2. Load plane definitions.
    planes = read_planes(args.csv_file)
    print("Number of planes:", len(planes))

    # 3. Calculate the projections.
    projections = []

    for index, (kind, points) in enumerate(planes, start=1):
        if kind == "triangle":
            projection = project_triangle(volume, *points)
        else:
            projection = project_trapezoid(volume, *points)

        projections.append(projection)

        print(
            f"Frame {index}: {kind}, "
            f"shape={projection.shape}"
        )

    # 4. Calculate a common video frame size.
    max_height = max(p.shape[0] for p in projections)
    max_width = max(p.shape[1] for p in projections)

    # Ensure even dimensions for H.264 yuv420p.
    frame_height = max(2, max_height + max_height % 2)
    frame_width = max(2, max_width + max_width % 2)

    volume_min = float(np.min(volume))
    volume_max = float(np.max(volume))

    # Include zero, because out-of-volume pixels use zero.
    display_min = min(volume_min, 0.0)
    display_max = max(volume_max, 0.0)

    # 5. Encode frames to MP4.
    output_path = Path(args.mp4_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with imageio.get_writer(
        str(output_path),
        format="FFMPEG",
        fps=2,
        codec="libx264",
        pixelformat="yuv420p",
        macro_block_size=1
    ) as writer:

        for projection in projections:
            image = normalize_image(
                projection,
                display_min,
                display_max
            )

            frame = center_frame(
                image,
                frame_height,
                frame_width
            )

            writer.append_data(frame)

    print("\nVideo saved:", output_path.resolve())
    print("Total frames:", len(projections))


if __name__ == "__main__":
    main()
