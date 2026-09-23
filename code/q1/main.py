"""Plot DEM terrain profiles from O01 to every service area S001–S015.

Run from the repository root with ``python code/q1/main.py``. Source files are
read only. Pass ``--data-root`` to use a different copy of the D-question data.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LightSource, LinearSegmentedColormap
from openpyxl import load_workbook
from scipy.interpolate import RegularGridInterpolator
from scipy.io import loadmat

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common.paths import FIGURES, RESULTS, ROOT, TABLES  # noqa: E402
from common.plot_style import set_style  # noqa: E402

EARTH_RADIUS_M = 6_371_008.8
WORKBOOK_REL = Path("数据/无人机应急物资运输基础数据/调度中心与服务区.xlsx")
DEM_REL = Path("数据/镇龙乡地理空间数据/镇龙乡及周边地理数据/数字高程模型数据（DEM）/镇龙乡及周边30米DEM.mat")


def data_root(override: Path | None) -> Path:
    if override:
        return override
    env = os.environ.get("Q1_DATA_ROOT")
    candidates = [
        Path(env) if env else None,
        ROOT / "data/raw/D题",
        Path.home() / "Desktop/第二十三届中国研究生数学建模竞赛 - 中文题目/中文题目/D题",
    ]
    for candidate in candidates:
        if candidate and (candidate / WORKBOOK_REL).is_file() and (candidate / DEM_REL).is_file():
            return candidate
    raise FileNotFoundError("找不到 D题原始数据；请用 --data-root 指向含有“数据”目录的 D题文件夹。")


def read_nodes(path: Path) -> dict[str, dict]:
    workbook = load_workbook(path, read_only=True, data_only=True)
    try:
        nodes = {}
        for row in workbook.active.values:
            key = row[0]
            if isinstance(key, str) and (key == "O01" or key.startswith("S")):
                nodes[key] = {"id": key, "name": row[1], "lon": float(row[2]),
                              "lat": float(row[3]), "nominal_elevation_m": float(row[4])}
    finally:
        workbook.close()
    expected = {"O01"} | {f"S{i:03d}" for i in range(1, 16)}
    if set(nodes) != expected:
        raise ValueError(f"点位编号与题目不符：缺少 {sorted(expected - set(nodes))}，多出 {sorted(set(nodes) - expected)}")
    return nodes


def read_dem(path: Path):
    raw = loadmat(path)
    if int(raw["epsg_code"].item()) != 4326:
        raise ValueError("DEM 坐标系不是 EPSG:4326")
    lon = raw["longitude"].ravel()
    lat = raw["latitude"].ravel()
    dem = raw["dem"].astype(float)
    dem[dem == float(raw["nodata"].item())] = np.nan
    if dem.shape != (len(lat), len(lon)):
        raise ValueError("DEM 网格与经纬度轴尺寸不一致")
    if np.diff(lat).mean() < 0:
        lat, dem = lat[::-1], dem[::-1, :]
    if np.diff(lon).mean() < 0:
        lon, dem = lon[::-1], dem[:, ::-1]
    return lon, lat, dem, RegularGridInterpolator((lat, lon), dem, method="linear", bounds_error=True)


def haversine_m(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(np.radians, (lon1, lat1, lon2, lat2))
    delta_lon, delta_lat = lon2 - lon1, lat2 - lat1
    a = np.sin(delta_lat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(delta_lon / 2) ** 2
    return 2 * EARTH_RADIUS_M * np.arcsin(np.sqrt(a))


def profile(origin: dict, target: dict, interpolator):
    horizontal_m = float(haversine_m(origin["lon"], origin["lat"], target["lon"], target["lat"]))
    count = math.ceil(horizontal_m / 30) + 1
    fraction = np.linspace(0, 1, count)
    lons = origin["lon"] + fraction * (target["lon"] - origin["lon"])
    lats = origin["lat"] + fraction * (target["lat"] - origin["lat"])
    elevations = interpolator(np.column_stack((lats, lons)))
    if not np.all(np.isfinite(elevations)):
        raise ValueError(f"{target['id']} 航段含 DEM NoData 采样点")
    segment_m = haversine_m(lons[:-1], lats[:-1], lons[1:], lats[1:])
    distance_m = np.r_[0, np.cumsum(segment_m)]
    delta_z = np.diff(elevations)
    peak = int(np.argmax(elevations))
    summary = {
        "origin": "O01", "destination": target["id"],
        "horizontal_distance_m": round(float(distance_m[-1]), 3),
        "terrain_polyline_length_m": round(float(np.hypot(segment_m, delta_z).sum()), 3),
        "sample_count": count,
        "mean_sample_spacing_m": round(float(np.mean(segment_m)), 3),
        "origin_dem_elevation_m": round(float(elevations[0]), 3),
        "destination_dem_elevation_m": round(float(elevations[-1]), 3),
        "net_elevation_change_m": round(float(elevations[-1] - elevations[0]), 3),
        "minimum_elevation_m": round(float(np.min(elevations)), 3),
        "maximum_elevation_m": round(float(elevations[peak]), 3),
        "peak_distance_from_origin_m": round(float(distance_m[peak]), 3),
        "cumulative_ascent_m": round(float(np.maximum(delta_z, 0).sum()), 3),
        "cumulative_descent_m": round(float(-np.minimum(delta_z, 0).sum()), 3),
    }
    return lons, lats, distance_m, elevations, summary


def draw_profile(ax, distance_m, elevation_m, destination, *, detailed=False):
    x = distance_m / 1000
    ax.plot(x, elevation_m, color="#126b7a", linewidth=1.8)
    bottom = max(0, float(elevation_m.min()) - 35)
    ax.fill_between(x, bottom, elevation_m, color="#84b9b4", alpha=0.38)
    ax.set_ylim(bottom, max(elevation_m.max() + 25, bottom + 60))
    ax.set_xlim(0, x[-1])
    ax.set_title(f"O01 → {destination}", loc="left", fontweight="bold")
    ax.set_xlabel("沿线水平距离 (km)")
    ax.set_ylabel("DEM 高程 (m)")
    if detailed:
        peak = int(np.argmax(elevation_m))
        ax.scatter([0, x[peak], x[-1]], [elevation_m[0], elevation_m[peak], elevation_m[-1]],
                   c=["#bb3940", "#d28b22", "#126b7a"], s=[42, 35, 42], zorder=4)
        ax.annotate(f"最高点 {elevation_m[peak]:.1f} m", (x[peak], elevation_m[peak]),
                    xytext=(6, 8), textcoords="offset points", fontsize=9)
        ax.text(0.015, 0.04, f"起点 {elevation_m[0]:.1f} m", transform=ax.transAxes, fontsize=9)
        ax.text(0.985, 0.04, f"终点 {elevation_m[-1]:.1f} m", transform=ax.transAxes,
                ha="right", fontsize=9)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, help="赛题 D题 文件夹路径")
    args = parser.parse_args()
    source = data_root(args.data_root)
    nodes = read_nodes(source / WORKBOOK_REL)
    lon_axis, lat_axis, dem, interp = read_dem(source / DEM_REL)
    set_style()
    plt.rcParams.update({"svg.fonttype": "none", "pdf.fonttype": 42})

    profiles = {}
    summaries = []
    rows = []
    for i in range(1, 16):
        destination = f"S{i:03d}"
        lons, lats, distances, elevations, summary = profile(nodes["O01"], nodes[destination], interp)
        profiles[destination] = (lons, lats, distances, elevations)
        summaries.append(summary)
        rows.extend((destination, j, float(distances[j]), float(lons[j]), float(lats[j]), float(elevations[j]))
                    for j in range(len(distances)))
        fig, ax = plt.subplots(figsize=(8.2, 3.8), layout="constrained")
        draw_profile(ax, distances, elevations, destination, detailed=True)
        fig.savefig(FIGURES / f"q1_profile_O01-{destination}.png", dpi=300)
        plt.close(fig)

    fig, axes = plt.subplots(5, 3, figsize=(13, 15), layout="constrained")
    for ax, (destination, (_, _, distances, elevations)) in zip(axes.flat, profiles.items()):
        draw_profile(ax, distances, elevations, destination)
    fig.suptitle("O01 至 15 个服务区的 DEM 直线地形剖面", fontsize=16, fontweight="bold")
    fig.savefig(FIGURES / "q1_profiles_O01-S001-S015.png", dpi=300)
    plt.close(fig)

    # Spatial context: the map shows every endpoint and the 15 sampled ground projections.
    fig, ax = plt.subplots(figsize=(9, 8), layout="constrained")
    muted_relief = LinearSegmentedColormap.from_list(
        "muted_relief", ["#dce8df", "#9dbfa8", "#799b83", "#a79776", "#ddd5be"]
    )
    terrain = LightSource(azdeg=315, altdeg=45).shade(
        dem, cmap=muted_relief, vert_exag=0.8, blend_mode="overlay"
    )
    ax.imshow(terrain, extent=[lon_axis[0], lon_axis[-1], lat_axis[0], lat_axis[-1]], origin="lower")
    for destination, (lons, lats, _, _) in profiles.items():
        ax.plot(lons, lats, color="#f9e37c", linewidth=0.9, alpha=0.8)
        ax.plot(lons[-1], lats[-1], "o", color="#00ced1", markeredgecolor="#12434a", markersize=6)
        ax.annotate(destination, (lons[-1], lats[-1]), xytext=(4, 3), textcoords="offset points",
                    fontsize=8, color="#102c34", fontweight="bold")
    ax.plot(nodes["O01"]["lon"], nodes["O01"]["lat"], marker="*", color="#cf373b",
            markeredgecolor="white", markersize=16)
    ax.annotate("O01", (nodes["O01"]["lon"], nodes["O01"]["lat"]),
                xytext=(7, -12), textcoords="offset points", color="#a51c30", fontweight="bold")
    ax.set_xlim(min(n["lon"] for n in nodes.values()) - 0.025, max(n["lon"] for n in nodes.values()) + 0.025)
    ax.set_ylim(min(n["lat"] for n in nodes.values()) - 0.025, max(n["lat"] for n in nodes.values()) + 0.025)
    ax.set_aspect(1 / np.cos(np.radians(nodes["O01"]["lat"])))
    ax.set_xlabel("经度 (°E)")
    ax.set_ylabel("纬度 (°N)")
    ax.set_title("O01、服务区及直线剖面位置")
    fig.savefig(FIGURES / "q1_dem_O01_S001-S015.png", dpi=300)
    plt.close(fig)

    with (TABLES / "q1_profiles_O01-S001-S015.csv").open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["destination", "sample_index", "distance_m", "longitude_deg", "latitude_deg", "dem_elevation_m"])
        writer.writerows(rows)
    with (RESULTS / "q1_profiles_O01-S001-S015_summary.json").open("w", encoding="utf-8") as file:
        json.dump({"source_crs": "EPSG:4326", "target_spacing_m": 30,
                   "interpolation": "bilinear", "profiles": summaries}, file, ensure_ascii=False, indent=2)
    for item in summaries:
        print(f"{item['destination']}: {item['horizontal_distance_m']/1000:.3f} km, "
              f"峰值 {item['maximum_elevation_m']:.1f} m, {item['sample_count']} 点")
    print(f"输出目录：{FIGURES}")


if __name__ == "__main__":
    main()
