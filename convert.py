import os
import glob
import gpxpy
import matplotlib.pyplot as plt

def gpx_to_png_clean(gpx_file_path, png_output_path):
    with open(gpx_file_path, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    lats, lons = [], []

    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                lats.append(point.latitude)
                lons.append(point.longitude)

    if not lats or not lons:
        print(f"GPX is empty: {gpx_file_path}")
        return

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(lons, lats, color='#bebebe', linewidth=2)
    ax.axis('off')
    ax.set_aspect('equal', adjustable='box')
    fig.patch.set_alpha(0.0)
    ax.set_facecolor('none')

    plt.savefig(png_output_path, dpi=300, bbox_inches='tight', pad_inches=0, transparent=True)
    plt.close()
    print(f"Saved: {png_output_path}")


def main():
    for gpx_file in glob.glob("*.gpx"):
        png_file = os.path.splitext(gpx_file)[0] + ".png"
        gpx_to_png_clean(gpx_file, png_file)


if __name__ == "__main__":
    main()
