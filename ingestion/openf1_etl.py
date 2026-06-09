import json
import time
import threading
import requests
import pandas as pd
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "https://api.openf1.org/v1"
YEAR = 2026
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "raw"
STATE_FILE = OUTPUT_DIR / ".etl_state.json"
DELAY = 1.0
MAX_RETRIES = 3
MAX_WORKERS = 4


# ── State management ──────────────────────────────────────────────────────────

def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {"processed_session_keys": []}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


# ── Fetching ──────────────────────────────────────────────────────────────────

def fetch_by_year(endpoint: str) -> pd.DataFrame:
    """Endpunkte die year direkt unterstützen (meetings, sessions)."""
    r = requests.get(f"{BASE_URL}/{endpoint}", params={"year": YEAR})
    r.raise_for_status()
    data = r.json()
    return pd.DataFrame(data) if data else pd.DataFrame()


def _fetch_single(endpoint: str, key: int, lock: threading.Lock) -> pd.DataFrame:
    for attempt in range(1, MAX_RETRIES + 1):
        r = requests.get(f"{BASE_URL}/{endpoint}", params={"session_key": key})
        if r.status_code == 429:
            wait = DELAY * 2 ** attempt
            with lock:
                print(f"  session_key={key} — 429, warte {wait:.0f}s...")
            time.sleep(wait)
            continue
        if r.status_code == 404:
            with lock:
                print(f"  session_key={key} — 404, übersprungen")
            time.sleep(DELAY)
            return pd.DataFrame()
        r.raise_for_status()
        break
    else:
        with lock:
            print(f"  session_key={key} — max. Retries erreicht, übersprungen")
        return pd.DataFrame()

    data = r.json()
    with lock:
        print(f"  session_key={key} — {len(data)} Zeilen")
    time.sleep(DELAY)
    return pd.DataFrame(data) if data else pd.DataFrame()


def fetch_by_session(endpoint: str, session_keys: list[int]) -> pd.DataFrame:
    lock = threading.Lock()
    frames = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(_fetch_single, endpoint, key, lock): key
            for key in session_keys
        }
        for future in as_completed(futures):
            df = future.result()
            if not df.empty:
                frames.append(df)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


# ── Saving (mit Append-Logik) ─────────────────────────────────────────────────

def save(df: pd.DataFrame, name: str) -> None:
    """Überschreibt die Datei komplett (für kleine Stammdaten)."""
    if df.empty:
        print(f"[SKIP] {name} — keine Daten")
        return
    path = OUTPUT_DIR / f"{name}.parquet"
    df.to_parquet(path, index=False)
    print(f"[OK]   {name}: {df.shape[0]} Zeilen, {df.shape[1]} Spalten")


def append_or_create(new_df: pd.DataFrame, name: str) -> pd.DataFrame:
    """Hängt neue Daten an existierendes Parquet an (für session-basierte Daten)."""
    if new_df.empty:
        print(f"[SKIP] {name} — keine neuen Daten")
        path = OUTPUT_DIR / f"{name}.parquet"
        return pd.read_parquet(path) if path.exists() else pd.DataFrame()

    path = OUTPUT_DIR / f"{name}.parquet"
    if path.exists():
        existing = pd.read_parquet(path)
        combined = pd.concat([existing, new_df], ignore_index=True)
        combined.to_parquet(path, index=False)
        print(f"[OK]   {name}: +{new_df.shape[0]} neue Zeilen → {combined.shape[0]} gesamt")
        return combined
    else:
        new_df.to_parquet(path, index=False)
        print(f"[OK]   {name}: {new_df.shape[0]} Zeilen (neu erstellt)")
        return new_df


# ── Abgeleitete Tabellen ──────────────────────────────────────────────────────

def derive_starting_grid(positions: pd.DataFrame) -> pd.DataFrame:
    positions["date"] = pd.to_datetime(positions["date"], format='ISO8601')
    return (
        positions
        .sort_values("date")
        .groupby(["session_key", "driver_number"], as_index=False)
        .first()
    )


def derive_session_results(positions: pd.DataFrame) -> pd.DataFrame:
    positions["date"] = pd.to_datetime(positions["date"], format='ISO8601')
    return (
        positions
        .sort_values("date")
        .groupby(["session_key", "driver_number"], as_index=False)
        .last()
    )


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    state = load_state()
    already_done = set(state["processed_session_keys"])

    # ── 1. Meetings ──────────────────────────────────────────────────────────
    print("Lade Meetings...")
    meetings = fetch_by_year("meetings")
    save(meetings, f"f1_meetings_{YEAR}")

    # ── 2. Sessions ──────────────────────────────────────────────────────────
    print("\nLade Sessions...")
    sessions = fetch_by_year("sessions")
    save(sessions, f"f1_sessions_{YEAR}")

    if sessions.empty:
        print("Keine Sessions gefunden — Abbruch.")
        return

    sessions["date_end"] = pd.to_datetime(sessions["date_end"], utc=True)
    past_sessions = sessions[sessions["date_end"] < pd.Timestamp.now(tz="UTC")]
    all_keys = set(past_sessions["session_key"].dropna().astype(int).tolist())

    new_keys = sorted(all_keys - already_done)
    if not new_keys:
        print(f"\nKeine neuen Sessions seit letztem Lauf ({len(already_done)} bereits geladen).")
        return

    print(f"\n{len(new_keys)} neue Sessions gefunden (von {len(all_keys)} gesamt).")

    # ── 3. Drivers ───────────────────────────────────────────────────────────
    print("\nLade Drivers (neu)...")
    new_drivers = fetch_by_session("drivers", new_keys)
    append_or_create(new_drivers, f"f1_drivers_{YEAR}")

    # ── 4. Weather ───────────────────────────────────────────────────────────
    print("\nLade Weather (neu)...")
    new_weather = fetch_by_session("weather", new_keys)
    append_or_create(new_weather, f"f1_weather_{YEAR}")

    # ── 5. Laps ──────────────────────────────────────────────────────────────
    print("\nLade Laps (neu)...")
    new_laps = fetch_by_session("laps", new_keys)
    append_or_create(new_laps, f"f1_laps_{YEAR}")

    # ── 6. Positions → Starting Grid + Session Results ───────────────────────
    print("\nLade Position-Daten (neu)...")
    new_positions = fetch_by_session("position", new_keys)
    all_positions = append_or_create(new_positions, f"f1_positions_{YEAR}")

    if not all_positions.empty:
        print("Leite Starting Grid ab...")
        save(derive_starting_grid(all_positions), f"f1_starting_grid_{YEAR}")

        print("Leite Session Results ab...")
        save(derive_session_results(all_positions), f"f1_session_results_{YEAR}")
    else:
        print("[SKIP] Starting Grid & Session Results — keine Positionsdaten")

    # ── State aktualisieren ──────────────────────────────────────────────────
    state["processed_session_keys"] = sorted(already_done | all_keys)
    save_state(state)
    print(f"\nState gespeichert: {len(state['processed_session_keys'])} Sessions insgesamt verarbeitet.")
    print("Fertig. Alle Dateien liegen in:", OUTPUT_DIR.resolve())


if __name__ == "__main__":
    main()
