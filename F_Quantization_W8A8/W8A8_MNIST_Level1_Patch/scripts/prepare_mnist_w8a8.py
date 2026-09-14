#!/usr/bin/env python3
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="data/mnist_w8a8")
    parser.add_argument("--cache", default="data/torchvision")
    args = parser.parse_args()

    try:
        import numpy as np
        from torchvision.datasets import MNIST
        from torchvision.transforms import InterpolationMode
        from torchvision.transforms import functional as TF
    except ImportError as exc:
        raise SystemExit(
            "Missing Python dependency. Run: python -m pip install torch torchvision numpy"
        ) from exc

    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    dataset = MNIST(root=args.cache, train=False, download=True)
    image_path = output / "mnist_test_32x32.bin"
    label_path = output / "mnist_test_labels.bin"

    with image_path.open("wb") as image_stream, label_path.open("wb") as label_stream:
        for index, (image, label) in enumerate(dataset):
            resized = TF.resize(
                image,
                [32, 32],
                interpolation=InterpolationMode.BILINEAR,
                antialias=True,
            )
            pixels = np.asarray(resized, dtype=np.uint8)
            if pixels.shape != (32, 32):
                raise RuntimeError(f"Unexpected shape at index {index}: {pixels.shape}")
            image_stream.write(pixels.tobytes(order="C"))
            label_stream.write(bytes((int(label),)))
            if (index + 1) % 1000 == 0:
                print(f"Prepared {index + 1}/10000")

    print("W8A8_MNIST_DATA_PREPARATION_PASS")
    print(f"IMAGES={image_path.resolve()}")
    print(f"LABELS={label_path.resolve()}")


if __name__ == "__main__":
    main()
