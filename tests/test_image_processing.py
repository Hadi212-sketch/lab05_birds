import tempfile
import unittest
from pathlib import Path

from PIL import Image

from image_processing import (
    ImageProcessingError,
    convert_to_grayscale,
    details_to_rows,
    detect_edges,
    extract_image_details,
    format_prediction_summary,
    predictions_to_rows,
    recognize_image,
    save_snapshot,
)


class ImageProcessingTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.image_path = Path(self.temp_dir.name) / "sample.png"
        image = Image.new("RGB", (120, 80), color=(120, 40, 200))
        image.save(self.image_path, format="PNG")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_convert_to_grayscale_preserves_size(self):
        grayscale = convert_to_grayscale(self.image_path)
        self.assertEqual(grayscale.mode, "L")
        self.assertEqual(grayscale.size, (120, 80))

    def test_detect_edges_returns_grayscale_image(self):
        edges = detect_edges(self.image_path)
        self.assertEqual(edges.mode, "L")
        self.assertEqual(edges.size, (120, 80))

    def test_extract_image_details_returns_expected_values(self):
        details = extract_image_details(self.image_path)
        self.assertEqual(details["filename"], "sample.png")
        self.assertEqual(details["format"], "PNG")
        self.assertEqual(details["width_px"], 120)
        self.assertEqual(details["height_px"], 80)
        self.assertEqual(details["orientation"], "Landscape")
        self.assertEqual(details["has_transparency"], "No")

    def test_details_to_rows_converts_metadata_for_table_display(self):
        details = extract_image_details(self.image_path)
        rows = details_to_rows(details)
        self.assertEqual(rows[0]["Property"], "Filename")
        self.assertEqual(rows[0]["Value"], "sample.png")

    def test_save_snapshot_copies_image_to_target_directory(self):
        output_dir = Path(self.temp_dir.name) / "snapshots"
        snapshot_path = save_snapshot(self.image_path, output_dir=output_dir)
        self.assertTrue(snapshot_path.exists())
        self.assertEqual(snapshot_path.parent, output_dir)

    def test_recognize_image_accepts_custom_predictor(self):
        def fake_predictor(image, top_k):
            self.assertEqual(image.size, (120, 80))
            self.assertEqual(top_k, 5)
            return [
                ("tabby", 0.81),
                ("lynx", 0.12),
                ("tiger cat", 0.04),
            ]

        label_scores, predictions, summary = recognize_image(
            self.image_path,
            predictor=fake_predictor,
            top_k=5,
        )

        self.assertAlmostEqual(label_scores["tabby"], 0.81)
        self.assertEqual(predictions[0][0], "tabby")
        self.assertIn("Most likely match: tabby", summary)
        self.assertIn("Model: EfficientNet-B0.", summary)

    def test_prediction_rows_format_confidence_as_percentages(self):
        rows = predictions_to_rows([("tabby", 0.81), ("lynx", 0.12)])
        self.assertEqual(
            rows,
            [
                {"Label": "tabby", "Confidence": "81.00%"},
                {"Label": "lynx", "Confidence": "12.00%"},
            ],
        )

    def test_format_prediction_summary_handles_empty_list(self):
        summary = format_prediction_summary([])
        self.assertEqual(summary, "No predictions are available for this image.")

    def test_missing_image_raises_processing_error(self):
        with self.assertRaises(ImageProcessingError):
            convert_to_grayscale(None)


if __name__ == "__main__":
    unittest.main()
