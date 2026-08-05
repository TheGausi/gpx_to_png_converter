import os
import sys
import glob
import gpxpy
import matplotlib.pyplot as plt


def load_gpx_files(paths: list[str]) -> tuple[list[float], list[float]]:
    """Lädt alle GPX-Dateien und gibt eine zusammengeführte Koordinatenliste zurück."""
    all_lats, all_lons = [], []

    for path in paths:
        if not os.path.isfile(path):
            print(f"Datei nicht gefunden, wird übersprungen: {path}")
            continue
        with open(path, "r") as f:
            gpx = gpxpy.parse(f)
        count_before = len(all_lats)
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    all_lats.append(point.latitude)
                    all_lons.append(point.longitude)
        added = len(all_lats) - count_before
        print(f"  {os.path.basename(path)}: {added} Punkte geladen")

    return all_lats, all_lons


def render(lats: list[float], lons: list[float], output_path: str) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(lons, lats, color="#DF0037", linewidth=6)
    ax.axis("off")
    ax.set_aspect("equal", adjustable="box")
    fig.patch.set_alpha(0.0)
    ax.set_facecolor("none")
    plt.savefig(output_path, dpi=300, bbox_inches="tight", pad_inches=0, transparent=True)
    plt.close()
    print(f"Gespeichert: {output_path}")


def resolve_paths(args: list[str]) -> list[str]:
    """Unterstützt explizite Dateipfade und Glob-Muster (z. B. *.gpx)."""
    resolved = []
    for arg in args:
        matched = glob.glob(arg)
        if matched:
            resolved.extend(sorted(matched))
        else:
            resolved.append(arg)  # wird in load_gpx_files als fehlend gemeldet
    return resolved


def main() -> None:
    # Aufruf: python gpx_to_png.py tour1.gpx tour2.gpx tour3.gpx [-o ausgabe.png]
    # Oder:   python gpx_to_png.py *.gpx
    # Ohne Argumente: alle *.gpx im aktuellen Verzeichnis

    args = sys.argv[1:]

    output_path = "combined_track.png"
    if "-o" in args:
        idx = args.index("-o")
        output_path = args[idx + 1]
        args = args[:idx] + args[idx + 2:]

    if not args:
        args = ["*.gpx"]
        print("Keine Dateien angegeben – suche nach *.gpx im aktuellen Verzeichnis …")

    gpx_files = resolve_paths(args)

    if not gpx_files:
        print("Keine GPX-Dateien gefunden.")
        sys.exit(1)

    print(f"\n{len(gpx_files)} GPX-Datei(en) werden verarbeitet:")
    lats, lons = load_gpx_files(gpx_files)

    if not lats:
        print("Keine Koordinaten gefunden.")
        sys.exit(1)

    print(f"\nGesamt: {len(lats)} Punkte → wird gerendert …")
    render(lats, lons, output_path)


if __name__ == "__main__":
    main()