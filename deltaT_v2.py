import streamlit as st
import pandas as pd
from datetime import datetime
import io

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Flow Measurement",
    page_icon="⏱️",
    layout="centered",
)


# ── Session-state initialisation ─────────────────────────────────────────────
if "recording" not in st.session_state:
    st.session_state.recording = False
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "measurements" not in st.session_state:
    st.session_state.measurements = []  # list of dicts

    
# Replace the existing st.markdown(...) CSS block with this:
button_color = "#d32f2f" if st.session_state.recording else "#2DC5A2"  # dark red : Streamlit default red

st.markdown(
    f"""
    <style>
    div[data-testid="stButton"] > button[kind="primary"] {{
        height: 5rem;
        font-size: 1.6rem;
        font-weight: 700;
        width: 100%;
        background-color: {button_color} !important;
        border-color: {button_color} !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)



# ── Header ────────────────────────────────────────────────────────────────────
st.title("⏱️ Flow Measurement")
st.caption("Tap **Start** when material begins passing under the sensor, **Stop** when it ends.")

st.divider()

# ── Live elapsed timer (visible only while recording) ────────────────────────
elapsed_placeholder = st.empty()

# if st.session_state.recording and st.session_state.start_time:
#     elapsed = (datetime.now() - st.session_state.start_time).total_seconds()
#     elapsed_placeholder.metric("⏳ Recording…", f"{elapsed:.1f} s")

# ── Start / Stop button ───────────────────────────────────────────────────────
if not st.session_state.recording:
    if st.button("▶ Start", type="primary", use_container_width=True):
        st.session_state.recording = True
        st.session_state.start_time = datetime.now()
        st.rerun()
else:
    if st.button("⏹ Stop", type="primary", width="stretch"):
        end_time = datetime.now()
        start_time = st.session_state.start_time
        delta = (end_time - start_time).total_seconds()

        st.session_state.measurements.append(
            {
                "Start": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "End": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                "ΔT (s)": round(delta, 1),
            }
        )
        st.session_state.recording = False
        st.session_state.start_time = None
        st.rerun()

# # Auto-refresh while recording so the elapsed timer stays live
# if st.session_state.recording:
#     st.caption("🔴 Recording in progress — tap Stop when material has passed.")
#     # Use a short sleep + rerun to tick the timer
#     import time
#     time.sleep(0.5)
#     st.rerun()

st.divider()

# ── Results table ─────────────────────────────────────────────────────────────
measurements = st.session_state.measurements

if not measurements:
    st.info("No measurements yet. Press **Start** to begin your first measurement.")
else:
    st.subheader(f"Results — {len(measurements)} measurement(s)")

    df = pd.DataFrame(measurements)
    df.index = df.index + 1  # 1-based row numbers
    st.dataframe(df, use_container_width=True)

    # ── Actions row ───────────────────────────────────────────────────────────
    col_del, col_csv, col_xlsx = st.columns(3)

    with col_del:
        if st.button("🗑️ Delete last row", use_container_width=True):
            st.session_state.measurements.pop()
            st.rerun()

    # CSV export
    csv_bytes = df.to_csv(index_label="No.").encode("utf-8")
    with col_csv:
        st.download_button(
            label="⬇ Download CSV",
            data=csv_bytes,
            file_name=f"measurements_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    # Excel export
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index_label="No.", sheet_name="Measurements")
    excel_bytes = excel_buffer.getvalue()

    with col_xlsx:
        st.download_button(
            label="⬇ Download Excel",
            data=excel_bytes,
            file_name=f"measurements_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )