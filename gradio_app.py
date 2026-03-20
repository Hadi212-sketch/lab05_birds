from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Optional

import gradio as gr
import pandas as pd

from bird_api_client import BirdAPIClient, BirdAPIError

APP_TITLE = "Birds Viewer"
DEFAULT_WINGSPAN_CM = 50
DEFAULT_CONSERVATION_STATUS = "Least Concern"
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
        return empty_dataframe(SPECIES_COLUMNS), f"Species refresh failed: {exc}"

    return (
        build_species_dataframe(species_items),
        f"Loaded {len(species_items)} species from {client.base_url}.",
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
            f"Bird refresh failed: {exc}",
            gr.update(choices=[], value=None),
        )

    species_lookup = build_species_lookup(species_items)
    species_choices = build_species_choices(species_items)
    default_species_id = species_choices[0][1] if species_choices else None
    return (
        build_birds_dataframe(bird_items, species_lookup),
        f"Loaded {len(bird_items)} birds from {client.base_url}.",
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
            f"Sightings refresh failed: {exc}",
            gr.update(choices=[], value=None),
        )

    species_lookup = build_species_lookup(species_items)
    bird_lookup = build_bird_lookup(bird_items)
    bird_choices = build_bird_choices(bird_items, species_lookup)
    default_bird_id = bird_choices[0][1] if bird_choices else None
    return (
        build_sightings_dataframe(sighting_items, bird_lookup, species_lookup),
        f"Loaded {len(sighting_items)} sightings from {client.base_url}.",
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
            "Species could not be created: fill in name, scientific name, and family.",
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
            "Species could not be created: wingspan must be a valid number.",
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
            f"Species could not be created: {exc}",
            dataframe,
            name,
            scientific_name,
            family,
            conservation_status,
            wingspan_cm,
        )

    return (
        f"Created species #{created['id']}: {created['name']}.",
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
            "Bird could not be created: fill in nickname and ring code.",
            dataframe,
            species_dropdown,
            nickname,
            ring_code,
            age,
        )

    if species_id is None:
        dataframe, _, species_dropdown = refresh_birds_data(client)
        return (
            "Bird could not be created: choose a species first.",
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
            "Bird could not be created: age must be a whole number.",
            dataframe,
            species_dropdown,
            nickname,
            ring_code,
            age,
        )
    except BirdAPIError as exc:
        dataframe, _, species_dropdown = refresh_birds_data(client)
        return (
            f"Bird could not be created: {exc}",
            dataframe,
            species_dropdown,
            nickname,
            ring_code,
            age,
        )

    return (
        f"Created bird #{created['id']}: {created['nickname']}.",
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
            "Sighting could not be created: fill in location and observer name.",
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
            "Sighting could not be created: choose a bird first.",
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
            "Sighting could not be created: use ISO 8601 format like 2026-03-20T14:30:00.",
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
            f"Sighting could not be created: {exc}",
            dataframe,
            bird_dropdown,
            spotted_at,
            location,
            observer_name,
            notes,
        )

    return (
        f"Created sighting #{created['id']} for bird #{created['bird_id']}.",
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

    with gr.Blocks(title=APP_TITLE) as demo:
        gr.Markdown("# Birds Viewer")
        gr.Markdown(f"Live data from the Birds API at `{api_client.base_url}`.")

        with gr.Tabs():
            with gr.Tab("Species"):
                with gr.Row():
                    species_filter = gr.Dropdown(
                        choices=["All", *CONSERVATION_STATUSES],
                        value="All",
                        label="Filter by conservation status",
                    )
                    species_refresh_button = gr.Button("Refresh", variant="secondary")

                species_status = gr.Markdown("Use refresh to load species data.")
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
                birds_status = gr.Markdown("Use refresh to load bird data.")
                birds_table = gr.Dataframe(
                    headers=BIRDS_COLUMNS,
                    value=empty_dataframe(BIRDS_COLUMNS),
                    interactive=False,
                    show_search="filter",
                    wrap=True,
                    max_height=350,
                    label="Birds",
                )
                birds_refresh_button = gr.Button("Refresh", variant="secondary")

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
                with gr.Row():
                    observer_filter = gr.Textbox(
                        label="Filter by observer name",
                        placeholder="e.g. Nina Peeters",
                    )
                    sightings_refresh_button = gr.Button(
                        "Refresh", variant="secondary"
                    )

                sightings_status = gr.Markdown("Use refresh to load sightings data.")
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
    build_demo().launch(theme=gr.themes.Soft(primary_hue="blue", secondary_hue="slate"))
