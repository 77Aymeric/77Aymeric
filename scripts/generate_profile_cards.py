#!/usr/bin/env python3

from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path


USER = "77Aymeric"
ACCENT = "#60A5FA"
GHCHART_COLOR = "3b82f6"
ASSETS_DIR = Path("assets")

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

THEMES = {
    "dark": {
        "bg": "#020617",
        "border": "#1E293B",
        "title": "#60A5FA",
        "text": "#F8FAFC",
        "muted": "#94A3B8",
        "subtle": "#64748B",
        "empty": "#0F172A",
        "label": "#94A3B8",
    },
    "light": {
        "bg": "#F8FAFC",
        "border": "#CBD5E1",
        "title": "#2563EB",
        "text": "#0F172A",
        "muted": "#334155",
        "subtle": "#64748B",
        "empty": "#E2E8F0",
        "label": "#475569",
    },
}


def fetch_text(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "text/html,application/json,application/xml;q=0.9,*/*;q=0.8",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def format_date(date_str: str) -> str:
    year, month, day = map(int, date_str.split("-"))
    return f"{MONTHS[month - 1]} {day}, {year}"


def load_stats() -> dict[str, object]:
    return json.loads(fetch_text(f"https://streak-stats.demolab.com/?user={USER}&type=json"))


def load_heatmap_markup(theme: dict[str, str]) -> str:
    raw = fetch_text(f"https://ghchart.rshah.org/{GHCHART_COLOR}/{USER}")
    match = re.search(r"<svg[^>]*>(.*)</svg>", raw, flags=re.S)
    if not match:
        raise RuntimeError("Unable to parse heatmap SVG")

    inner = match.group(1)
    inner = inner.replace("#EEEEEE", theme["empty"])
    inner = inner.replace("#767676", theme["label"])
    return inner


def build_stats_card(theme_name: str, data: dict[str, object]) -> str:
    theme = THEMES[theme_name]
    current = data["currentStreak"]
    longest = data["longestStreak"]
    total = data["totalContributions"]
    first = format_date(data["firstContribution"])
    current_range = f"{format_date(current['start'])} - {format_date(current['end'])}"
    longest_range = f"{format_date(longest['start'])} - {format_date(longest['end'])}"

    return f"""<svg width="360" height="236" viewBox="0 0 360 236" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="title desc">
  <title id="title">Aymeric GitHub stats</title>
  <desc id="desc">Total contributions {total} since {first}. Current streak {current['length']} days from {current_range}. Longest streak {longest['length']} days from {longest_range}.</desc>
  <rect x="1" y="1" width="358" height="234" rx="22" fill="{theme['bg']}" stroke="{theme['border']}" stroke-width="2"/>
  <rect x="28" y="26" width="92" height="5" rx="2.5" fill="{ACCENT}"/>
  <text x="28" y="58" fill="{theme['title']}" font-family="Segoe UI, Ubuntu, Arial, sans-serif" font-size="22" font-weight="700">GitHub Stats</text>

  <text x="28" y="96" fill="{theme['muted']}" font-family="Segoe UI, Ubuntu, Arial, sans-serif" font-size="14" font-weight="600">Total Contributions</text>
  <text x="332" y="96" fill="{theme['text']}" font-family="Segoe UI, Ubuntu, Arial, sans-serif" font-size="22" font-weight="700" text-anchor="end">{total}</text>
  <text x="28" y="116" fill="{theme['subtle']}" font-family="Segoe UI, Ubuntu, Arial, sans-serif" font-size="12">Since {first}</text>
  <line x1="28" y1="130" x2="332" y2="130" stroke="{theme['border']}" stroke-width="1"/>

  <text x="28" y="154" fill="{theme['muted']}" font-family="Segoe UI, Ubuntu, Arial, sans-serif" font-size="14" font-weight="600">Current Streak</text>
  <text x="332" y="154" fill="{theme['text']}" font-family="Segoe UI, Ubuntu, Arial, sans-serif" font-size="22" font-weight="700" text-anchor="end">{current['length']} days</text>
  <text x="28" y="174" fill="{theme['subtle']}" font-family="Segoe UI, Ubuntu, Arial, sans-serif" font-size="12">{current_range}</text>
  <line x1="28" y1="186" x2="332" y2="186" stroke="{theme['border']}" stroke-width="1"/>

  <text x="28" y="210" fill="{theme['muted']}" font-family="Segoe UI, Ubuntu, Arial, sans-serif" font-size="14" font-weight="600">Longest Streak</text>
  <text x="332" y="210" fill="{theme['text']}" font-family="Segoe UI, Ubuntu, Arial, sans-serif" font-size="22" font-weight="700" text-anchor="end">{longest['length']} days</text>
  <text x="28" y="228" fill="{theme['subtle']}" font-family="Segoe UI, Ubuntu, Arial, sans-serif" font-size="12">{longest_range}</text>
</svg>
"""


def build_heatmap_card(theme_name: str, heatmap_markup: str) -> str:
    theme = THEMES[theme_name]
    return f"""<svg width="560" height="236" viewBox="0 0 560 236" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="title desc">
  <title id="title">Aymeric contribution calendar</title>
  <desc id="desc">GitHub contribution calendar covering the last 52 weeks.</desc>
  <rect x="1" y="1" width="558" height="234" rx="22" fill="{theme['bg']}" stroke="{theme['border']}" stroke-width="2"/>
  <rect x="28" y="26" width="126" height="5" rx="2.5" fill="{ACCENT}"/>
  <text x="28" y="58" fill="{theme['title']}" font-family="Segoe UI, Ubuntu, Arial, sans-serif" font-size="22" font-weight="700">Contribution Calendar</text>
  <text x="28" y="80" fill="{theme['subtle']}" font-family="Segoe UI, Ubuntu, Arial, sans-serif" font-size="12">Last 52 weeks</text>
  <g transform="translate(18 98) scale(0.78)">
    {heatmap_markup}
  </g>
</svg>
"""


def main() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    stats = load_stats()

    for theme_name in THEMES:
        heatmap_markup = load_heatmap_markup(THEMES[theme_name])
        (ASSETS_DIR / f"profile-stats-{theme_name}.svg").write_text(
            build_stats_card(theme_name, stats),
            encoding="utf-8",
        )
        (ASSETS_DIR / f"contribution-heatmap-{theme_name}.svg").write_text(
            build_heatmap_card(theme_name, heatmap_markup),
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
