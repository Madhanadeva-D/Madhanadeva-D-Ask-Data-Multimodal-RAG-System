import streamlit as st
import requests

API = "http://localhost:8000"

st.set_page_config(
    page_title="Ask Data",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

*, html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    box-sizing: border-box;
}

.stApp { background: #e8edf5; color: #1c2a45; }

[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e2e8f4 !important;
    box-shadow: 2px 0 12px rgba(0,0,0,0.04) !important;
}
[data-testid="stSidebar"] > div { padding-top: 1.5rem; }
[data-testid="stSidebar"] * { color: #1c2a45 !important; }
[data-testid="stSidebar"] hr { border-color: #e2e8f4 !important; }

/* Hide default header & decoration */
header[data-testid="stHeader"] { display: none !important; }
[data-testid="stDecoration"]    { display: none !important; }

/* ── Sidebar collapse arrow — visible on white background ── */
[data-testid="collapsedControl"] {
    background: #1c2a45 !important;
    border: none !important;
    border-radius: 0 8px 8px 0 !important;
    color: #ffffff !important;
    width: 22px !important;
    box-shadow: 2px 0 8px rgba(0,0,0,0.15) !important;
}
[data-testid="collapsedControl"]:hover {
    background: #2a6acc !important;
}
[data-testid="collapsedControl"] svg { fill: #ffffff !important; stroke: #ffffff !important; }

/* ── brand ── */
.brand {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.5rem; font-weight: 700;
    letter-spacing: -0.04em; line-height: 1; color: #0f1a30;
    display: flex; align-items: center; gap: 0.45rem;
}
.brand em {
    font-style: normal;
    background: linear-gradient(135deg, #2a6acc, #4a8fff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.brand-sub {
    font-size: 0.6rem; letter-spacing: 0.18em; text-transform: uppercase;
    color: #94a3b8; margin-top: 0.25rem; margin-bottom: 1.5rem; font-weight: 500;
}

/* ── badge ── */
.badge {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 4px 12px; border-radius: 100px;
    font-size: 0.7rem; font-weight: 600; letter-spacing: 0.04em;
    font-family: 'Space Grotesk', sans-serif;
}
.badge-ok  { background: #ecfdf5; color: #059669; border: 1px solid #a7f3d0; }
.badge-bad { background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; }
.bdot { width: 6px; height: 6px; border-radius: 50%; display: inline-block; flex-shrink: 0; }
.bdot-ok  { background: #10b981; box-shadow: 0 0 6px #10b98180; }
.bdot-bad { background: #ef4444; box-shadow: 0 0 6px #ef444480; }

/* ── sidebar nav label ── */
.nav-label {
    font-size: 0.6rem; letter-spacing: 0.2em; text-transform: uppercase;
    color: #94a3b8; margin-top: 1.2rem; margin-bottom: 0.5rem;
    font-family: 'Space Grotesk', sans-serif; font-weight: 600;
}
.stat-card {
    background: #f0f4fb; border: 1px solid #dde4f0;
    border-radius: 10px; padding: 0.75rem 0.9rem; margin-bottom: 0.45rem;
}
.stat-val {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.4rem; font-weight: 700;
    letter-spacing: -0.04em; color: #0f172a; line-height: 1;
}
.stat-lbl { font-size: 0.6rem; color: #94a3b8; letter-spacing: 0.12em; text-transform: uppercase; margin-top: 0.2rem; }

/* ── cards ── */
.card {
    background: #ffffff; border: 1px solid #dde4f0;
    border-radius: 12px; padding: 1.1rem 1.3rem; margin-bottom: 0.75rem;
    transition: border-color 0.2s, box-shadow 0.2s;
    position: relative; overflow: hidden;
    box-shadow: 0 1px 4px rgba(30,60,120,0.07), 0 4px 16px rgba(30,60,120,0.05);
}
.card::before {
    content: ''; position: absolute; top: 0; left: 0;
    width: 100%; height: 3px;
    background: linear-gradient(90deg, #e2e8f0, #e2e8f0);
    transition: background 0.2s;
}
.card:hover { border-color: #93c5fd; box-shadow: 0 4px 24px rgba(37,99,235,0.1); }
.card:hover::before { background: linear-gradient(90deg, #3b82f6, #60a5fa, #93c5fd); }
.card-icon { font-size: 1.15rem; margin-bottom: 0.5rem; display: block; }
.card-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.88rem; font-weight: 600; color: #0f172a; margin-bottom: 0.2rem; letter-spacing: -0.01em;
}
.card-desc { font-size: 0.76rem; color: #64748b; line-height: 1.55; margin-bottom: 0; }

/* ── inputs ── */
.stTextArea textarea, .stTextInput input {
    background: #ffffff !important; border: 1.5px solid #e2e8f0 !important;
    border-radius: 8px !important; color: #0f172a !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important; caret-color: #2563eb !important;
    transition: border-color 0.15s, box-shadow 0.15s !important;
    padding: 0.625rem 0.875rem !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
    outline: none !important;
}
.stTextArea textarea::placeholder, .stTextInput input::placeholder {
    color: #cbd5e1 !important;
}

/* ── buttons ── */
.stButton > button {
    background: #1d4ed8 !important;
    color: #ffffff !important; border: none !important;
    border-radius: 8px !important; font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important; font-size: 0.84rem !important;
    letter-spacing: 0.01em !important; padding: 0.5rem 1.25rem !important;
    transition: all 0.15s !important; box-shadow: 0 1px 3px rgba(29,78,216,0.3) !important;
    height: 38px !important;
}
.stButton > button:hover {
    background: #1e40af !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 14px rgba(29,78,216,0.35) !important;
}
.stButton > button:active { transform: translateY(0) !important; box-shadow: none !important; }

/* ── file uploader — full white theme override ── */
[data-testid="stFileUploader"] {
    background: #ffffff !important;
    border-radius: 10px !important;
}
[data-testid="stFileUploader"] > div {
    background: #ffffff !important;
    border: 2px dashed #cbd5e1 !important;
    border-radius: 10px !important;
    transition: border-color 0.2s, background 0.2s !important;
}
[data-testid="stFileUploader"] > div:hover {
    border-color: #3b82f6 !important;
    background: #eff6ff !important;
}
[data-testid="stFileUploaderDropzone"] {
    background: #ffffff !important;
    border-radius: 10px !important;
}
/* Override the dark drop zone inner content */
[data-testid="stFileUploaderDropzone"] > div {
    background: transparent !important;
}
[data-testid="stFileUploaderDropzone"] small,
[data-testid="stFileUploaderDropzone"] span,
[data-testid="stFileUploaderDropzone"] p {
    color: #64748b !important;
    font-size: 0.8rem !important;
}
/* The "Browse files" button inside uploader */
[data-testid="stFileUploaderDropzone"] button {
    background: #1d4ed8 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 7px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.8rem !important;
    padding: 0.4rem 1rem !important;
}
[data-testid="stFileUploaderDropzone"] button:hover {
    background: #1e40af !important;
}
/* Upload icon color */
[data-testid="stFileUploaderDropzone"] svg {
    fill: #94a3b8 !important;
    color: #94a3b8 !important;
}

/* ── answer card ── */
.answer-wrap {
    background: #ffffff; border: 1px solid #dde4f0;
    border-radius: 12px; padding: 1.4rem 1.6rem; margin-top: 0.9rem;
    position: relative; overflow: hidden;
    box-shadow: 0 2px 8px rgba(30,60,120,0.08), 0 8px 24px rgba(30,60,120,0.06);
}
.answer-wrap::before {
    content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 3px;
    background: linear-gradient(90deg, #1d4ed8, #3b82f6, #60a5fa, #3b82f6, #1d4ed8);
}
.answer-glow { display: none; }
.answer-text {
    font-size: 0.9rem; line-height: 1.8; color: #1e293b;
    white-space: pre-wrap; font-weight: 400;
}
.answer-meta {
    display: flex; align-items: center; gap: 0.7rem; flex-wrap: wrap;
    margin-top: 1rem; padding-top: 0.8rem; border-top: 1px solid #f1f5f9;
}
.conf-pill {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.68rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase;
    padding: 3px 10px; border-radius: 100px; border: 1px solid;
}
.source-tag {
    font-size: 0.68rem; color: #475569; background: #f8fafc;
    border: 1px solid #e2e8f0; border-radius: 5px; padding: 2px 8px;
    word-break: break-all; font-style: italic;
}

/* ── history ── */
.hist-card {
    background: #ffffff; border: 1px solid #dde4f0;
    border-radius: 10px; padding: 0.9rem 1.1rem; margin-bottom: 0.5rem;
    transition: border-color 0.15s, box-shadow 0.15s;
    box-shadow: 0 1px 4px rgba(30,60,120,0.06);
}
.hist-card:hover { border-color: #93c5fd; box-shadow: 0 2px 12px rgba(59,130,246,0.09); }
.hist-q {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.82rem; font-weight: 600; color: #0f172a; margin-bottom: 0.35rem;
}
.hist-a { font-size: 0.78rem; color: #475569; line-height: 1.6; }

/* ── manage cards ── */
.manage-card {
    background: #ffffff; border: 1px solid #dde4f0;
    border-radius: 12px; padding: 1.2rem; margin-bottom: 0.75rem;
    box-shadow: 0 1px 4px rgba(30,60,120,0.07), 0 4px 16px rgba(30,60,120,0.04);
}
.manage-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.88rem; font-weight: 600; color: #0f172a; margin-bottom: 0.25rem;
}
.manage-desc { font-size: 0.75rem; color: #64748b; line-height: 1.65; margin-bottom: 0.85rem; }
.manage-desc code {
    background: #f1f5f9; border: 1px solid #e2e8f0; border-radius: 4px;
    padding: 1px 6px; font-size: 0.71rem; color: #1d4ed8; font-family: 'SFMono-Regular', monospace;
}

/* ── metric boxes ── */
.metric-box {
    background: #ffffff; border: 1px solid #dde4f0;
    border-radius: 10px; padding: 0.9rem 1rem; text-align: center;
    transition: border-color 0.15s, box-shadow 0.15s;
    box-shadow: 0 1px 4px rgba(30,60,120,0.07);
}
.metric-box:hover { border-color: #93c5fd; box-shadow: 0 2px 10px rgba(59,130,246,0.1); }
.metric-val {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.5rem; font-weight: 700; letter-spacing: -0.04em; color: #0f172a;
}
.metric-lbl { font-size: 0.6rem; letter-spacing: 0.15em; text-transform: uppercase; color: #94a3b8; margin-top: 0.2rem; }

/* ── section label ── */
.sec-label {
    font-size: 0.62rem; font-weight: 600; letter-spacing: 0.18em; text-transform: uppercase;
    color: #94a3b8; margin-top: 1.4rem; margin-bottom: 0.8rem;
    display: flex; align-items: center; gap: 10px;
}
.sec-label::after { content: ''; flex: 1; height: 1px; background: #e2e8f0; }

/* ── empty state ── */
.empty { text-align: center; padding: 3.5rem 2rem; }
.empty-icon { font-size: 2.2rem; margin-bottom: 0.75rem; display: block; opacity: 0.25; }
.empty-msg {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.9rem; font-weight: 600; letter-spacing: -0.01em; color: #94a3b8;
}
.empty-sub { font-size: 0.75rem; color: #cbd5e1; margin-top: 0.3rem; }

/* ── tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1.5px solid #e2e8f0 !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important; color: #94a3b8 !important;
    font-family: 'Space Grotesk', sans-serif !important; font-size: 0.8rem !important;
    font-weight: 600 !important; letter-spacing: 0.02em !important;
    border-radius: 0 !important; border-bottom: 2px solid transparent !important;
    padding: 0.6rem 1.2rem !important; margin-bottom: -1.5px !important;
    transition: color 0.15s !important;
}
.stTabs [data-baseweb="tab"]:hover { color: #334155 !important; background: #f8fafc !important; }
.stTabs [aria-selected="true"] {
    color: #1d4ed8 !important;
    border-bottom: 2px solid #1d4ed8 !important;
    background: transparent !important;
}
/* Remove Streamlit's default red/pink highlight bar */
.stTabs [data-baseweb="tab-highlight"] { background: transparent !important; }

/* ── top bar ── */
.topbar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.5rem 0; margin-bottom: 0;
    border-bottom: 1px solid #e2e8f0;
}
.topbar-brand {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1rem; font-weight: 700; letter-spacing: -0.03em; color: #0f172a;
    display: flex; align-items: center; gap: 0.4rem;
}
.topbar-brand em {
    font-style: normal;
    background: linear-gradient(135deg, #1d4ed8, #3b82f6);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.topbar-status { font-size: 0.66rem; color: #94a3b8; display: flex; align-items: center; gap: 5px; }

/* ── hero ── */
.hero { padding: 0.8rem 0 0.5rem 0; }
.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.75rem; font-weight: 700;
    letter-spacing: -0.04em; line-height: 1.15;
    color: #0f172a; margin-bottom: 0.4rem;
}
.hero-title span {
    background: linear-gradient(135deg, #1d4ed8, #3b82f6);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.hero-desc {
    font-size: 0.84rem; color: #64748b; line-height: 1.7;
    max-width: 520px; margin-bottom: 1rem; font-weight: 400;
}

/* ── alerts ── */
.stAlert {
    border-radius: 8px !important;
    font-size: 0.82rem !important;
    border: 1px solid !important;
}
/* Remove Streamlit default warning / error / success backgrounds that clash */
div[data-baseweb="notification"] { border-radius: 8px !important; font-size: 0.82rem !important; }

.stSpinner > div { border-top-color: #3b82f6 !important; }
hr { border-color: #e2e8f0 !important; }
[data-testid="stCaptionContainer"] { color: #64748b !important; font-size: 0.75rem !important; }

/* ── layout ── */
.block-container {
    padding-top: 0.3rem !important;
    padding-bottom: 2rem !important;
    max-width: 1100px !important;
}
.block-container > div:first-child { margin-top: 0 !important; padding-top: 0 !important; }
section[data-testid="stMain"] > div { padding-top: 0 !important; }
[data-testid="stMainBlockContainer"] { padding-top: 0.3rem !important; }

/* ── scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #e8edf5; }
::-webkit-scrollbar-thumb { background: #c8d4e8; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #3b82f6; }
</style>
""", unsafe_allow_html=True)


# ── helpers ───────────────────────────────────────────────────────────────────
def _get(path):
    try:
        r = requests.get(f"{API}{path}", timeout=6)
        r.raise_for_status()
        return r.json(), None
    except requests.ConnectionError:
        return None, "Backend offline"
    except Exception as e:
        return None, str(e)


def _post(path, **kw):
    try:
        r = requests.post(f"{API}{path}", timeout=120, **kw)
        r.raise_for_status()
        return r.json(), None
    except requests.ConnectionError:
        return None, "Backend offline"
    except requests.HTTPError as e:
        try:    detail = e.response.json().get("detail", str(e))
        except: detail = str(e)
        return None, detail
    except Exception as e:
        return None, str(e)


def _delete(path, **kw):
    try:
        r = requests.delete(f"{API}{path}", timeout=30, **kw)
        r.raise_for_status()
        return r.json(), None
    except requests.ConnectionError:
        return None, "Backend offline"
    except requests.HTTPError as e:
        try:    detail = e.response.json().get("detail", str(e))
        except: detail = str(e)
        return None, detail
    except Exception as e:
        return None, str(e)


def _conf_style(c):
    if c >= 0.75: return "background:#ecfdf5; color:#059669; border-color:#a7f3d0;"
    if c >= 0.4:  return "background:#fefce8; color:#ca8a04; border-color:#fde68a;"
    return "background:#fef2f2; color:#dc2626; border-color:#fecaca;"


def _render_result(answer, sources, conf):
    pct   = int(conf * 100)
    style = _conf_style(conf)
    stags = "".join(f'<span class="source-tag">{s}</span>' for s in sources) if sources else ""
    st.markdown(
        f'<div class="answer-wrap">'
        f'<div class="answer-glow"></div>'
        f'<div class="answer-text">{answer}</div>'
        f'<div class="answer-meta">'
        f'<span class="conf-pill" style="{style}">◈ {pct}% confidence</span>'
        f'{stags}'
        f'</div></div>',
        unsafe_allow_html=True,
    )


# ── session state ─────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []


# ── sidebar — status only, no user controls ───────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div class="brand">🧠 Ask <em>Data</em></div>'
        '<div class="brand-sub">Multimodal RAG · Nemotron</div>',
        unsafe_allow_html=True,
    )

    h, err = _get("/health")
    if h:
        ok  = h.get("connected", False)
        cls = "badge-ok"  if ok else "badge-bad"
        dot = "bdot-ok"   if ok else "bdot-bad"
        lbl = "System online" if ok else "Degraded"
        st.markdown(
            f'<span class="badge {cls}"><span class="bdot {dot}"></span>{lbl}</span>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<span class="badge badge-bad"><span class="bdot bdot-bad"></span>Offline</span>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="nav-label">Index Stats</div>', unsafe_allow_html=True)
    if h:
        vecs = h.get("vectors")
        col  = h.get("collection", "—")
        st.markdown(
            f'<div class="stat-card">'
            f'<div class="stat-val">{f"{vecs:,}" if isinstance(vecs, int) else "—"}</div>'
            f'<div class="stat-lbl">vectors indexed</div></div>'
            f'<div class="stat-card">'
            f'<div class="stat-val" style="font-size:0.95rem;letter-spacing:0;">{col}</div>'
            f'<div class="stat-lbl">collection</div></div>',
            unsafe_allow_html=True,
        )

    st.divider()
    st.markdown(
        '<div style="font-size:0.62rem;color:#94a3b8;line-height:2.2;letter-spacing:0.04em;">'
        '◈ nvidia/nemotron-3-super-120b<br>'
        '◈ all-MiniLM-L6-v2<br>'
        '◈ Milvus · HNSW / COSINE'
        '</div>',
        unsafe_allow_html=True,
    )


# ── top bar ───────────────────────────────────────────────────────────────────
h_top, _ = _get("/health")
status_dot = "🟢" if (h_top and h_top.get("connected")) else "🔴"
vecs_top   = h_top.get("vectors", "—") if h_top else "—"
vecs_str   = f"{vecs_top:,}" if isinstance(vecs_top, int) else "—"

st.markdown(
    f'<div class="topbar">'
    f'<div class="topbar-brand">🧠 Ask <em>Data</em></div>'
    f'<div class="topbar-status">{status_dot}&nbsp; {vecs_str} vectors indexed</div>'
    f'</div>'
    f'<div class="hero">'
    f'<div class="hero-title">Ask anything.<br><span>Get precise answers.</span></div>'
    f'<div class="hero-desc">Load URLs, PDFs, or images into the knowledge base — '
    f'then query them with natural language. Powered by Nemotron reasoning.</div>'
    f'</div>',
    unsafe_allow_html=True,
)


# ── main tabs ─────────────────────────────────────────────────────────────────
tab_load, tab_query, tab_manage = st.tabs(["⊕  Load Data", "◈  Ask", "⊘  Manage"])


# ══════════════════════════════════════════════════════════════════════════════
# LOAD
# ══════════════════════════════════════════════════════════════════════════════
with tab_load:
    col_url, col_file = st.columns(2, gap="large")

    with col_url:
        st.markdown(
            '<div class="card"><span class="card-icon">🌐</span>'
            '<div class="card-title">From URL</div>'
            '<div class="card-desc">Scrape any public web page — articles, wikis, documentation.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        url_val = st.text_input("url", placeholder="https://en.wikipedia.org/wiki/…",
                                label_visibility="collapsed")
        if st.button("Load URL →", use_container_width=True):
            if not url_val.strip():
                st.warning("Enter a URL first.")
            else:
                with st.spinner("Fetching & indexing…"):
                    data, err = _post("/load", params={"url": url_val.strip()})
                if err:
                    st.error(err)
                else:
                    st.success(f"✓ Indexed {data['chunks']} chunks")
                    st.caption(f"Source ID → {data['source']}")

    with col_file:
        st.markdown(
            '<div class="card"><span class="card-icon">📄</span>'
            '<div class="card-title">From File</div>'
            '<div class="card-desc">Upload a PDF or image — text is extracted automatically via OCR.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        f = st.file_uploader("file", label_visibility="collapsed",
                             type=["pdf","png","jpg","jpeg","tiff","bmp","webp"])
        if f:
            st.caption(f"📎  {f.name}  ·  {f.name.rsplit('.',1)[-1].upper()}  ·  {f.size/1024:.1f} KB")
            if st.button("Load File →", use_container_width=True):
                with st.spinner("Extracting & indexing…"):
                    data, err = _post("/load", files={"file": (f.name, f.getvalue(), f.type)})
                if err:
                    st.error(err)
                else:
                    st.success(f"✓ Indexed {data['chunks']} chunks")
                    st.caption(f"Source ID → {data['source']}")


# ══════════════════════════════════════════════════════════════════════════════
# QUERY
# ══════════════════════════════════════════════════════════════════════════════
with tab_query:
    question = st.text_area(
        "Your question",
        placeholder="e.g.  What are the key findings of the report?",
        height=110,
    )
    ask = st.button("Get Answer →")

    if ask:
        q = question.strip()
        if not q:
            st.warning("Type a question first.")
        else:
            with st.spinner("Searching knowledge base & generating answer…"):
                data, err = _post("/query", json={"question": q})
            if err:
                st.error(err)
            else:
                answer  = data.get("answer", "")
                sources = data.get("sources", [])
                conf    = data.get("confidence", 0.0)
                st.session_state.history.insert(0,
                    {"q": q, "answer": answer, "sources": sources, "conf": conf})
                _render_result(answer, sources, conf)

    hist_start = 1 if ask else 0
    if len(st.session_state.history) > hist_start:
        st.markdown('<div class="sec-label">Previous answers</div>', unsafe_allow_html=True)
        for item in st.session_state.history[hist_start:]:
            preview = item["answer"][:200] + ("…" if len(item["answer"]) > 200 else "")
            st.markdown(
                f'<div class="hist-card">'
                f'<div class="hist-q">Q — {item["q"]}</div>'
                f'<div class="hist-a">{preview}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    if not st.session_state.history and not ask:
        st.markdown(
            '<div class="empty"><span class="empty-icon">🧠</span>'
            '<div class="empty-msg">No queries yet</div>'
            '<div class="empty-sub">Load some data first, then ask your question</div>'
            '</div>',
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════════════════════════════════════
# MANAGE
# ══════════════════════════════════════════════════════════════════════════════
with tab_manage:
    col_del, col_stats = st.columns(2, gap="large")

    with col_del:
        st.markdown(
            '<div class="manage-card"><div class="manage-title">🗑 Delete a Source</div>'
            '<div class="manage-desc">Permanently removes all indexed chunks for a given source.<br><br>'
            '<code>url:https://…</code><br>'
            '<code>pdf:filename.pdf</code><br>'
            '<code>image:filename.jpg</code>'
            '</div></div>',
            unsafe_allow_html=True,
        )
        src = st.text_input("source", placeholder="pdf:my-document.pdf",
                            label_visibility="collapsed")
        if st.button("Delete Source →", use_container_width=True):
            if not src.strip():
                st.warning("Enter a source ID.")
            else:
                with st.spinner("Deleting…"):
                    data, err = _delete("/delete", params={"source": src.strip()})
                if err:
                    st.error(err)
                elif data["deleted"] == 0:
                    st.info("No chunks found for that source ID.")
                else:
                    st.success(f"✓ Removed {data['deleted']} chunks")

    with col_stats:
        st.markdown(
            '<div class="manage-card"><div class="manage-title">◈ System Status</div>'
            '<div class="manage-desc">Live stats from the Milvus vector database.</div></div>',
            unsafe_allow_html=True,
        )
        if st.button("Refresh →", use_container_width=True):
            st.rerun()

        h2, err2 = _get("/health")
        if h2:
            m1, m2, m3 = st.columns(3)
            with m1:
                st.markdown(
                    f'<div class="metric-box">'
                    f'<div class="metric-val">{"OK" if h2.get("connected") else "ERR"}</div>'
                    f'<div class="metric-lbl">Status</div></div>',
                    unsafe_allow_html=True,
                )
            with m2:
                vecs = h2.get("vectors")
                st.markdown(
                    f'<div class="metric-box">'
                    f'<div class="metric-val">{f"{vecs:,}" if isinstance(vecs, int) else "—"}</div>'
                    f'<div class="metric-lbl">Vectors</div></div>',
                    unsafe_allow_html=True,
                )
            with m3:
                st.markdown(
                    f'<div class="metric-box">'
                    f'<div class="metric-val" style="font-size:0.9rem;letter-spacing:0;">'
                    f'{h2.get("collection","—")}</div>'
                    f'<div class="metric-lbl">Collection</div></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.error(f"Unreachable: {err2}")