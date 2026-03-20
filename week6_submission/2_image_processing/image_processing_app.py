from __future__ import annotations

from typing import Optional

import gradio as gr
import pandas as pd

from image_processing import (
    ImageProcessingError,
    convert_to_grayscale,
    details_to_rows,
    detect_edges,
    extract_image_details,
    predictions_to_rows,
    recognize_image,
    save_snapshot,
)

APP_TITLE = "Image Processing Studio"
DETAIL_COLUMNS = ["Property", "Value"]
PREDICTION_COLUMNS = ["Label", "Confidence"]
APP_THEME = gr.themes.Soft(
    primary_hue="emerald",
    secondary_hue="amber",
    neutral_hue="stone",
)
APP_CSS = """
.gradio-container {
  font-family: "Montserrat", "Aptos", "Trebuchet MS", sans-serif;
  background:
    radial-gradient(circle at top left, rgba(255, 196, 112, 0.35), transparent 28%),
    radial-gradient(circle at bottom right, rgba(91, 173, 151, 0.22), transparent 24%),
    linear-gradient(180deg, #f7f1e8 0%, #f3eee7 100%);
}
footer {
  display: none !important;
}
.mode-strip {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 0.9rem;
  margin: 0.4rem 0 1.1rem;
}
.mode-card {
  background: rgba(255, 252, 247, 0.72);
  border: 1px solid rgba(105, 84, 66, 0.12);
  border-radius: 20px;
  padding: 1rem 1.05rem 0.9rem;
  box-shadow: 0 12px 28px rgba(66, 50, 34, 0.08);
}
.mode-index {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 2.1rem;
  height: 2.1rem;
  border-radius: 999px;
  background: linear-gradient(135deg, #0f766e, #159a8c);
  color: #f7fbfa;
  font-size: 0.8rem;
  font-weight: 800;
  letter-spacing: 0.08em;
}
.mode-card h3 {
  margin: 0.8rem 0 0.3rem;
  font-size: 1rem;
  color: #35291f;
}
.mode-card p {
  margin: 0;
  color: #6b584a;
  font-size: 0.92rem;
  line-height: 1.45;
}
.upload-panel,
.results-panel {
  background: rgba(255, 250, 243, 0.64);
  border: 1px solid rgba(109, 87, 68, 0.14);
  border-radius: 24px;
  padding: 0.9rem;
  box-shadow: 0 16px 36px rgba(71, 52, 36, 0.09);
  backdrop-filter: blur(6px);
}
.panel-heading {
  margin: 0 0 0.95rem;
}
.panel-kicker {
  display: inline-block;
  font-size: 0.74rem;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #11796f;
  margin-bottom: 0.35rem;
}
.panel-heading h2 {
  margin: 0;
  font-size: 1.3rem;
  color: #33271f;
}
.panel-heading p {
  margin: 0.35rem 0 0;
  color: #6d5a4b;
  line-height: 1.5;
  font-size: 0.95rem;
}
.hero-card {
  background: linear-gradient(135deg, rgba(41, 52, 63, 0.96), rgba(82, 58, 36, 0.94));
  color: #f8f4ec;
  padding: 1.5rem 1.7rem;
  border-radius: 24px;
  box-shadow: 0 18px 45px rgba(40, 33, 25, 0.18);
  margin-bottom: 1rem;
}
.hero-kicker {
  text-transform: uppercase;
  letter-spacing: 0.16em;
  font-size: 0.74rem;
  opacity: 0.74;
  margin-bottom: 0.55rem;
}
.hero-card h1 {
  margin: 0;
  font-size: 2.2rem;
  line-height: 1.05;
}
.hero-card p {
  margin: 0.85rem 0 0;
  max-width: 52rem;
  color: rgba(248, 244, 236, 0.9);
}
.hero-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.55rem;
  margin-top: 1rem;
}
.hero-chip {
  display: inline-flex;
  align-items: center;
  border: 1px solid rgba(255, 245, 232, 0.14);
  background: rgba(255, 247, 236, 0.08);
  color: rgba(255, 247, 236, 0.9);
  border-radius: 999px;
  padding: 0.42rem 0.8rem;
  font-size: 0.82rem;
  font-weight: 700;
}
.upload-panel .prose,
.upload-panel .prose p,
.results-panel .prose,
.results-panel .prose p,
.results-panel .prose li,
.upload-panel .prose li {
  color: #5b4a3d !important;
  font-size: 0.98rem;
  line-height: 1.55;
}
.results-panel [role="tablist"] {
  gap: 0.45rem;
  padding: 0.25rem 0 0.65rem;
  border-bottom: 1px solid rgba(82, 58, 36, 0.22);
}
.results-panel [role="tab"] {
  color: #7a6656 !important;
  font-weight: 700;
  border-radius: 999px;
  padding: 0.55rem 1rem !important;
  transition: background 0.2s ease, color 0.2s ease, transform 0.2s ease;
}
.results-panel [role="tab"]:hover {
  color: #2f241d !important;
  background: rgba(255, 255, 255, 0.62);
}
.results-panel [role="tab"][aria-selected="true"] {
  color: #f6fcfb !important;
  background: linear-gradient(135deg, #0f766e, #159a8c);
  box-shadow: 0 10px 24px rgba(21, 122, 110, 0.24);
}
.results-panel [role="tabpanel"] {
  padding-top: 0.35rem;
}
.upload-panel label,
.results-panel label,
.upload-panel .block-label,
.results-panel .block-label {
  color: #4c3d31 !important;
  font-weight: 700;
}
.upload-panel .image-container,
.results-panel .image-container {
  background: linear-gradient(180deg, #212b39, #1c2632) !important;
}
.upload-panel .icon-button,
.results-panel .icon-button {
  color: #fff8ef !important;
  background: rgba(15, 118, 110, 0.82) !important;
  border: none !important;
}
.upload-panel .icon-button:hover,
.results-panel .icon-button:hover {
  background: rgba(21, 154, 140, 0.92) !important;
}
.upload-panel button.secondary,
.results-panel button.secondary {
  background: linear-gradient(135deg, #4d5969, #36404f) !important;
  color: #fff8ef !important;
  border: none !important;
}
.upload-panel button.primary,
.results-panel button.primary {
  background: linear-gradient(135deg, #0f766e, #159a8c) !important;
  color: #fff8ef !important;
  border: none !important;
  box-shadow: 0 12px 26px rgba(21, 122, 110, 0.22);
}
.upload-panel button.primary:hover,
.upload-panel button.secondary:hover,
.results-panel button.primary:hover,
.results-panel button.secondary:hover {
  filter: brightness(1.04);
  transform: translateY(-1px);
}
.upload-panel .wrap,
.results-panel .wrap {
  border-radius: 18px !important;
}
.status-card {
  border-radius: 16px;
  padding: 0.8rem 1rem;
  font-size: 0.95rem;
  border: 1px solid transparent;
}
.status-card.success {
  background: rgba(86, 140, 122, 0.12);
  border-color: rgba(86, 140, 122, 0.28);
  color: #183d31;
}
.status-card.error {
  background: rgba(165, 76, 71, 0.1);
  border-color: rgba(165, 76, 71, 0.25);
  color: #5d1d19;
}
.status-card.neutral {
  background: rgba(102, 88, 74, 0.08);
  border-color: rgba(102, 88, 74, 0.14);
  color: #43362b;
}
"""


def empty_dataframe(columns: list[str]) -> pd.DataFrame:
    """Create an empty dataframe with fixed columns for Gradio tables."""
    return pd.DataFrame(columns=columns)


def render_status(message: str, tone: str = "neutral") -> str:
    """Render a styled HTML status message."""
    return f"<div class='status-card {tone}'>{message}</div>"


def grayscale_action(image_path: Optional[str]) -> tuple[Optional[object], str]:
    """Generate a grayscale image for the current upload."""
    try:
        grayscale_image = convert_to_grayscale(image_path)
        return grayscale_image, render_status(
            "Grayscale conversion completed successfully.", "success"
        )
    except ImageProcessingError as exc:
        return None, render_status(str(exc), "error")


def details_action(
    image_path: Optional[str],
) -> tuple[pd.DataFrame, dict[str, object], str]:
    """Extract structured image details for display."""
    try:
        details = extract_image_details(image_path)
        rows = details_to_rows(details)
        return (
            pd.DataFrame(rows, columns=DETAIL_COLUMNS),
            details,
            render_status("Image details extracted successfully.", "success"),
        )
    except ImageProcessingError as exc:
        return (
            empty_dataframe(DETAIL_COLUMNS),
            {},
            render_status(str(exc), "error"),
        )


def recognition_action(
    image_path: Optional[str],
) -> tuple[dict[str, float], pd.DataFrame, str]:
    """Run image recognition on the current upload."""
    try:
        label_scores, predictions, summary = recognize_image(image_path, top_k=5)
        prediction_rows = predictions_to_rows(predictions)
        return (
            label_scores,
            pd.DataFrame(prediction_rows, columns=PREDICTION_COLUMNS),
            render_status(summary, "success"),
        )
    except ImageProcessingError as exc:
        return {}, empty_dataframe(PREDICTION_COLUMNS), render_status(str(exc), "error")


def edge_detection_action(image_path: Optional[str]) -> tuple[Optional[object], str]:
    """Generate a simple edge-detected preview for the current upload."""
    try:
        edges_image = detect_edges(image_path)
        return edges_image, render_status(
            "Edge detection completed successfully.", "success"
        )
    except ImageProcessingError as exc:
        return None, render_status(str(exc), "error")


def save_snapshot_action(image_path: Optional[str]) -> tuple[Optional[str], str]:
    """Save the current upload or webcam frame to the snapshots folder."""
    try:
        snapshot_path = save_snapshot(image_path)
        return str(snapshot_path), render_status(
            f"Snapshot saved to {snapshot_path}.", "success"
        )
    except ImageProcessingError as exc:
        return None, render_status(str(exc), "error")


def build_demo() -> gr.Blocks:
    """Create the Gradio app for the image-processing assignment."""
    with gr.Blocks(title=APP_TITLE, fill_width=True) as demo:
        gr.HTML(
            """
            <section class="hero-card">
              <div class="hero-kicker">Week 6 | Image Processing</div>
              <h1>Image Processing Studio</h1>
              <p>
                Upload or capture an image, then explore four processing paths:
                grayscale conversion, technical image details, EfficientNet-based
                recognition, and a bonus edge-detection preview. Webcam snapshots
                can also be saved locally for later review.
              </p>
              <div class="hero-meta">
                <span class="hero-chip">4 live processing modes</span>
                <span class="hero-chip">Webcam capture ready</span>
                <span class="hero-chip">EfficientNet recognition</span>
                <span class="hero-chip">Snapshot export included</span>
              </div>
            </section>
            """
        )
        gr.HTML(
            """
            <section class="mode-strip">
              <article class="mode-card">
                <div class="mode-index">01</div>
                <h3>Grayscale</h3>
                <p>Turn any upload into a crisp monochrome study.</p>
              </article>
              <article class="mode-card">
                <div class="mode-index">02</div>
                <h3>Image Details</h3>
                <p>Inspect format, dimensions, orientation, and file characteristics.</p>
              </article>
              <article class="mode-card">
                <div class="mode-index">03</div>
                <h3>Recognition</h3>
                <p>Estimate the most likely object classes with a pre-trained model.</p>
              </article>
              <article class="mode-card">
                <div class="mode-index">04</div>
                <h3>Edge Detection</h3>
                <p>Highlight contours and contrast boundaries as a bonus effect.</p>
              </article>
            </section>
            """
        )

        with gr.Row():
            with gr.Column(scale=4, min_width=320, elem_classes="upload-panel"):
                gr.HTML(
                    """
                    <section class="panel-heading">
                      <div class="panel-kicker">Input Canvas</div>
                      <h2>Bring in an image</h2>
                      <p>Upload from disk, paste from your clipboard, or capture a fresh frame from the webcam.</p>
                    </section>
                    """
                )
                image_input = gr.Image(
                    label="Upload or capture an image",
                    type="filepath",
                    sources=["upload", "webcam", "clipboard"],
                    height=420,
                    buttons=["download", "fullscreen"],
                )
                gr.Markdown(
                    "Supported workflow: upload from disk, paste from clipboard, "
                    "or capture directly from your webcam."
                )

                with gr.Row():
                    save_snapshot_button = gr.Button(
                        "Save snapshot",
                        variant="secondary",
                    )
                    snapshot_file = gr.File(
                        label="Saved snapshot",
                        interactive=False,
                        visible=True,
                    )

                snapshot_status = gr.HTML(
                    render_status(
                        "Capture or upload an image, then save a snapshot if you want a local copy."
                    )
                )

            with gr.Column(scale=6, elem_classes="results-panel"):
                gr.HTML(
                    """
                    <section class="panel-heading">
                      <div class="panel-kicker">Processing Lab</div>
                      <h2>Choose a transformation</h2>
                      <p>Each tab focuses on a different output mode, from quick analysis to model-based interpretation.</p>
                    </section>
                    """
                )
                with gr.Tabs():
                    with gr.Tab("Grayscale"):
                        gr.Markdown(
                            "Convert the current image into a monochrome version that keeps its original dimensions."
                        )
                        grayscale_button = gr.Button(
                            "Generate grayscale image",
                            variant="primary",
                        )
                        grayscale_output = gr.Image(
                            label="Grayscale result",
                            type="pil",
                            image_mode="L",
                            height=420,
                            buttons=["download", "fullscreen"],
                        )
                        grayscale_status = gr.HTML(
                            render_status("Ready to create a grayscale version.")
                        )

                    with gr.Tab("Image details"):
                        gr.Markdown(
                            "Inspect the uploaded file to see its format, resolution, orientation, size, and transparency information."
                        )
                        details_button = gr.Button(
                            "Extract image details",
                            variant="primary",
                        )
                        details_table = gr.Dataframe(
                            headers=DETAIL_COLUMNS,
                            value=empty_dataframe(DETAIL_COLUMNS),
                            interactive=False,
                            wrap=True,
                            label="Details table",
                        )
                        details_json = gr.JSON(
                            value={},
                            label="Raw details",
                            open=False,
                        )
                        details_status = gr.HTML(
                            render_status("Ready to inspect the current image.")
                        )

                    with gr.Tab("Recognition"):
                        gr.Markdown(
                            "Run a pre-trained EfficientNet-B0 classifier and review the top predictions with confidence scores."
                        )
                        recognition_button = gr.Button(
                            "Recognize objects",
                            variant="primary",
                        )
                        recognition_label = gr.Label(
                            value={},
                            label="Top predictions",
                            num_top_classes=5,
                        )
                        recognition_table = gr.Dataframe(
                            headers=PREDICTION_COLUMNS,
                            value=empty_dataframe(PREDICTION_COLUMNS),
                            interactive=False,
                            wrap=True,
                            label="Prediction table",
                        )
                        recognition_status = gr.HTML(
                            render_status(
                                "Ready to run object recognition with EfficientNet-B0."
                            )
                        )

                    with gr.Tab("Edge detection"):
                        gr.Markdown(
                            "Bonus feature: generate a simple edge-detection preview to highlight outlines and strong contrast transitions."
                        )
                        edge_button = gr.Button(
                            "Detect edges",
                            variant="primary",
                        )
                        edge_output = gr.Image(
                            label="Edge-detected result",
                            type="pil",
                            image_mode="L",
                            height=420,
                            buttons=["download", "fullscreen"],
                        )
                        edge_status = gr.HTML(
                            render_status("Ready to generate an edge preview.")
                        )

        save_snapshot_button.click(
            fn=save_snapshot_action,
            inputs=image_input,
            outputs=[snapshot_file, snapshot_status],
        )
        grayscale_button.click(
            fn=grayscale_action,
            inputs=image_input,
            outputs=[grayscale_output, grayscale_status],
        )
        details_button.click(
            fn=details_action,
            inputs=image_input,
            outputs=[details_table, details_json, details_status],
        )
        recognition_button.click(
            fn=recognition_action,
            inputs=image_input,
            outputs=[recognition_label, recognition_table, recognition_status],
        )
        edge_button.click(
            fn=edge_detection_action,
            inputs=image_input,
            outputs=[edge_output, edge_status],
        )

    return demo


if __name__ == "__main__":
    build_demo().launch(theme=APP_THEME, css=APP_CSS, footer_links=[])
