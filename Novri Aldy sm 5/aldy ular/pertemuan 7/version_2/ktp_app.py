"""
KTP Data Registration System
----------------------------
A Streamlit application for registering, viewing, and inspecting
Indonesian ID card (KTP) data.

Run with:
    streamlit run ktp_app.py
"""

import re
from datetime import date, datetime

import pandas as pd
import streamlit as st

import json
from pathlib import Path

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="KTP Registration System",
    page_icon="🪪",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
GENDER_OPTIONS = ["Laki-laki", "Perempuan"]
RELIGION_OPTIONS = ["Islam", "Kristen", "Katolik", "Hindu", "Buddha", "Konghucu", "Lainnya"]
MARITAL_OPTIONS = ["Belum Kawin", "Kawin", "Cerai Hidup", "Cerai Mati"]
NATIONALITY_OPTIONS = ["WNI", "WNA"]

# File used to store data permanently (same folder as this script)
DATA_FILE = Path(__file__).parent / "ktp_data.json"

# Column order used for table display
TABLE_COLUMNS = [
    "NIK",
    "Full Name",
    "Place of Birth",
    "Date of Birth",
    "Gender",
    "Address",
    "Religion",
    "Marital Status",
    "Nationality",
    "Occupation",
    "Registered At",
]


# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------
def load_records() -> list:
    """Load saved records from the JSON file (empty list if none)."""
    if not DATA_FILE.exists():
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            records = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []
    # Convert stored ISO date strings back into date objects
    for r in records:
        r["_birth_date"] = date.fromisoformat(r["_birth_date"])
    return records


def save_records() -> None:
    """Write all records in session state to the JSON file."""
    serializable = [
        {**r, "_birth_date": r["_birth_date"].isoformat()}
        for r in st.session_state.records
    ]
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(serializable, f, ensure_ascii=False, indent=2)


def init_state() -> None:
    """Load saved records into session state on first run."""
    if "records" not in st.session_state:
        st.session_state.records = load_records()
    if "form_counter" not in st.session_state:
        st.session_state.form_counter = 0


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def is_valid_nik(nik: str) -> bool:
    """A valid NIK consists of exactly 16 digits."""
    return bool(re.fullmatch(r"\d{16}", nik))


def nik_exists(nik: str) -> bool:
    """Check whether a NIK is already registered."""
    return any(r["NIK"] == nik for r in st.session_state.records)


def calculate_age(birth_date: date) -> int:
    """Calculate age in full years from a birth date."""
    today = date.today()
    return today.year - birth_date.year - (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )


def format_date(d: date) -> str:
    """Format a date as DD-MM-YYYY (the common KTP format)."""
    return d.strftime("%d-%m-%Y")


def initials(name: str) -> str:
    """Return up to two initials from a full name for the avatar."""
    parts = [p for p in name.split() if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][0].upper()
    return (parts[0][0] + parts[-1][0]).upper()


def records_to_dataframe() -> pd.DataFrame:
    """Convert the stored records to a pandas DataFrame for display."""
    if not st.session_state.records:
        return pd.DataFrame(columns=TABLE_COLUMNS)
    df = pd.DataFrame(st.session_state.records)
    return df[TABLE_COLUMNS]


def delete_record(nik: str) -> None:
    """Remove a record by NIK."""
    st.session_state.records = [
        r for r in st.session_state.records if r["NIK"] != nik
    ]
    save_records()


# ---------------------------------------------------------------------------
# Section: registration form
# ---------------------------------------------------------------------------
def render_registration_form() -> None:
    """Render the KTP data input form and handle submission."""
    st.subheader("📝 Register New KTP Data")

    # Changing the key suffix resets all widgets after a successful submit
    key = st.session_state.form_counter

    with st.form(key=f"ktp_form_{key}"):
        col1, col2 = st.columns(2)

        with col1:
            nik = st.text_input(
                "NIK (16 digits)",
                max_chars=16,
                placeholder="e.g. 1271010101900001",
            )
            full_name = st.text_input("Full Name", placeholder="As written on KTP")
            place_of_birth = st.text_input("Place of Birth", placeholder="e.g. Medan")
            birth_date = st.date_input(
                "Date of Birth",
                value=date(2000, 1, 1),
                min_value=date(1900, 1, 1),
                max_value=date.today(),
            )
            gender = st.radio("Gender", GENDER_OPTIONS, horizontal=True)

        with col2:
            address = st.text_area(
                "Address",
                placeholder="Street, RT/RW, Village, District, City",
                height=100,
            )
            religion = st.selectbox("Religion", RELIGION_OPTIONS)
            marital_status = st.selectbox("Marital Status", MARITAL_OPTIONS)
            nationality = st.selectbox("Nationality", NATIONALITY_OPTIONS)
            occupation = st.text_input("Occupation", placeholder="e.g. Student")

        submitted = st.form_submit_button("Register", type="primary")

    if not submitted:
        return

    # ----- Validation -----
    errors = []
    nik = nik.strip()
    if not is_valid_nik(nik):
        errors.append("NIK must be exactly 16 digits (numbers only).")
    elif nik_exists(nik):
        errors.append("This NIK is already registered.")
    if not full_name.strip():
        errors.append("Full name is required.")
    if not place_of_birth.strip():
        errors.append("Place of birth is required.")
    if not address.strip():
        errors.append("Address is required.")
    if not occupation.strip():
        errors.append("Occupation is required.")

    if errors:
        for err in errors:
            st.error(err)
        return

    # ----- Save record -----
    st.session_state.records.append(
        {
            "NIK": nik,
            "Full Name": full_name.strip().title(),
            "Place of Birth": place_of_birth.strip().title(),
            "Date of Birth": format_date(birth_date),
            "Gender": gender,
            "Address": address.strip(),
            "Religion": religion,
            "Marital Status": marital_status,
            "Nationality": nationality,
            "Occupation": occupation.strip().title(),
            "Registered At": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            "_birth_date": birth_date,  # raw date kept for age calculation
        }
    )
    st.session_state.form_counter += 1
    save_records()  # reset the form on next run
    st.session_state.flash = f"KTP for {full_name.strip().title()} registered successfully."
    st.rerun()


# ---------------------------------------------------------------------------
# Section: data table
# ---------------------------------------------------------------------------
def render_data_table() -> None:
    """Show all registered records in a searchable table."""
    st.subheader("📋 Registered KTP Data")

    if not st.session_state.records:
        st.info("No data registered yet. Use the form in the 'Register' tab.")
        return

    df = records_to_dataframe()

    # Simple text search across all columns
    query = st.text_input("🔍 Search (NIK, name, address, etc.)", key="search_query")
    if query:
        mask = df.apply(
            lambda row: row.astype(str).str.contains(query, case=False, regex=False).any(),
            axis=1,
        )
        df = df[mask]

    st.caption(f"Showing {len(df)} of {len(st.session_state.records)} record(s)")
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Download the data as CSV
    st.download_button(
        "⬇️ Download as CSV",
        data=records_to_dataframe().to_csv(index=False).encode("utf-8"),
        file_name="ktp_data.csv",
        mime="text/csv",
    )


# ---------------------------------------------------------------------------
# Section: record selector (shared by detail and profile views)
# ---------------------------------------------------------------------------
def select_record(widget_key: str):
    """Show a selectbox of registered records and return the chosen one."""
    records = st.session_state.records
    if not records:
        st.info("No data registered yet. Use the form in the 'Register' tab.")
        return None

    options = {f"{r['NIK']} — {r['Full Name']}": r for r in records}
    choice = st.selectbox("Select a KTP record", list(options.keys()), key=widget_key)
    return options[choice]


# ---------------------------------------------------------------------------
# Section: detailed information
# ---------------------------------------------------------------------------
def render_detail_view() -> None:
    """Show every field of the selected record in a structured layout."""
    st.subheader("🔎 Detailed Information")
    record = select_record("detail_select")
    if record is None:
        return

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### Identity")
        st.write(f"**NIK:** {record['NIK']}")
        st.write(f"**Full Name:** {record['Full Name']}")
        st.write(
            f"**Place / Date of Birth:** {record['Place of Birth']}, {record['Date of Birth']}"
        )
        st.write(f"**Gender:** {record['Gender']}")
        st.write(f"**Age:** {calculate_age(record['_birth_date'])} years")

    with col2:
        st.markdown("##### Other Details")
        st.write(f"**Address:** {record['Address']}")
        st.write(f"**Religion:** {record['Religion']}")
        st.write(f"**Marital Status:** {record['Marital Status']}")
        st.write(f"**Nationality:** {record['Nationality']}")
        st.write(f"**Occupation:** {record['Occupation']}")

    st.caption(f"Registered at {record['Registered At']}")

    st.markdown("---")
    if st.button("🗑️ Delete this record", key="delete_btn"):
        delete_record(record["NIK"])
        st.session_state.flash = "Record deleted."
        st.rerun()


# ---------------------------------------------------------------------------
# Section: profile card
# ---------------------------------------------------------------------------
def render_profile_card() -> None:
    """Show a styled profile card for the selected KTP owner."""
    st.subheader("👤 KTP Owner Profile")
    record = select_record("profile_select")
    if record is None:
        return

    age = calculate_age(record["_birth_date"])
    avatar_color = "#1f6feb" if record["Gender"] == "Laki-laki" else "#d1457b"

    # Card styling with plain HTML/CSS
    card_html = f"""
    <div style="
        max-width: 640px; margin: 10px auto; padding: 24px;
        border-radius: 16px; border: 1px solid #d0d7de;
        background: linear-gradient(135deg, #f6f8fa 0%, #e8f0fe 100%);
        box-shadow: 0 4px 14px rgba(0,0,0,0.08); color: #1f2328;
        font-family: sans-serif;">
        <div style="display:flex; align-items:center; gap:20px;">
            <div style="
                width:84px; height:84px; border-radius:50%;
                background:{avatar_color}; color:white; font-size:32px;
                font-weight:700; display:flex; align-items:center;
                justify-content:center; flex-shrink:0;">
                {initials(record['Full Name'])}
            </div>
            <div>
                <div style="font-size:24px; font-weight:700;">{record['Full Name']}</div>
                <div style="font-size:14px; color:#57606a;">NIK: {record['NIK']}</div>
                <div style="font-size:14px; color:#57606a;">
                    {record['Gender']} · {age} years old · {record['Nationality']}
                </div>
            </div>
        </div>
        <hr style="margin:18px 0; border:none; border-top:1px solid #d0d7de;">
        <table style="width:100%; font-size:15px; border-collapse:collapse;">
            <tr><td style="padding:5px 0; width:38%; color:#57606a;">Birth</td>
                <td>{record['Place of Birth']}, {record['Date of Birth']}</td></tr>
            <tr><td style="padding:5px 0; color:#57606a;">Occupation</td>
                <td>{record['Occupation']}</td></tr>
            <tr><td style="padding:5px 0; color:#57606a;">Religion</td>
                <td>{record['Religion']}</td></tr>
            <tr><td style="padding:5px 0; color:#57606a;">Marital Status</td>
                <td>{record['Marital Status']}</td></tr>
            <tr><td style="padding:5px 0; color:#57606a; vertical-align:top;">Address</td>
                <td>{record['Address']}</td></tr>
        </table>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Sidebar: summary statistics
# ---------------------------------------------------------------------------
def render_sidebar() -> None:
    """Display quick statistics and a clear-all control in the sidebar."""
    st.sidebar.title("🪪 KTP System")
    st.sidebar.caption("Data is stored in this browser session only.")

    total = len(st.session_state.records)
    st.sidebar.metric("Total Registered", total)

    if total:
        df = pd.DataFrame(st.session_state.records)
        male = int((df["Gender"] == "Laki-laki").sum())
        female = int((df["Gender"] == "Perempuan").sum())
        col1, col2 = st.sidebar.columns(2)
        col1.metric("Male", male)
        col2.metric("Female", female)

        st.sidebar.markdown("---")
        confirm = st.sidebar.checkbox("Confirm clear all data")
        if st.sidebar.button("Clear all data", disabled=not confirm):
            st.session_state.records = []
            save_records()
            st.session_state.flash = "All data cleared."
            st.rerun()


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------
def main() -> None:
    """Application entry point."""
    init_state()
    render_sidebar()

    st.title("🪪 KTP Data Registration System")
    st.caption("Register Indonesian ID card (KTP) data, then browse, inspect, and view profiles.")

    # Show one-time success messages set before a rerun
    if "flash" in st.session_state:
        st.success(st.session_state.pop("flash"))

    tab_register, tab_table, tab_detail, tab_profile = st.tabs(
        ["📝 Register", "📋 All Data", "🔎 Detail", "👤 Profile Card"]
    )

    with tab_register:
        render_registration_form()
    with tab_table:
        render_data_table()
    with tab_detail:
        render_detail_view()
    with tab_profile:
        render_profile_card()


if __name__ == "__main__":
    main()