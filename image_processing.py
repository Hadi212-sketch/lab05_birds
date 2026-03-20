from __future__ import annotations

import shutil
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Optional

from PIL import Image, ImageFilter, ImageOps

MODEL_DISPLAY_NAME = "EfficientNet-B0"
DETAIL_LABELS = {
    "filename": "Filename",
    "format": "Format",
    "mode": "Color mode",
    "width_px": "Width (px)",
    "height_px": "Height (px)",
    "aspect_ratio": "Aspect ratio",
    "orientation": "Orientation",
    "megapixels": "Megapixels",
    "file_size_kb": "File size (KB)",
    "has_transparency": "Has transparency",
}

Prediction = tuple[str, float]
PredictionFunction = Callable[[Image.Image, int], list[Prediction]]


class ImageProcessingError(Exception):
    """Raised when an image-processing task cannot be completed."""


def load_image(image_path: Optional[str | Path]) -> Image.Image:
    """Load an image from disk and return a detached PIL image copy."""
    if not image_path:
        raise ImageProcessingError("Please upload or capture an image first.")

    path = Path(image_path)
    if not path.exists():
        raise ImageProcessingError("The selected image could not be found on disk.")

    try:
        with Image.open(path) as image:
            return image.copy()
    except OSError as exc:
        raise ImageProcessingError("The selected file is not a valid image.") from exc


def convert_to_grayscale(image_path: Optional[str | Path]) -> Image.Image:
    """Convert an image to grayscale while preserving its dimensions."""
    image = load_image(image_path)
    return ImageOps.grayscale(image)


def detect_edges(image_path: Optional[str | Path]) -> Image.Image:
    """Create a simple edge-detection rendering using Pillow filters."""
    grayscale = convert_to_grayscale(image_path)
    return grayscale.filter(ImageFilter.FIND_EDGES)


def extract_image_details(image_path: Optional[str | Path]) -> dict[str, Any]:
    """Extract a concise set of image details for display in the UI."""
    if not image_path:
        raise ImageProcessingError("Please upload or capture an image first.")

    path = Path(image_path)
    if not path.exists():
        raise ImageProcessingError("The selected image could not be found on disk.")

    try:
        with Image.open(path) as image:
            width, height = image.size
            orientation = "Landscape"
            if height > width:
                orientation = "Portrait"
            elif width == height:
                orientation = "Square"

            has_transparency = (
                "A" in image.getbands()
                or image.info.get("transparency") is not None
            )

            return {
                "filename": path.name,
                "format": image.format or path.suffix.lstrip(".").upper() or "Unknown",
                "mode": image.mode,
                "width_px": width,
                "height_px": height,
                "aspect_ratio": f"{width / height:.2f}:1" if height else "Unknown",
                "orientation": orientation,
                "megapixels": round((width * height) / 1_000_000, 2),
                "file_size_kb": round(path.stat().st_size / 1024, 1),
                "has_transparency": "Yes" if has_transparency else "No",
            }
    except OSError as exc:
        raise ImageProcessingError("The selected file is not a valid image.") from exc


def details_to_rows(details: dict[str, Any]) -> list[dict[str, str]]:
    """Convert extracted image metadata into dataframe-friendly rows."""
    return [
        {
            "Property": DETAIL_LABELS.get(key, key.replace("_", " ").title()),
            "Value": str(value),
        }
        for key, value in details.items()
    ]


def save_snapshot(
    image_path: Optional[str | Path], output_dir: str | Path = "snapshots"
) -> Path:
    """Save the current uploaded or webcam image as a dated snapshot."""
    if not image_path:
        raise ImageProcessingError("Please upload or capture an image before saving.")

    source_path = Path(image_path)
    if not source_path.exists():
        raise ImageProcessingError("The selected image could not be found on disk.")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    extension = source_path.suffix.lower() or ".png"
    target_path = output_path / (
        f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}{extension}"
    )
    shutil.copy2(source_path, target_path)
    return target_path


@lru_cache(maxsize=1)
def get_efficientnet_resources():
    """Lazily load the EfficientNet model, transforms, and label list."""
    import torch
    from torchvision.models import EfficientNet_B0_Weights, efficientnet_b0

    weights = EfficientNet_B0_Weights.DEFAULT
    model = efficientnet_b0(weights=weights)
    model.eval()
    preprocess = weights.transforms()
    categories = list(weights.meta["categories"])

    return model, preprocess, categories, torch


def efficientnet_predict(image: Image.Image, top_k: int = 5) -> list[Prediction]:
    """Run EfficientNet-B0 image recognition and return the top predictions."""
    model, preprocess, categories, torch = get_efficientnet_resources()

    rgb_image = image.convert("RGB")
    batch = preprocess(rgb_image).unsqueeze(0)
    top_k = max(1, min(top_k, len(categories)))

    with torch.inference_mode():
        logits = model(batch)
        probabilities = torch.nn.functional.softmax(logits[0], dim=0)
        values, indices = torch.topk(probabilities, k=top_k)

    return [
        (categories[int(index)], float(value))
        for value, index in zip(values.tolist(), indices.tolist())
    ]


def format_prediction_summary(
    predictions: list[Prediction], model_name: str = MODEL_DISPLAY_NAME
) -> str:
    """Format the top predictions into a short human-readable summary."""
    if not predictions:
        return "No predictions are available for this image."

    best_label, best_score = predictions[0]
    runners_up = ", ".join(
        f"{label} ({score * 100:.1f}%)" for label, score in predictions[1:3]
    )

    summary = f"Most likely match: {best_label} ({best_score * 100:.1f}%)."
    if runners_up:
        summary += f" Next likely matches: {runners_up}."
    summary += f" Model: {model_name}."
    return summary


def predictions_to_rows(predictions: list[Prediction]) -> list[dict[str, str]]:
    """Convert prediction tuples into dataframe-friendly rows."""
    return [
        {
            "Label": label,
            "Confidence": f"{score * 100:.2f}%",
        }
        for label, score in predictions
    ]


def recognize_image(
    image_path: Optional[str | Path],
    predictor: Optional[PredictionFunction] = None,
    top_k: int = 5,
) -> tuple[dict[str, float], list[Prediction], str]:
    """Run image recognition and return label scores, rows, and a summary."""
    image = load_image(image_path)
    prediction_function = predictor or efficientnet_predict

    try:
        predictions = prediction_function(image, top_k)
    except Exception as exc:
        raise ImageProcessingError(
            "Object recognition is currently unavailable. Please try again."
        ) from exc

    label_scores = {label: score for label, score in predictions}
    summary = format_prediction_summary(predictions)
    return label_scores, predictions, summary
