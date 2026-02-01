#https://www.youtube.com/watch?v=d7fnzDQ5qM8
# DONE THROUGH AI

import streamlit as st
import time 

st.set_page_config(
    page_title="SponsorSkip + Flashcards",
    layout="wide",
)

# ---------- Helpers ----------
def go(step: str):
    st.session_state["step"] = step

def fetch_transcript(url: str):
    """
    Replace with your real transcript fetch.
    Return: list of dicts: [{"start": 12.3, "duration": 4.2, "text": "..."}, ...]
    """
    # TODO: integrate youtube-transcript-api
    return [
        {"start": 0.0, "duration": 3.0, "text": "Welcome back..."},
        {"start": 30.0, "duration": 6.0, "text": "This video is sponsored by ... use code ..."},
        {"start": 60.0, "duration": 4.0, "text": "Now let's get into the lesson..."},
    ]

def detect_sponsor_segments(segments):
    """
    Replace with your sponsor detector.
    Return: list of (start, end, reason)
    """
    out = []
    for s in segments:
        t = s["text"].lower()
        if "sponsored" in t or "use code" in t:
            out.append((s["start"], s["start"] + s["duration"], "Sponsor cue words"))
    return out

def build_flashcards(segments, target_lang="en"):
    """
    Replace with keyword extraction + translation.
    Return list of cards: [{"front": "...", "back": "..."}, ...]
    """
    return [{"front": "مثال", "back": "example"}]

def fmt_ts(seconds: float) -> str:
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m:02d}:{s:02d}"

# ---------- State ----------
if "step" not in st.session_state:
    st.session_state.step = "home"
if "url" not in st.session_state:
    st.session_state.url = ""
if "transcript" not in st.session_state:
    st.session_state.transcript = None

# ---------- Global header ----------
left, right = st.columns([0.75, 0.25])
with left:
    st.title("SponsorSkip + Flashcards")
    st.caption("Paste a YouTube URL → fetch transcript → detect sponsor segments + generate flashcards.")
with right:
    if st.session_state.step != "home":
        st.button("← New video", use_container_width=True, on_click=lambda: (st.session_state.update({"url":"", "transcript":None}), go("home")))

st.divider()

# ---------- Page 1 ----------
if st.session_state.step == "home":
    col = st.columns([0.15, 0.7, 0.15])[1]
    with col:
        st.subheader("1) Paste a video URL")
        st.session_state.url = st.text_input(
            "YouTube URL",
            value=st.session_state.url,
            placeholder="https://www.youtube.com/watch?v=...",
            label_visibility="collapsed",
        )

        st.write("")
        fetch = st.button("Fetch transcript", type="primary", use_container_width=True, disabled=not st.session_state.url)

        if fetch:
            with st.status("Fetching transcript…", expanded=True) as status:
                try:
                    tr = fetch_transcript(st.session_state.url)
                    st.session_state.transcript = tr
                    status.update(label="Transcript fetched ✅", state="complete")
                    go("analyze")
                    st.rerun()
                except Exception as e:
                    status.update(label="Failed to fetch transcript ❌", state="error")
                    st.error(str(e))

# ---------- Page 2 ----------
elif st.session_state.step == "analyze":
    tr = st.session_state.transcript or []
    st.subheader("2) Choose what to do")
    st.caption(f"Video: {st.session_state.url}")

    tab1, tab2, tab3 = st.tabs(["Sponsor sections", "Flashcards", "Transcript"])

    with tab1:
        st.markdown("### Detect sponsor segments")
        run = st.button("Find sponsor segments", type="primary")
        if run:
            with st.spinner("Analyzing transcript…"):
                segments = detect_sponsor_segments(tr)

            if not segments:
                st.info("No sponsor-like segments detected.")
            else:
                st.success(f"Detected {len(segments)} segment(s).")
                for start, end, reason in segments:
                    st.write(f"**{fmt_ts(start)} → {fmt_ts(end)}** — {reason}")

                st.markdown("#### Copy-friendly output")
                lines = [f"{fmt_ts(a)}-{fmt_ts(b)}" for a, b, _ in segments]
                st.code("\n".join(lines))

    with tab2:
        st.markdown("### Translate + generate flashcards")
        target = st.selectbox("Translate to", ["en", "fr", "es"], index=0)
        make = st.button("Generate flashcards", type="primary")
        if make:
            with st.spinner("Extracting keywords + translating…"):
                cards = build_flashcards(tr, target_lang=target)

            st.success(f"Created {len(cards)} flashcards.")
            for c in cards[:10]:
                st.write(f"**{c['front']}** → {c['back']}")

            # Export CSV (two columns: Front, Back)
            csv = "Front,Back\n" + "\n".join([f"\"{c['front']}\",\"{c['back']}\"" for c in cards])
            st.download_button("Download CSV for Anki", data=csv.encode("utf-8"), file_name="flashcards.csv", mime="text/csv")

    with tab3:
        st.markdown("### Transcript")
        st.caption("Keep it tucked away so your UI stays clean.")
        with st.expander("Show transcript text", expanded=False):
            for s in tr:
                st.write(f"**{fmt_ts(s['start'])}** — {s['text']}")
