import time
import requests
import pandas as pd
from pathlib import Path

BASE_URL = "https://api.openf1.org/v1"
YEAR = 2026
OUTPUT_DIR = Path("data/raw")
DELAY = 1.0
MAX_RETRIES = 3


def fetch_by_year(endpoint: str) -> pd.DataFrame:
    """Endpunkte, die year direkt unterstützen (drivers, meetings, sessions)."""
    r = requests.get(f"{BASE_URL}/{endpoint}", params={"year": YEAR})
    r.raise_for_status()
    data = r.json()
    return pd.DataFrame(data) if data else pd.DataFrame()


def fetch_by_session(endpoint: str, session_keys: list[int]) -> pd.DataFrame:
    """Endpunkte, die nur session_key als Filter kennen — iteriert über alle Sessions."""
    frames = []
    total = len(session_keys)
    for i, key in enumerate(session_keys, 1):
        print(f"  [{i}/{total}] session_key={key}", end="", flush=True)
        for attempt in range(1, MAX_RETRIES + 1):
            r = requests.get(f"{BASE_URL}/{endpoint}", params={"session_key": key})
            if r.status_code == 429:
                wait = DELAY * 2 ** attempt
                print(f" — 429, warte {wait:.0f}s...", end="", flush=True)
                time.sleep(wait)
                continue
            if r.status_code == 404:
                print(" — 404 (keine Daten), übersprungen")
                break
            r.raise_for_status()
            break
        else:
            print(" — max. Retries erreicht, übersprungen")
            continue
        if r.status_code == 404:
            time.sleep(DELAY)
            continue
        data = r.json()
        if data:
            frames.append(pd.DataFrame(data))
        print(f" — {len(data)} Zeilen")
        time.sleep(DELAY)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def save(df: pd.DataFrame, name: str) -> None:
    if df.empty:
        print(f"[SKIP] {name} — keine Daten")
        return
    path = OUTPUT_DIR / f"{name}.parquet"
    df.to_parquet(path, index=False)
    print(f"[OK]   {name}: {df.shape[0]} Zeilen, {df.shape[1]} Spalten")


def derive_starting_grid(positions: pd.DataFrame) -> pd.DataFrame:
    positions["date"] = pd.to_datetime(positions["date"])
    return (
        positions
        .sort_values("date")
        .groupby(["session_key", "driver_number"], as_index=False)
        .first()
    )


def derive_session_results(positions: pd.DataFrame) -> pd.DataFrame:
    positions["date"] = pd.to_datetime(positions["date"])
    return (
        positions
        .sort_values("date")
        .groupby(["session_key", "driver_number"], as_index=False)
        .last()
    )


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # ── 1. Drivers ───────────────────────────────────────────────────────────
    print("Lade Drivers...")
    drivers = fetch_by_year("drivers")
    save(drivers, f"f1_drivers_{YEAR}")

    # ── 2. Meetings ──────────────────────────────────────────────────────────
    print("\nLade Meetings...")
    meetings = fetch_by_year("meetings")
    save(meetings, f"f1_meetings_{YEAR}")

    # ── 3. Sessions ──────────────────────────────────────────────────────────
    print("\nLade Sessions...")
    sessions = fetch_by_year("sessions")
    save(sessions, f"f1_sessions_{YEAR}")

    if sessions.empty:
        print("Keine Sessions gefunden — Abbruch.")
        return

    sessions["date_end"] = pd.to_datetime(sessions["date_end"], utc=True)
    past_sessions = sessions[sessions["date_end"] < pd.Timestamp.now(tz="UTC")]
    session_keys = past_sessions["session_key"].dropna().astype(int).tolist()
    print(f"{len(session_keys)} abgeschlossene Sessions aus {YEAR} gefunden.\n")

    # ── 4. Weather ───────────────────────────────────────────────────────────
    print("Lade Weather...")
    weather = fetch_by_session("weather", session_keys)
    save(weather, f"f1_weather_{YEAR}")

    # ── 5. Laps ──────────────────────────────────────────────────────────────
    print("\nLade Laps...")
    laps = fetch_by_session("laps", session_keys)
    save(laps, f"f1_laps_{YEAR}")

    # ── 6 & 7. Position → Starting Grid + Session Results ───────────────────
    print("\nLade Position-Daten...")
    positions = fetch_by_session("position", session_keys)

    if not positions.empty:
        print("Leite Starting Grid ab...")
        save(derive_starting_grid(positions), f"f1_starting_grid_{YEAR}")

        print("Leite Session Results ab...")
        save(derive_session_results(positions), f"f1_session_results_{YEAR}")
    else:
        print("[SKIP] Starting Grid & Session Results — keine Positionsdaten")

    print("\nFertig. Alle Dateien liegen in:", OUTPUT_DIR.resolve())


if __name__ == "__main__":
    main()
