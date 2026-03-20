from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Optional

import gradio as gr
import pandas as pd

from bird_api_client import BirdAPIClient, BirdAPIError

APP_TITLE = "Birds Viewer"
DEFAULT_WINGSPAN_CM = 50
DEFAULT_CONSERVATION_STATUS = "Least Concern"
APP_THEME = gr.themes.Soft(
    primary_hue="teal",
    secondary_hue="amber",
    neutral_hue="stone",
)
APP_CSS = """
.gradio-container {
  font-family: "Montserrat", "Aptos", "Trebuchet MS", sans-serif;
  background:
    radial-gradient(circle at top left, rgba(125, 196, 173, 0.26), transparent 24%),
    radial-gradient(circle at bottom right, rgba(226, 181, 95, 0.22), transparent 20%),
    linear-gradient(180deg, #f3efe7 0%, #f7f3ea 100%);
}
footer {
  display: none !important;
}
.hero-card {
  background:
    radial-gradient(circle at top right, rgba(255, 226, 168, 0.18), transparent 24%),
    linear-gradient(135deg, rgba(30, 46, 57, 0.97), rgba(50, 74, 67, 0.94));
  color: #f8f4eb;
  padding: 1.6rem 1.8rem;
  border-radius: 28px;
  box-shadow: 0 20px 46px rgba(34, 41, 36, 0.18);
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
  font-size: 2.15rem;
  line-height: 1.05;
}
.hero-card p {
  margin: 0.85rem 0 0;
  max-width: 55rem;
  color: rgba(248, 244, 235, 0.9);
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
  border: 1px solid rgba(247, 241, 227, 0.14);
  background: rgba(247, 241, 227, 0.08);
  color: rgba(247, 241, 227, 0.92);
  border-radius: 999px;
  padding: 0.42rem 0.8rem;
  font-size: 0.82rem;
  font-weight: 700;
}
.mode-strip {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 0.9rem;
  margin: 0.35rem 0 1.15rem;
}
.mode-card {
  background: rgba(255, 252, 246, 0.74);
  border: 1px solid rgba(96, 83, 66, 0.1);
  border-radius: 22px;
  padding: 1rem 1.05rem 0.95rem;
  box-shadow: 0 14px 30px rgba(55, 43, 33, 0.08);
}
.mode-index {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 2.1rem;
  height: 2.1rem;
  border-radius: 999px;
  background: linear-gradient(135deg, #0f766e, #14b8a6);
  color: #f7fbfa;
  font-size: 0.8rem;
  font-weight: 800;
  letter-spacing: 0.08em;
}
.mode-card h3 {
  margin: 0.8rem 0 0.3rem;
  font-size: 1rem;
  color: #34281f;
}
.mode-card p {
  margin: 0;
  color: #6d5a4b;
  font-size: 0.92rem;
  line-height: 1.45;
}
.viewer-shell {
  background: rgba(255, 250, 242, 0.65);
  border: 1px solid rgba(109, 87, 68, 0.12);
  border-radius: 28px;
  padding: 1rem;
  box-shadow: 0 18px 38px rgba(57, 42, 28, 0.1);
  backdrop-filter: blur(8px);
}
.viewer-shell [role="tablist"] {
  gap: 0.45rem;
  padding: 0.1rem 0 0.7rem;
  border-bottom: 1px solid rgba(80, 67, 54, 0.18);
}
.viewer-shell [role="tab"] {
  color: #7b6550 !important;
  font-weight: 700;
  border-radius: 999px;
  padding: 0.6rem 1rem !important;
  transition: background 0.2s ease, color 0.2s ease, transform 0.2s ease;
}
.viewer-shell [role="tab"]:hover {
  color: #2c231b !important;
  background: rgba(255, 255, 255, 0.62);
}
.viewer-shell [role="tab"][aria-selected="true"] {
  color: #f6fcfb !important;
  background: linear-gradient(135deg, #0f766e, #14b8a6);
  box-shadow: 0 12px 24px rgba(15, 118, 110, 0.22);
}
.viewer-shell [role="tabpanel"] {
  padding-top: 0.55rem;
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
  font-size: 1.28rem;
  color: #33271f;
}
.panel-heading p {
  margin: 0.35rem 0 0;
  color: #6d5a4b;
  line-height: 1.5;
  font-size: 0.95rem;
}
.viewer-shell .prose,
.viewer-shell .prose p,
.viewer-shell .prose li {
  color: #5e4c3e !important;
}
.viewer-shell label,
.viewer-shell .block-label {
  color: #4b3c31 !important;
  font-weight: 700;
}
.viewer-shell button.primary {
  background: linear-gradient(135deg, #0f766e, #14b8a6) !important;
  color: #fff8ef !important;
  border: none !important;
  box-shadow: 0 12px 24px rgba(15, 118, 110, 0.2);
}
.viewer-shell button.secondary {
  background: linear-gradient(135deg, #55606d, #39414a) !important;
  color: #fff8ef !important;
  border: none !important;
}
.viewer-shell button.primary:hover,
.viewer-shell button.secondary:hover {
  filter: brightness(1.04);
  transform: translateY(-1px);
}
.viewer-shell .wrap {
  border-radius: 18px !important;
}
.status-card {
  border-radius: 16px;
  padding: 0.85rem 1rem;
  font-size: 0.95rem;
  border: 1px solid transparent;
}
.status-card.success {
  background: rgba(86, 140, 122, 0.11);
  border-color: rgba(86, 140, 122, 0.24);
  color: #183d31;
}
.status-card.error {
  background: rgba(165, 76, 71, 0.1);
  border-color: rgba(165, 76, 71, 0.22);
  color: #5d1d19;
}
.status-card.neutral {
  background: rgba(102, 88, 74, 0.08);
  border-color: rgba(102, 88, 74, 0.14);
  color: #43362b;
}
"""
SPECIES_COLUMNS = [
    "id",
    "name",
    "scientific_name",
    "family",
    "conservation_status",
    "wingspan_cm",
]
BIRDS_COLUMNS = ["id", "nickname", "ring_code", "age", "species"]
SIGHTINGS_COLUMNS = [
    "id",
    "bird",
    "species",
    "spotted_at",
    "location",
    "observer_name",
    "notes",
]
CONSERVATION_STATUSES = [
    "Least Concern",
    "Near Threatened",
    "Vulnerable",
    "Endangered",
    "Critically Endangered",
    "Extinct in the Wild",
    "Extinct",
]
KNOWN_BIRD_FAMILIES = sorted(
    {
        "Accipitridae",
        "Alcedinidae",
        "Anatidae",
        "Apodidae",
        "Ardeidae",
        "Ciconiidae",
        "Columbidae",
        "Corvidae",
        "Falconidae",
        "Fringillidae",
        "Laridae",
        "Muscicapidae",
        "Paridae",
        "Passeridae",
        "Strigidae",
        "Sturnidae",
        "Sylviidae",
        "Troglodytidae",
        "Turdidae",
        "Tytonidae",
    }
)


def empty_dataframe(columns: list[str]) -> pd.DataFrame:
    """Create a typed empty dataframe with stable columns for Gradio."""
    return pd.DataFrame(columns=columns)


def render_status(message: str, tone: str = "neutral") -> str:
    """Render a styled HTML status message."""
    return f"<div class='status-card {tone}'>{message}</div>"


def normalize_filter(value: Optional[str]) -> Optional[str]:
    """Convert empty or 'All' UI values into API-friendly filters."""
    if value is None:
        return None
    cleaned = str(value).strip()
    if not cleaned or cleaned.lower() == "all":
        return None
    return cleaned


def format_species_label(species: dict[str, Any]) -> str:
    """Create a compact label for species dropdowns."""
    return f"{species['name']} ({species['scientific_name']})"


def format_bird_label(
    bird: dict[str, Any], species_lookup: dict[int, dict[str, Any]]
) -> str:
    """Create a human-friendly bird label with ring code and species name."""
    species = species_lookup.get(bird["species_id"])
    species_name = species["name"] if species else f"Species #{bird['species_id']}"
    return f"{bird['nickname']} [{bird['ring_code']}] - {species_name}"


def build_species_lookup(
    species_items: list[dict[str, Any]],
) -> dict[int, dict[str, Any]]:
    """Index species by id for fast relation lookups."""
    return {item["id"]: item for item in species_items}


def build_bird_lookup(bird_items: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    """Index birds by id for fast relation lookups."""
    return {item["id"]: item for item in bird_items}


def build_species_choices(
    species_items: list[dict[str, Any]],
) -> list[tuple[str, int]]:
    """Convert species records into Gradio dropdown choices."""
    return [(format_species_label(item), item["id"]) for item in species_items]


def build_bird_choices(
    bird_items: list[dict[str, Any]],
    species_lookup: dict[int, dict[str, Any]],
) -> list[tuple[str, int]]:
    """Convert bird records into Gradio dropdown choices."""
    return [
        (format_bird_label(item, species_lookup), item["id"]) for item in bird_items
    ]


def build_species_dataframe(species_items: list[dict[str, Any]]) -> pd.DataFrame:
    """Prepare species data for the read-only table."""
    rows = [
        {
            "id": item["id"],
            "name": item["name"],
            "scientific_name": item["scientific_name"],
            "family": item["family"],
            "conservation_status": item["conservation_status"],
            "wingspan_cm": float(item["wingspan_cm"]),
        }
        for item in species_items
    ]
    if not rows:
        return empty_dataframe(SPECIES_COLUMNS)
    return pd.DataFrame(rows, columns=SPECIES_COLUMNS)


def build_birds_dataframe(
    bird_items: list[dict[str, Any]],
    species_lookup: dict[int, dict[str, Any]],
) -> pd.DataFrame:
    """Prepare birds data for the read-only table."""
    rows = []
    for item in bird_items:
        species = species_lookup.get(item["species_id"])
        species_name = species["name"] if species else f"Species #{item['species_id']}"
        rows.append(
            {
                "id": item["id"],
                "nickname": item["nickname"],
                "ring_code": item["ring_code"],
                "age": item["age"],
                "species": species_name,
            }
        )
    if not rows:
        return empty_dataframe(BIRDS_COLUMNS)
    return pd.DataFrame(rows, columns=BIRDS_COLUMNS)


def build_sightings_dataframe(
    sighting_items: list[dict[str, Any]],
    bird_lookup: dict[int, dict[str, Any]],
    species_lookup: dict[int, dict[str, Any]],
) -> pd.DataFrame:
    """Prepare birdspotting data for the read-only table."""
    rows = []
    for item in sighting_items:
        bird = bird_lookup.get(item["bird_id"])
        bird_name = bird["nickname"] if bird else f"Bird #{item['bird_id']}"
        species_name = ""
        if bird:
            species = species_lookup.get(bird["species_id"])
            species_name = species["name"] if species else f"Species #{bird['species_id']}"
        rows.append(
            {
                "id": item["id"],
                "bird": bird_name,
                "species": species_name,
                "spotted_at": format_timestamp(item["spotted_at"]),
                "location": item["location"],
                "observer_name": item["observer_name"],
                "notes": item.get("notes") or "",
            }
        )
    if not rows:
        return empty_dataframe(SIGHTINGS_COLUMNS)
    return pd.DataFrame(rows, columns=SIGHTINGS_COLUMNS)


def format_timestamp(value: Any) -> str:
    """Format API timestamps into a more readable local string."""
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")

    raw_value = str(value).strip()
    if not raw_value:
        return ""

    try:
        parsed = datetime.fromisoformat(raw_value.replace("Z", "+00:00"))
    except ValueError:
        return raw_value
    return parsed.strftime("%Y-%m-%d %H:%M:%S")


def refresh_species_data(
    client: BirdAPIClient, conservation_status: Optional[str]
) -> tuple[pd.DataFrame, str]:
    """Fetch and format species data for the UI."""
    try:
        species_items = client.list_species(
            conservation_status=normalize_filter(conservation_status)
        )
    except BirdAPIError as exc:
        return empty_dataframe(SPECIES_COLUMNS), render_status(
            f"Species refresh failed: {exc}", "error"
        )

    return (
        build_species_dataframe(species_items),
        render_status(
            f"Loaded {len(species_items)} species from {client.base_url}.",
            "success",
        ),
    )


def refresh_birds_data(
    client: BirdAPIClient,
) -> tuple[pd.DataFrame, str, gr.update]:
    """Fetch birds and species data for the birds tab."""
    try:
        species_items = client.list_species()
        bird_items = client.list_birds()
    except BirdAPIError as exc:
        return (
            empty_dataframe(BIRDS_COLUMNS),
            render_status(f"Bird refresh failed: {exc}", "error"),
            gr.update(choices=[], value=None),
        )

    species_lookup = build_species_lookup(species_items)
    species_choices = build_species_choices(species_items)
    default_species_id = species_choices[0][1] if species_choices else None
    return (
        build_birds_dataframe(bird_items, species_lookup),
        render_status(
            f"Loaded {len(bird_items)} birds from {client.base_url}.", "success"
        ),
        gr.update(choices=species_choices, value=default_species_id),
    )


def refresh_sightings_data(
    client: BirdAPIClient, observer_name: Optional[str]
) -> tuple[pd.DataFrame, str, gr.update]:
    """Fetch sightings, birds, and species data for the sightings tab."""
    try:
        species_items = client.list_species()
        bird_items = client.list_birds()
        sighting_items = client.list_birdspottings(
            observer_name=normalize_filter(observer_name)
        )
    except BirdAPIError as exc:
        return (
            empty_dataframe(SIGHTINGS_COLUMNS),
            render_status(f"Sightings refresh failed: {exc}", "error"),
            gr.update(choices=[], value=None),
        )

    species_lookup = build_species_lookup(species_items)
    bird_lookup = build_bird_lookup(bird_items)
    bird_choices = build_bird_choices(bird_items, species_lookup)
    default_bird_id = bird_choices[0][1] if bird_choices else None
    return (
        build_sightings_dataframe(sighting_items, bird_lookup, species_lookup),
        render_status(
            f"Loaded {len(sighting_items)} sightings from {client.base_url}.",
            "success",
        ),
        gr.update(choices=bird_choices, value=default_bird_id),
    )


def create_species_action(
    client: BirdAPIClient,
    name: str,
    scientific_name: str,
    family: str,
    conservation_status: str,
    wingspan_cm: float,
    active_filter: Optional[str],
) -> tuple[str, pd.DataFrame, str, str, Optional[str], str, float]:
    """Create a species and refresh the species table."""
    cleaned_name = (name or "").strip()
    cleaned_scientific_name = (scientific_name or "").strip()
    cleaned_family = (family or "").strip()
    if not all([cleaned_name, cleaned_scientific_name, cleaned_family]):
        dataframe, _ = refresh_species_data(client, active_filter)
        return (
            render_status(
                "Species could not be created: fill in name, scientific name, and family.",
                "error",
            ),
            dataframe,
            name,
            scientific_name,
            family,
            conservation_status,
            wingspan_cm,
        )

    try:
        wingspan = Decimal(str(wingspan_cm))
    except (InvalidOperation, ValueError):
        dataframe, _ = refresh_species_data(client, active_filter)
        return (
            render_status(
                "Species could not be created: wingspan must be a valid number.",
                "error",
            ),
            dataframe,
            name,
            scientific_name,
            family,
            conservation_status,
            wingspan_cm,
        )

    try:
        created = client.create_species(
            {
                "name": cleaned_name,
                "scientific_name": cleaned_scientific_name,
                "family": cleaned_family,
                "conservation_status": conservation_status,
                "wingspan_cm": str(wingspan),
            }
        )
        dataframe, _ = refresh_species_data(client, active_filter)
    except BirdAPIError as exc:
        dataframe, _ = refresh_species_data(client, active_filter)
        return (
            render_status(f"Species could not be created: {exc}", "error"),
            dataframe,
            name,
            scientific_name,
            family,
            conservation_status,
            wingspan_cm,
        )

    return (
        render_status(
            f"Created species #{created['id']}: {created['name']}.", "success"
        ),
        dataframe,
        "",
        "",
        None,
        DEFAULT_CONSERVATION_STATUS,
        DEFAULT_WINGSPAN_CM,
    )


def create_bird_action(
    client: BirdAPIClient,
    nickname: str,
    ring_code: str,
    age: float,
    species_id: Optional[int],
) -> tuple[str, pd.DataFrame, gr.update, str, str, float]:
    """Create a bird and refresh the birds table and dropdown choices."""
    cleaned_nickname = (nickname or "").strip()
    cleaned_ring_code = (ring_code or "").strip()
    if not cleaned_nickname or not cleaned_ring_code:
        dataframe, _, species_dropdown = refresh_birds_data(client)
        return (
            render_status(
                "Bird could not be created: fill in nickname and ring code.",
                "error",
            ),
            dataframe,
            species_dropdown,
            nickname,
            ring_code,
            age,
        )

    if species_id is None:
        dataframe, _, species_dropdown = refresh_birds_data(client)
        return (
            render_status(
                "Bird could not be created: choose a species first.", "error"
            ),
            dataframe,
            species_dropdown,
            nickname,
            ring_code,
            age,
        )

    try:
        created = client.create_bird(
            {
                "nickname": cleaned_nickname,
                "ring_code": cleaned_ring_code,
                "age": int(age),
                "species_id": species_id,
            }
        )
        dataframe, _, species_dropdown = refresh_birds_data(client)
    except (ValueError, TypeError):
        dataframe, _, species_dropdown = refresh_birds_data(client)
        return (
            render_status(
                "Bird could not be created: age must be a whole number.", "error"
            ),
            dataframe,
            species_dropdown,
            nickname,
            ring_code,
            age,
        )
    except BirdAPIError as exc:
        dataframe, _, species_dropdown = refresh_birds_data(client)
        return (
            render_status(f"Bird could not be created: {exc}", "error"),
            dataframe,
            species_dropdown,
            nickname,
            ring_code,
            age,
        )

    return (
        render_status(
            f"Created bird #{created['id']}: {created['nickname']}.", "success"
        ),
        dataframe,
        species_dropdown,
        "",
        "",
        0,
    )


def create_sighting_action(
    client: BirdAPIClient,
    bird_id: Optional[int],
    spotted_at: str,
    location: str,
    observer_name: str,
    notes: str,
    active_observer_filter: Optional[str],
) -> tuple[str, pd.DataFrame, gr.update, str, str, str, str]:
    """Create a sighting and refresh the sightings table and dropdown choices."""
    cleaned_location = (location or "").strip()
    cleaned_observer_name = (observer_name or "").strip()
    if not cleaned_location or not cleaned_observer_name:
        dataframe, _, bird_dropdown = refresh_sightings_data(client, active_observer_filter)
        return (
            render_status(
                "Sighting could not be created: fill in location and observer name.",
                "error",
            ),
            dataframe,
            bird_dropdown,
            spotted_at,
            location,
            observer_name,
            notes,
        )

    if bird_id is None:
        dataframe, _, bird_dropdown = refresh_sightings_data(client, active_observer_filter)
        return (
            render_status(
                "Sighting could not be created: choose a bird first.", "error"
            ),
            dataframe,
            bird_dropdown,
            spotted_at,
            location,
            observer_name,
            notes,
        )

    timestamp = (spotted_at or "").strip()
    try:
        datetime.fromisoformat(timestamp)
    except ValueError:
        dataframe, _, bird_dropdown = refresh_sightings_data(client, active_observer_filter)
        return (
            render_status(
                "Sighting could not be created: use ISO 8601 format like 2026-03-20T14:30:00.",
                "error",
            ),
            dataframe,
            bird_dropdown,
            spotted_at,
            location,
            observer_name,
            notes,
        )

    try:
        created = client.create_birdspotting(
            {
                "bird_id": bird_id,
                "spotted_at": timestamp,
                "location": cleaned_location,
                "observer_name": cleaned_observer_name,
                "notes": (notes or "").strip() or None,
            }
        )
        dataframe, _, bird_dropdown = refresh_sightings_data(
            client, active_observer_filter
        )
    except BirdAPIError as exc:
        dataframe, _, bird_dropdown = refresh_sightings_data(client, active_observer_filter)
        return (
            render_status(f"Sighting could not be created: {exc}", "error"),
            dataframe,
            bird_dropdown,
            spotted_at,
            location,
            observer_name,
            notes,
        )

    return (
        render_status(
            f"Created sighting #{created['id']} for bird #{created['bird_id']}.",
            "success",
        ),
        dataframe,
        bird_dropdown,
        datetime.now().replace(microsecond=0).isoformat(),
        "",
        "",
        "",
    )


def build_demo(client: Optional[BirdAPIClient] = None) -> gr.Blocks:
    """Create the Gradio Blocks app for the Bird API integration exercise."""
    api_client = client or BirdAPIClient()

    with gr.Blocks(title=APP_TITLE, fill_width=True) as demo:
        gr.HTML(
            f"""
            <section class="hero-card">
              <div class="hero-kicker">Week 6 | Bird API Integration</div>
              <h1>Birds Viewer</h1>
              <p>
                Explore live species, birds, and sighting records from your FastAPI backend at
                <strong>{api_client.base_url}</strong>. This dashboard is designed for quick inspection,
                lightweight data entry, and relationship-aware browsing across the whole birds domain.
              </p>
              <div class="hero-meta">
                <span class="hero-chip">Live PostgreSQL data</span>
                <span class="hero-chip">Species, birds, sightings</span>
                <span class="hero-chip">Linked dropdown workflows</span>
                <span class="hero-chip">Filter and refresh ready</span>
              </div>
            </section>
            """
        )
        gr.HTML(
            """
            <section class="mode-strip">
              <article class="mode-card">
                <div class="mode-index">01</div>
                <h3>Species Registry</h3>
                <p>Review conservation profiles and add new species with curated status and family inputs.</p>
              </article>
              <article class="mode-card">
                <div class="mode-index">02</div>
                <h3>Bird Directory</h3>
                <p>Manage individual birds and connect them directly to the correct species records.</p>
              </article>
              <article class="mode-card">
                <div class="mode-index">03</div>
                <h3>Sightings Feed</h3>
                <p>Track observations by bird, observer, and location with readable timestamps.</p>
              </article>
            </section>
            """
        )

        with gr.Column(elem_classes="viewer-shell"):
            with gr.Tabs():
                with gr.Tab("Species"):
                    gr.HTML(
                        """
                        <section class="panel-heading">
                          <div class="panel-kicker">Species Registry</div>
                          <h2>Browse and create species</h2>
                          <p>Filter by conservation status, inspect the core species table, and add new entries with sensible defaults.</p>
                        </section>
                        """
                    )
                    with gr.Row():
                        species_filter = gr.Dropdown(
                            choices=["All", *CONSERVATION_STATUSES],
                            value="All",
                            label="Filter by conservation status",
                        )
                        species_refresh_button = gr.Button(
                            "Refresh", variant="secondary"
                        )

                    species_status = gr.HTML(
                        render_status("Use refresh to load species data.")
                    )
                    species_table = gr.Dataframe(
                        headers=SPECIES_COLUMNS,
                        value=empty_dataframe(SPECIES_COLUMNS),
                        interactive=False,
                        show_search="filter",
                        wrap=True,
                        max_height=350,
                        label="Species",
                    )

                    with gr.Accordion("Add new species", open=False):
                        with gr.Row():
                            species_name = gr.Textbox(
                                label="Name",
                                placeholder="e.g. Atlantic Puffin",
                            )
                            species_scientific_name = gr.Textbox(
                                label="Scientific name",
                                placeholder="e.g. Fratercula arctica",
                            )
                        with gr.Row():
                            species_family = gr.Dropdown(
                                choices=KNOWN_BIRD_FAMILIES,
                                label="Family",
                                filterable=True,
                                allow_custom_value=True,
                            )
                            species_conservation_status = gr.Dropdown(
                                choices=CONSERVATION_STATUSES,
                                value=DEFAULT_CONSERVATION_STATUS,
                                label="Conservation status",
                            )
                            species_wingspan = gr.Slider(
                                minimum=5,
                                maximum=300,
                                step=5,
                                value=DEFAULT_WINGSPAN_CM,
                                label="Wingspan (cm)",
                            )
                        species_create_button = gr.Button(
                            "Create species",
                            variant="primary",
                        )

                with gr.Tab("Birds"):
                    gr.HTML(
                        """
                        <section class="panel-heading">
                          <div class="panel-kicker">Bird Directory</div>
                          <h2>Manage individual birds</h2>
                          <p>Review each bird alongside its linked species and add new ringed birds with species-aware dropdown selection.</p>
                        </section>
                        """
                    )
                    with gr.Row():
                        birds_status = gr.HTML(
                            render_status("Use refresh to load bird data.")
                        )
                        birds_refresh_button = gr.Button(
                            "Refresh", variant="secondary"
                        )

                    birds_table = gr.Dataframe(
                        headers=BIRDS_COLUMNS,
                        value=empty_dataframe(BIRDS_COLUMNS),
                        interactive=False,
                        show_search="filter",
                        wrap=True,
                        max_height=350,
                        label="Birds",
                    )

                    with gr.Accordion("Add new bird", open=False):
                        with gr.Row():
                            bird_nickname = gr.Textbox(
                                label="Nickname",
                                placeholder="e.g. Skipper",
                            )
                            bird_ring_code = gr.Textbox(
                                label="Ring code",
                                placeholder="e.g. AB-1234",
                            )
                        with gr.Row():
                            bird_age = gr.Number(
                                label="Age (years)",
                                value=0,
                                minimum=0,
                                precision=0,
                            )
                            bird_species_id = gr.Dropdown(
                                choices=[],
                                label="Species",
                                filterable=True,
                                allow_custom_value=False,
                            )
                        with gr.Row():
                            birds_refresh_species_button = gr.Button(
                                "Refresh species list",
                                variant="secondary",
                            )
                            bird_create_button = gr.Button(
                                "Create bird",
                                variant="primary",
                            )

                with gr.Tab("Sightings"):
                    gr.HTML(
                        """
                        <section class="panel-heading">
                          <div class="panel-kicker">Sightings Feed</div>
                          <h2>Record bird observations</h2>
                          <p>Filter the sightings stream, inspect readable observation rows, and add new records tied to existing birds.</p>
                        </section>
                        """
                    )
                    with gr.Row():
                        observer_filter = gr.Textbox(
                            label="Filter by observer name",
                            placeholder="e.g. Nina Peeters",
                        )
                        sightings_refresh_button = gr.Button(
                            "Refresh", variant="secondary"
                        )

                    sightings_status = gr.HTML(
                        render_status("Use refresh to load sightings data.")
                    )
                    sightings_table = gr.Dataframe(
                        headers=SIGHTINGS_COLUMNS,
                        value=empty_dataframe(SIGHTINGS_COLUMNS),
                        interactive=False,
                        show_search="filter",
                        wrap=True,
                        max_height=350,
                        label="Sightings",
                    )

                    with gr.Accordion("Add new sighting", open=False):
                        with gr.Row():
                            sighting_bird_id = gr.Dropdown(
                                choices=[],
                                label="Bird",
                                filterable=True,
                                allow_custom_value=False,
                            )
                            sightings_refresh_birds_button = gr.Button(
                                "Refresh bird list",
                                variant="secondary",
                            )
                        with gr.Row():
                            sighting_spotted_at = gr.Textbox(
                                label="Spotted at (ISO 8601)",
                                placeholder="e.g. 2026-03-20T14:30:00",
                                value=datetime.now().replace(microsecond=0).isoformat(),
                            )
                            sighting_location = gr.Textbox(
                                label="Location",
                                placeholder="e.g. Brussels Park",
                            )
                        with gr.Row():
                            sighting_observer = gr.Textbox(
                                label="Observer name",
                                placeholder="e.g. Nina Peeters",
                            )
                            sighting_notes = gr.Textbox(
                                label="Notes (optional)",
                                placeholder="e.g. Seen near the fountain",
                                lines=2,
                            )
                        sighting_create_button = gr.Button(
                            "Create sighting",
                            variant="primary",
                        )

        species_refresh_button.click(
            fn=lambda conservation_status: refresh_species_data(
                api_client, conservation_status
            ),
            inputs=species_filter,
            outputs=[species_table, species_status],
        )
        species_filter.change(
            fn=lambda conservation_status: refresh_species_data(
                api_client, conservation_status
            ),
            inputs=species_filter,
            outputs=[species_table, species_status],
        )
        species_create_button.click(
            fn=lambda name, scientific_name, family, conservation_status, wingspan, active_filter: create_species_action(
                api_client,
                name,
                scientific_name,
                family,
                conservation_status,
                wingspan,
                active_filter,
            ),
            inputs=[
                species_name,
                species_scientific_name,
                species_family,
                species_conservation_status,
                species_wingspan,
                species_filter,
            ],
            outputs=[
                species_status,
                species_table,
                species_name,
                species_scientific_name,
                species_family,
                species_conservation_status,
                species_wingspan,
            ],
        )

        birds_refresh_button.click(
            fn=lambda: refresh_birds_data(api_client),
            outputs=[birds_table, birds_status, bird_species_id],
        )
        birds_refresh_species_button.click(
            fn=lambda: refresh_birds_data(api_client),
            outputs=[birds_table, birds_status, bird_species_id],
        )
        bird_create_button.click(
            fn=lambda nickname, ring_code, age, species_id: create_bird_action(
                api_client,
                nickname,
                ring_code,
                age,
                species_id,
            ),
            inputs=[bird_nickname, bird_ring_code, bird_age, bird_species_id],
            outputs=[
                birds_status,
                birds_table,
                bird_species_id,
                bird_nickname,
                bird_ring_code,
                bird_age,
            ],
        )

        sightings_refresh_button.click(
            fn=lambda name: refresh_sightings_data(api_client, name),
            inputs=observer_filter,
            outputs=[sightings_table, sightings_status, sighting_bird_id],
        )
        sightings_refresh_birds_button.click(
            fn=lambda name: refresh_sightings_data(api_client, name),
            inputs=observer_filter,
            outputs=[sightings_table, sightings_status, sighting_bird_id],
        )
        observer_filter.submit(
            fn=lambda name: refresh_sightings_data(api_client, name),
            inputs=observer_filter,
            outputs=[sightings_table, sightings_status, sighting_bird_id],
        )
        sighting_create_button.click(
            fn=lambda bird_id, spotted_at, location, observer_name, notes, active_filter: create_sighting_action(
                api_client,
                bird_id,
                spotted_at,
                location,
                observer_name,
                notes,
                active_filter,
            ),
            inputs=[
                sighting_bird_id,
                sighting_spotted_at,
                sighting_location,
                sighting_observer,
                sighting_notes,
                observer_filter,
            ],
            outputs=[
                sightings_status,
                sightings_table,
                sighting_bird_id,
                sighting_spotted_at,
                sighting_location,
                sighting_observer,
                sighting_notes,
            ],
        )

        demo.load(
            fn=lambda conservation_status: refresh_species_data(
                api_client, conservation_status
            ),
            inputs=species_filter,
            outputs=[species_table, species_status],
        )
        demo.load(
            fn=lambda: refresh_birds_data(api_client),
            outputs=[birds_table, birds_status, bird_species_id],
        )
        demo.load(
            fn=lambda name: refresh_sightings_data(api_client, name),
            inputs=observer_filter,
            outputs=[sightings_table, sightings_status, sighting_bird_id],
        )

    return demo


if __name__ == "__main__":
    build_demo().launch(theme=APP_THEME, css=APP_CSS, footer_links=[])
