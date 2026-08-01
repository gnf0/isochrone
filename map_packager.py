from pathlib import Path

# --- configure these ---
FOLDER = Path("html/")  # folder where your map pages live (e.g. html/map_*.html)
OUTPUT_INDEX_NAME = "index.html"  # generated index.html location (we'll write it into repo root by default)
GLOB_PATTERN = "*.html"
# -----------------------

html_files = sorted(
    [p for p in FOLDER.glob(GLOB_PATTERN) if p.is_file() and p.name != OUTPUT_INDEX_NAME]
)

def label_from_file(fname: str) -> str:
    return fname.replace(".html", "").replace("_", " ")

# Paths relative to the site root, e.g. "html/map_one.html"
map_urls = [f"{FOLDER.as_posix().rstrip('/')}/{p.name}" for p in html_files]

# A parallel list of labels for the dropdown
map_labels = [label_from_file(p.name) for p in html_files]

index_html = f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Map Gallery</title>
    <style>
      body{{
        margin:0;
        font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
        height:100vh;
        display:flex;
        flex-direction:column;
        background:#f6f7fb;
      }}
      .bar{{
        padding:10px 14px;
        display:flex;
        align-items:center;
        gap:10px;
        background:#f6f7fb;
        border-bottom:1px solid #e6e8ef;
      }}
      .title{{
        font-weight:650;
        color:#111827;
        white-space:nowrap;
        margin-right:6px;
      }}
      .controls{{
        display:flex;
        align-items:center;
        gap:10px;
        width:100%;
      }}
      select{{
        flex:1;
        height:40px;
        padding:0 12px;
        border:1px solid #d7dbe6;
        border-radius:10px;
        background:white;
        font-size:14px;
        outline:none;
      }}
      iframe{{
        width:100%;
        flex:1;
        min-height:0;
        border:0;
        display:block;
        background:white;
      }}
    </style>
  </head>

  <body>
    <div class="bar">
      <div class="title">Map Gallery</div>
      <div class="controls">
        <select id="mapSelect" aria-label="Select map"></select>
      </div>
    </div>

    <iframe id="frame" src="" title="Selected map"></iframe>

    <script>
      const MAP_URLS = {map_urls!r};
      const MAP_LABELS = {map_labels!r};

      const selectEl = document.getElementById("mapSelect");
      const frameEl = document.getElementById("frame");

      function escapeHtml(s) {{
        return String(s)
          .replaceAll("&", "&amp;")
          .replaceAll("<", "&lt;")
          .replaceAll(">", "&gt;")
          .replaceAll('"', "&quot;")
          .replaceAll("'", "&#039;");
      }}

      function init() {{
        // Build dropdown options
        for (let i = 0; i < MAP_URLS.length; i++) {{
          const url = MAP_URLS[i];
          const label = MAP_LABELS[i] ?? url;

          const opt = document.createElement("option");
          opt.value = url;
          opt.textContent = label;
          selectEl.appendChild(opt);
        }}

        if (MAP_URLS.length) {{
          frameEl.src = MAP_URLS[0];
          selectEl.value = MAP_URLS[0];
        }}

        selectEl.addEventListener("change", () => {{
          frameEl.src = selectEl.value;
        }});
      }}

      init();
    </script>
  </body>
</html>
"""

out_path = Path(OUTPUT_INDEX_NAME)
out_path.write_text(index_html, encoding="utf-8")

print(f"Wrote {out_path.resolve()}")
print(f"Included {len(html_files)} map files.")
