"""Shared helpers for the pixel-art library tools."""
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CATEGORIES = (
    'weapon armor tool food drink potion plant gem material block creature accessory '
    'clothing container furniture magic tech ui decoration misc'
).split()


def new_images():
    """PNG files at the repo root: a freshly added, not yet named batch (sorted by name)."""
    return sorted(f for f in os.listdir(REPO) if f.lower().endswith('.png') and os.path.isfile(os.path.join(REPO, f)))


def library_images():
    """Already named PNGs inside the category folders, as 'category/name.png' paths."""
    out = []
    for c in CATEGORIES:
        d = os.path.join(REPO, c)
        if os.path.isdir(d):
            out += [f'{c}/{f}' for f in sorted(os.listdir(d)) if f.lower().endswith('.png')]
    return out
