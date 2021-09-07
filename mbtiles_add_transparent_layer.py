#!/usr/bin/env python3

"""This script adds a transparent layer to a mbtiles map file.

Locus 3 requires the transparent layer for map overlays,
otherwise the largest zoom level is magnified too much.

Install prerequisites: pip install Pillow

Usage: python mbtiles_add_transparent_layer.py YOUR_FILE.mbtiles
"""

__author__ = "Fabian Otto"
__copyright__ = "Copyright (c) 2021 Fabian Otto"
__license__ = "MIT"
__version__ = "1.0"

import io
import os
import sqlite3
import sys

import PIL.Image

# Check arguments
if len(sys.argv) <= 1:
    print("Usage: python mbtiles_add_transparent_layer.py YOUR_FILE.mbtiles")
    exit(0)

# Check if file exists
filename = sys.argv[1]
if not os.path.exists(filename):
    print("Error: File not found:", filename)
    exit(1)

# Create transparent PNG file in memory
pngbuffer = io.BytesIO()
img = PIL.Image.new("RGBA", (256, 256), (255, 255, 255, 0))
img.save(pngbuffer, "PNG", optimize=True)
pngblob = pngbuffer.getvalue()

# Open database
con = sqlite3.connect(filename)
cur = con.cursor()

# Detect maximum zoom level
cur.execute("SELECT MAX(zoom_level) FROM tiles")
max_zoom_level = cur.fetchone()[0]
print("Maximum zoom level", max_zoom_level)

# Insert transparent tiles
print("Inserting transparent tiles")
cur.execute("SELECT tile_column, tile_row FROM tiles WHERE zoom_level = ?", (max_zoom_level,))
rows = cur.fetchall()
query = "INSERT INTO tiles (zoom_level, tile_column, tile_row, tile_data) VALUES (?, ?, ?, ?)"
zl = max_zoom_level + 1
for row in rows:
    tcol = row[0]
    trow = row[1]
    cur.execute(query, (zl, tcol * 2 + 0, trow * 2 + 0, pngblob))
    cur.execute(query, (zl, tcol * 2 + 0, trow * 2 + 1, pngblob))
    cur.execute(query, (zl, tcol * 2 + 1, trow * 2 + 0, pngblob))
    cur.execute(query, (zl, tcol * 2 + 1, trow * 2 + 1, pngblob))

# Store database
con.commit()
cur.close()
print("Done")
