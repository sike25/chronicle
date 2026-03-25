/* ============================================================
   CHRONICLE  —  Configuration
   This is the only section you need to edit.
   ============================================================ */

const CONFIG = {

  /* ── API ──────────────────────────────────────────────────
     Base URL of the deployed Chronicle backend.
     Trailing slash is fine either way.                       */
  apiUrl: "https://chronicle-435397225968.us-central1.run.app",

  /* ── Page chrome ── */
  siteLabel:   "Archivi.ng",
  toolName:    "Chronicle",
  description: "Search the archive. See history unfold across time.",

  /* ── Default query shown in the search box on load ── */
  defaultQuery: "Election crises and violence",
};


/* ============================================================
   ENGINE  —  Do not edit below this line
   ============================================================ */

/* ── Tiny helpers ── */

const esc = s => String(s ?? "")
  .replace(/&/g, "&amp;")
  .replace(/</g, "&lt;")
  .replace(/>/g, "&gt;")
  .replace(/"/g, "&quot;");

/**
 * Parse a Chronicle label like "2014-03-29 to 2015-01-01"
 * into human-readable parts.
 *
 * Returns { axisYear, range }
 *   axisYear — e.g. "2014" or "2014\n– 15"
 *   range    — e.g. "Mar 2014 – Jan 2015"
 */
function parseLabel(label) {
  const MONTHS = ["Jan","Feb","Mar","Apr","May","Jun",
                  "Jul","Aug","Sep","Oct","Nov","Dec"];

  const parts = label.split(" to ");
  const parseDate = str => {
    const [datePart] = str.trim().split(" ");
    const [y, m, d] = datePart.split("-").map(Number);
    return { y, m, d };
  };

  const start = parseDate(parts[0] || "");
  const end   = parseDate(parts[1] || parts[0] || "");

  const startMon = MONTHS[(start.m || 1) - 1] ?? "";
  const endMon   = MONTHS[(end.m   || 1) - 1] ?? "";

  const range = `${startMon} ${start.y} – ${endMon} ${end.y}`;

  let axisYear = String(start.y);
  if (end.y && end.y !== start.y) {
    const short = String(end.y).slice(-2);
    axisYear = `${start.y}\n– ${short}`;
  }

  return { axisYear, range };
}

/**
 * Map the `cluster_enriched` SSE payload from the API
 * into the internal cluster shape used by the renderer.
 */
function apiClusterToShape(data) {
  const { axisYear, range } = parseLabel(data.label ?? "");

  const sources = (data.entries ?? []).map((e, i) => ({
    pub:     e.publication    ?? "",
    date:    e.publication_date?.replace(/\//g, " ") ?? "",
    page:    `Pg ${e.page ?? "?"}`,
    title:   e.filename?.split("/").pop()?.replace(/\.tif$/, "") ?? e.filename ?? "",
    summary: e.summary        ?? "",
    tags:    [],   /* tags not in the API output contract — omit */
    archiveUrl: e.id ? `https://archivi.ng/search/${e.id}` : null,
  }));

  const firstPub = (data.entries?.[0]?.publication) ?? "Archive";

  return {
    id:       `c${data.index}`,
    year:     axisYear,
    range,
    title:    data.title   ?? `Period ${data.index + 1}`,
    summary:  data.summary ?? "",
    coverPub: firstPub,
    sources,
  };
}


/* ── HTML builders ── */

const thumbLinesHTML = () => `
  <div class="thumb-lines">
    <div class="thumb-line"></div>
    <div class="thumb-line" style="width:82%"></div>
    <div class="thumb-line" style="width:65%"></div>
    <div class="thumb-line" style="width:75%"></div>
  </div>`;

function cardHTML(cluster, index, isSkeleton = false) {
  const sid   = `sb-${esc(cluster.id)}`;
  const num   = String(index + 1).padStart(2, "0");
  const count = cluster.sources?.length ?? 0;
  const label = `${count} source${count !== 1 ? "s" : ""}`;

  if (isSkeleton) {
    return `
      <div class="card card-skeleton" data-index="${index}">
        <div class="card-content">
          <div class="skeleton-line" style="width:60%;height:9px;margin-bottom:8px"></div>
          <div class="skeleton-line" style="width:95%;height:13px;margin-bottom:5px"></div>
          <div class="skeleton-line" style="width:80%;height:13px;margin-bottom:5px"></div>
          <div class="skeleton-line" style="width:65%;height:13px;margin-bottom:10px"></div>
          <div class="skeleton-line" style="width:40%;height:9px;margin-top:auto"></div>
        </div>
      </div>`;
  }

  return `
    <div class="card" data-sidebar="${sid}" data-index="${index}"
         role="button" tabindex="0" aria-label="Open ${esc(cluster.title)}">
      <div class="card-content">
        <div class="card-range">${num} · ${esc(cluster.range)}</div>
        <h3 class="card-title">${esc(cluster.title)}</h3>
        <p  class="card-summary">${esc(cluster.summary)}</p>
        <div class="card-count">${label}</div>
      </div>
    </div>`;
}

function slotHTML(cluster, index, isSkeleton = false) {
  const above = index % 2 === 0;
  const year  = isSkeleton
    ? `<div class="skeleton-line" style="width:36px;height:10px"></div>`
    : esc(cluster.year).replace(/\n/g, "<br>");

  const inner = cardHTML(cluster, index, isSkeleton);

  if (above) return `
    <div class="slot" id="slot-${index}">
      <div class="upper">${inner}<div class="stem"></div></div>
      <div class="node"><div class="dot"></div><div class="year">${year}</div></div>
      <div class="lower void"></div>
    </div>`;

  return `
    <div class="slot" id="slot-${index}">
      <div class="upper void"></div>
      <div class="node"><div class="dot"></div><div class="year">${year}</div></div>
      <div class="lower"><div class="stem"></div>${inner}</div>
    </div>`;
}

function sidebarHTML(cluster, index) {
  const num   = String(index + 1).padStart(2, "0");
  const count = cluster.sources?.length ?? 0;

  /* Full cluster summary shown before sources */
  const summaryHTML = cluster.summary
    ? `<div class="sb-summary">${esc(cluster.summary)}</div>`
    : "";

  const sourcesHTML = (cluster.sources ?? []).map(src => {
    const tagsHTML = (src.tags ?? []).map(t => `<span class="tag">${esc(t)}</span>`).join("");
    const linkHTML = src.archiveUrl
      ? `<a class="source-link" href="${esc(src.archiveUrl)}" target="_blank" rel="noopener">
           View in archive ↗
         </a>`
      : "";
    return `
      <div class="source">
        <div class="source-meta">
          <span class="source-pub">${esc(src.pub)}</span><span class="source-dot">·</span>
          <span class="source-date">${esc(src.date)}</span><span class="source-dot">·</span>
          <span class="source-page">${esc(src.page)}</span>
        </div>
        <div class="source-title">${esc(src.title)}</div>
        <div class="source-summary">${esc(src.summary)}</div>
        ${tagsHTML ? `<div class="source-tags">${tagsHTML}</div>` : ""}
        ${linkHTML}
      </div>`;
  }).join("");

  return `
    <div class="sidebar" id="sb-${esc(cluster.id)}"
         role="dialog" aria-label="${esc(cluster.title)}">
      <div class="sb-header">
        <div class="sb-meta">
          <div class="sb-eyebrow">Period ${num} · ${esc(cluster.range)}</div>
          <h2 class="sb-title">${esc(cluster.title)}</h2>
          <div class="sb-count">${count} source${count !== 1 ? "s" : ""}</div>
        </div>
        <button class="sb-close" aria-label="Close sidebar">
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
            <path d="M1 1l10 10M11 1L1 11" stroke="currentColor"
                  stroke-width="1.5" stroke-linecap="round"/>
          </svg>
        </button>
      </div>
      ${summaryHTML}
      <div class="sb-sources">${sourcesHTML}</div>
    </div>`;
}


/* ── Static shell (renders once on load) ── */

function renderShell(query) {
  document.getElementById("app").innerHTML = `
    <header class="site-header">
      <div class="header-inner">
        <div class="header-brand">
          <span class="header-eyebrow">${esc(CONFIG.siteLabel)}</span>
          <h1 class="header-title">${esc(CONFIG.toolName)}</h1>
          <p class="header-desc">${esc(CONFIG.description)}</p>
        </div>
        <div class="search-box">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <circle cx="6.5" cy="6.5" r="4.5" stroke="currentColor" stroke-width="1.5"/>
            <path d="M10 10l3.5 3.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
          <input type="text" id="search-input"
                 value="${esc(query)}" placeholder="Search the archive…">
          <button class="search-btn" id="search-btn">Search</button>
        </div>
      </div>
    </header>

    <div class="results-banner" id="results-banner" style="display:none">
      <div class="results-query">
        <span class="results-label">Results for</span>
        <span class="results-term" id="banner-query"></span>
      </div>
      <div class="results-stats">
        <div class="stat-pill">
          <span class="stat-num" id="stat-periods">—</span>
          <span class="stat-label">periods</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-pill">
          <span class="stat-num" id="stat-sources">—</span>
          <span class="stat-label">sources</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-pill">
          <span class="stat-num" id="stat-span">—</span>
          <span class="stat-label">span</span>
        </div>
      </div>
    </div>

    <div class="timeline-scroll" id="timeline-scroll" style="display:none">
      <div class="timeline-inner" id="timeline"></div>
    </div>

    <div class="status-bar" id="status-bar" style="display:none">
      <span class="status-dot"></span>
      <span id="status-msg">Starting…</span>
    </div>

    <div class="sidebar-backdrop" id="backdrop"></div>
  `;

  wireSearch();
  wireBackdrop();
}


/* ── Banner + stat updaters ── */

function showBanner(query) {
  document.getElementById("results-banner").style.display = "";
  document.getElementById("banner-query").textContent = `"${query}"`;
}

function updateStats({ periods, sources, span }) {
  if (periods != null) document.getElementById("stat-periods").textContent = periods;
  if (sources != null) document.getElementById("stat-sources").textContent = sources;
  if (span    != null) document.getElementById("stat-span").textContent    = span;
}

function setStatus(msg, visible = true) {
  const bar = document.getElementById("status-bar");
  bar.style.display = visible ? "" : "none";
  if (visible) document.getElementById("status-msg").textContent = msg;
}


/* ── Timeline slot updaters ── */

/** Render N skeleton slots to give immediate visual feedback */
function renderSkeletons(n) {
  const timeline = document.getElementById("timeline");
  document.getElementById("timeline-scroll").style.display = "";

  const html = Array.from({ length: n }, (_, i) =>
    slotHTML({ id: `sk${i}`, year: "", range: "", title: "", summary: "", coverPub: "", sources: [] }, i, true)
  ).join("");

  timeline.innerHTML = html;
}

/** Replace one skeleton slot with a real enriched card + sidebar */
function hydrateSlot(cluster, index) {
  const slot = document.getElementById(`slot-${index}`);
  if (!slot) return;

  /* Inject the real card in place of the skeleton */
  slot.outerHTML = slotHTML(cluster, index, false);

  /* Append the sidebar to <body> and wire it */
  const sbEl = document.createElement("div");
  sbEl.innerHTML = sidebarHTML(cluster, index);
  document.body.appendChild(sbEl.firstElementChild);

  wireCard(document.querySelector(`[data-sidebar="sb-${cluster.id}"]`));
  wireSidebarClose(document.getElementById(`sb-${cluster.id}`));
}


/* ── Event wiring ── */

function openSidebar(id) {
  document.querySelectorAll(".sidebar.open").forEach(s => s.classList.remove("open"));
  document.querySelectorAll(".card.active").forEach(c => c.classList.remove("active"));

  const sidebar = document.getElementById(id);
  if (!sidebar) return;
  sidebar.classList.add("open");
  document.getElementById("backdrop").classList.add("visible");

  const card = document.querySelector(`.card[data-sidebar="${id}"]`);
  if (card) card.classList.add("active");
}

function closeAll() {
  document.querySelectorAll(".sidebar.open").forEach(s => s.classList.remove("open"));
  document.querySelectorAll(".card.active").forEach(c => c.classList.remove("active"));
  document.getElementById("backdrop").classList.remove("visible");
}

function wireCard(card) {
  if (!card) return;
  const handler = () => openSidebar(card.dataset.sidebar);
  card.addEventListener("click", handler);
  card.addEventListener("keydown", e => {
    if (e.key === "Enter" || e.key === " ") handler();
  });
}

function wireSidebarClose(sidebar) {
  if (!sidebar) return;
  sidebar.querySelector(".sb-close")?.addEventListener("click", closeAll);
}

function wireBackdrop() {
  document.getElementById("backdrop").addEventListener("click", closeAll);
  document.addEventListener("keydown", e => { if (e.key === "Escape") closeAll(); });
}

function wireSearch() {
  const btn   = document.getElementById("search-btn");
  const input = document.getElementById("search-input");

  const run = () => {
    const q = input.value.trim();
    if (q) startSearch(q);
  };

  btn.addEventListener("click", run);
  input.addEventListener("keydown", e => { if (e.key === "Enter") run(); });
}


/* ── API ── */

let activeReader = null;  /* Track the current stream so we can abort on new search */

async function startSearch(query) {
  /* Abort any in-flight stream */
  if (activeReader) {
    try { activeReader.cancel(); } catch (_) {}
    activeReader = null;
  }

  /* Close any open sidebar */
  closeAll();

  /* Remove stale sidebars from a previous run */
  document.querySelectorAll(".sidebar").forEach(s => s.remove());

  /* Reset timeline */
  const timeline = document.getElementById("timeline");
  if (timeline) timeline.innerHTML = "";
  document.getElementById("timeline-scroll").style.display = "none";

  showBanner(query);
  updateStats({ periods: "—", sources: "—", span: "—" });
  setStatus("Starting…");

  /* Disable search button while running */
  const btn = document.getElementById("search-btn");
  btn.disabled = true;
  btn.textContent = "Running…";

  const base = CONFIG.apiUrl.replace(/\/$/, "");

  try {
    /* 1. POST /chronicle → job_id */
    const initRes = await fetch(`${base}/chronicle`, {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ query }),
    });

    if (!initRes.ok) throw new Error(`POST /chronicle failed: ${initRes.status}`);

    const { job_id } = await initRes.json();
    setStatus(`Job started (${job_id.slice(0, 8)}…) — fetching results…`);

    /* 2. GET /chronicle/{job_id}/stream → SSE */
    const streamRes = await fetch(`${base}/chronicle/${job_id}/stream`);
    if (!streamRes.ok) throw new Error(`Stream failed: ${streamRes.status}`);

    const reader = streamRes.body.getReader();
    activeReader = reader;
    const decoder = new TextDecoder();

    let buffer   = "";
    let eventType = "";

    /* Running totals for the banner */
    let totalSources = 0;
    let spanFirst    = "";
    let spanLast     = "";
    let clusterCount = 0;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop();  /* keep incomplete line */

      for (const raw of lines) {
        const line = raw.trim();

        if (line.startsWith("event:")) {
          eventType = line.slice(6).trim();

        } else if (line.startsWith("data:")) {
          const payload = JSON.parse(line.slice(5).trim());

          if (eventType === "clusters_ready") {
            clusterCount = payload.cluster_count ?? 0;
            setStatus(`${clusterCount} time periods found — enriching with context…`);
            updateStats({ periods: clusterCount });
            renderSkeletons(clusterCount);

          } else if (eventType === "cluster_enriched") {
            const cluster = apiClusterToShape(payload);

            /* Update running banner stats */
            totalSources += payload.entry_count ?? cluster.sources.length;
            if (!spanFirst) spanFirst = cluster.year.split("\n")[0].trim();
            spanLast = cluster.year.split("\n")[0].trim();

            hydrateSlot(cluster, payload.index);

            const done = payload.index + 1;
            setStatus(`Enriched ${done} of ${clusterCount} periods…`);
            updateStats({
              sources: totalSources,
              span: spanFirst === spanLast ? spanFirst : `${spanFirst} – ${spanLast}`,
            });

          } else if (eventType === "done") {
            setStatus("", false);

          } else if (eventType === "error") {
            throw new Error(payload.message ?? "Unknown API error");
          }
        }
      }
    }

  } catch (err) {
    if (err.name === "AbortError") return;  /* user started a new search */
    setStatus(`Error: ${err.message}`);
    console.error("[Chronicle]", err);
  } finally {
    activeReader = null;
    btn.disabled = false;
    btn.textContent = "Search";
  }
}


/* ── Boot ── */
renderShell(CONFIG.defaultQuery);
