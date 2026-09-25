import os
import sys
import glob
import gpxpy
import matplotlib.pyplot as plt


# Ausgabegröße und Rand in cm
WIDTH_CM  = 13.0
HEIGHT_CM =  5.9
PAD_CM    =  0.7  # 7 mm auf jeder Seite


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


def render(lats: list[float], lons: list[float], output_path: str, portrait: bool = False) -> None:
    w_cm, h_cm = (HEIGHT_CM, WIDTH_CM) if portrait else (WIDTH_CM, HEIGHT_CM)
    fig, ax = plt.subplots(figsize=(w_cm / 2.54, h_cm / 2.54))
    ax.plot(lons, lats, color="#DF0037", linewidth=4)
    ax.axis("off")

    # Gleichmäßiger Innenrand – Axes-Bereich wird um PAD_CM auf jeder Seite eingerückt.
    # bbox_inches="tight" wird bewusst NICHT verwendet, damit die Ausgabegröße
    # exakt w_cm × h_cm bleibt.
    fig.subplots_adjust(
        left   = PAD_CM / w_cm,
        right  = 1 - PAD_CM / w_cm,
        bottom = PAD_CM / h_cm,
        top    = 1 - PAD_CM / h_cm,
    )

    fig.patch.set_alpha(0.0)
    ax.set_facecolor("none")
    plt.savefig(output_path, dpi=300, transparent=True)
    plt.close()
    ausrichtung = "hochkant" if portrait else "quer"
    print(f"Gespeichert ({ausrichtung}, {w_cm:.1f}×{h_cm:.1f} cm, Rand {PAD_CM*10:.0f} mm): {output_path}")


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


def parse_args(argv: list[str]) -> tuple[list[str], str, bool]:
    """
    Gibt zurück: (gpx_pfade, ausgabepfad, portrait)

    Flags:
      -o <datei>          Ausgabedatei (Standard: combined_track.png)
      -p / --portrait     Hochkant statt Quer
    """
    args = argv[:]
    portrait = False
    output_path = "combined_track.png"

    for flag in ("-p", "--portrait"):
        if flag in args:
            portrait = True
            args.remove(flag)

    if "-o" in args:
        idx = args.index("-o")
        output_path = args[idx + 1]
        args = args[:idx] + args[idx + 2:]

    return args, output_path, portrait


def main() -> None:
    # Aufruf: python gpx_to_png.py tour1.gpx tour2.gpx [-o ausgabe.png] [-p]
    # Oder:   python gpx_to_png.py *.gpx --portrait
    # Ohne Argumente: alle *.gpx im aktuellen Verzeichnis

    gpx_args, output_path, portrait = parse_args(sys.argv[1:])

    if not gpx_args:
        gpx_args = ["*.gpx"]
        print("Keine Dateien angegeben – suche nach *.gpx im aktuellen Verzeichnis …")

    gpx_files = resolve_paths(gpx_args)

    if not gpx_files:
        print("Keine GPX-Dateien gefunden.")
        sys.exit(1)

    print(f"\n{len(gpx_files)} GPX-Datei(en) werden verarbeitet:")
    lats, lons = load_gpx_files(gpx_files)

    if not lats:
        print("Keine Koordinaten gefunden.")
        sys.exit(1)

    print(f"\nGesamt: {len(lats)} Punkte → wird gerendert …")
    render(lats, lons, output_path, portrait=portrait)


if __name__ == "__main__":
    main()