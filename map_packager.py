from pathlib import Path

# --- configure these ---
FOLDER = Path("html/")  # folder where your map pages live (e.g. html/map_*.html)
OUTPUT_INDEX_NAME = "index.html"  # generated index.html location (we'll write it into repo root by default)
GLOB_PATTERN = "*.html"
# -----------------------

# Collect map files (exclude the generated index.html if it happens to be inside FOLDER)
html_files = sorted(
    [p for p in FOLDER.glob(GLOB_PATTERN) if p.is_file() and p.name != OUTPUT_INDEX_NAME]
)

def label_from_file(fname: str) -> str:
    return fname.replace(".html", "").replace("_", " ")

# Build URLs so iframe loads correctly when index.html is at repo root
# Example result: ["html/map_one.html", "html/map_two.html"]
map_urls = [f"{FOLDER.as_posix().rstrip('/')}/{p.name}" for p in html_files]

# Use correct JS values (as an array of strings)
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
        padding:12px 14px;
        display:flex;
        align-items:center;
        gap:12px;
        background:#f6f7fb;
        border-bottom:1px solid #e6e8ef;
      }}
      .title{{
        font-weight:650;
        color:#111827;
        white-space:nowrap;
      }}
      .search{{
        flex:1;
        height:40px;
        padding:0 12px;
        border:1px solid #d7dbe6;
        border-radius:10px;
        background:white;
        font-size:14px;
        outline:none;
      }}
      #main{{
        flex:1;
        min-height:0;
        display:grid;
        grid-template-columns: 320px 1fr;
      }}
      .sidebar{{
        overflow:auto;
        padding:12px;
      }}
      .list{{
        display:grid;
        gap:10px;
      }}
      .card{{
        text-align:left;
        border:1px solid #e5e7eb;
        background:#fff;
        border-radius:12px;
        padding:12px;
        cursor:pointer;
      }}
      .card:hover{{
        border-color:#cfd6e6;
        box-shadow: 0 1px 10px rgba(17,24,39,0.06);
      }}
      .cardTitle{{
        font-weight:650;
        color:#111827;
        font-size:14px;
        margin-bottom:4px;
      }}
      .cardFile{{
        color:#6b7280;
        font-size:12px;
        word-break:break-word;
      }}
      .frameWrap{{
        min-width:0;
        flex:1;
      }}
      iframe{{
        width:100%;
        height:100%;
        border:0;
        display:block;
        background:white;
      }}
      @media (max-width: 900px){{
        #main{{ grid-template-columns: 1fr; }}
        .frameWrap{{ height: 60vh; }}
      }}
    </style>
  </head>

  <body>
    <div class="bar">
      <div class="title">Map Gallery</div>
      <input id="filter" class="search" type="search" placeholder="Filter maps..." />
    </div>

    <div id="main">
      <div class="sidebar">
        <div id="list" class="list"></div>
      </div>
      <div class="frameWrap">
        <iframe id="frame" src="" title="Selected map"></iframe>
      </div>
    </div>

    <script>
      // These are paths relative to the site root, e.g. "html/map_foo.html"
      const MAP_FILES = {map_urls!r};

      const listEl = document.getElementById("list");
      const filterEl = document.getElementById("filter");
      const frameEl = document.getElementById("frame");

      function labelFromFile(fname) {{
        return fname.replace(/\\.html$/, "").replace(/.*\\//, "").replace(/_/g, " ");
      }}

      function render(items) {{
        listEl.innerHTML = "";
        for (const f of items) {{
          const btn = document.createElement("button");
          btn.type = "button";
          btn.className = "card";

          const safeLabel = labelFromFile(f).replaceAll("<","&lt;").replaceAll(">","&gt;");
          const safeFile = String(f).replaceAll("<","&lt;").replaceAll(">","&gt;");

          btn.innerHTML = `
            <div class="cardTitle">${{safeLabel}}</div>
            <div class="cardFile">${{safeFile}}</div>
          `;

          btn.addEventListener("click", () => {{
            frameEl.src = f;
          }});
          listEl.appendChild(btn);
        }}
      }}

      const all = MAP_FILES.slice();

      render(all);
      if (all.length) frameEl.src = all[0];

      filterEl.addEventListener("input", () => {{
        const q = filterEl.value.trim().toLowerCase();
        const filtered = all.filter(f => String(f).toLowerCase().includes(q));
        render(filtered);
        if (filtered.length) frameEl.src = filtered[0];
      }});
    </script>
  </body>
</html>
"""

# Write index.html to repo root (so it becomes site root)
# If you want it inside html/, change this to FOLDER / OUTPUT_INDEX_NAME.
out_path = Path(OUTPUT_INDEX_NAME)
out_path.write_text(index_html, encoding="utf-8")

print(f"Wrote {out_path.resolve()}")
print(f"Included {len(html_files)} map files.")
