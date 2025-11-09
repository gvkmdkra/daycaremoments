"""Professional UI Theme for DaycareMoments Application"""

import streamlit as st

def apply_professional_theme():
    """Apply professional purple gradient theme with modern UI elements"""
    st.markdown("""
    <style>
        /* ===== MAIN BACKGROUND ===== */
        .main {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            padding: 2rem !important;
        }

        /* ===== SIDEBAR STYLING ===== */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #667eea 0%, #764ba2 100%) !important;
        }

        section[data-testid="stSidebar"] * {
            color: white !important;
        }

        section[data-testid="stSidebar"] .stRadio > label,
        section[data-testid="stSidebar"] .stSelectbox > label,
        section[data-testid="stSidebar"] .stMultiSelect > label,
        section[data-testid="stSidebar"] .stDateInput > label,
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {
            color: white !important;
        }

        /* ===== CONTENT CONTAINERS ===== */
        .stApp {
            background: transparent;
        }

        /* White cards for content */
        div[data-testid="stVerticalBlock"] > div {
            background: rgba(255, 255, 255, 0.95) !important;
            border-radius: 20px !important;
            padding: 2rem !important;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1) !important;
            margin: 1rem 0 !important;
            backdrop-filter: blur(10px) !important;
        }

        /* ===== BUTTONS ===== */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 25px !important;
            padding: 0.75rem 2rem !important;
            font-weight: 600 !important;
            font-size: 16px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
        }

        .stButton > button:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6) !important;
            background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
        }

        .stButton > button:active {
            transform: translateY(-1px) !important;
        }

        /* Download button special styling */
        .stDownloadButton > button {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%) !important;
        }

        .stDownloadButton > button:hover {
            background: linear-gradient(135deg, #38ef7d 0%, #11998e 100%) !important;
        }

        /* ===== INPUT FIELDS ===== */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div > select,
        .stNumberInput > div > div > input,
        .stDateInput > div > div > input {
            border-radius: 15px !important;
            border: 2px solid #667eea !important;
            padding: 12px !important;
            font-size: 16px !important;
            transition: all 0.3s ease !important;
        }

        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus,
        .stSelectbox > div > div > select:focus,
        .stNumberInput > div > div > input:focus,
        .stDateInput > div > div > input:focus {
            border-color: #764ba2 !important;
            box-shadow: 0 0 0 3px rgba(118, 75, 162, 0.2) !important;
        }

        /* ===== HEADERS ===== */
        h1, h2, h3, h4, h5, h6 {
            color: #2d3748 !important;
            font-weight: 700 !important;
            margin-bottom: 1rem !important;
        }

        h1 {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 3rem !important;
        }

        h2 {
            color: #667eea !important;
            font-size: 2rem !important;
        }

        h3 {
            color: #764ba2 !important;
            font-size: 1.5rem !important;
        }

        /* ===== TABS ===== */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background: rgba(255, 255, 255, 0.9) !important;
            border-radius: 15px !important;
            padding: 10px !important;
        }

        .stTabs [data-baseweb="tab"] {
            background: transparent !important;
            border-radius: 10px !important;
            padding: 12px 24px !important;
            font-weight: 600 !important;
            color: #667eea !important;
            transition: all 0.3s ease !important;
        }

        .stTabs [data-baseweb="tab"]:hover {
            background: rgba(102, 126, 234, 0.1) !important;
        }

        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
        }

        /* ===== METRICS ===== */
        [data-testid="stMetricValue"] {
            font-size: 2.5rem !important;
            font-weight: 700 !important;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        [data-testid="stMetricLabel"] {
            font-size: 1rem !important;
            font-weight: 600 !important;
            color: #4a5568 !important;
        }

        [data-testid="stMetricDelta"] {
            font-weight: 600 !important;
        }

        /* ===== DATAFRAMES ===== */
        .dataframe {
            border-radius: 15px !important;
            overflow: hidden !important;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
        }

        .dataframe thead tr th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            font-weight: 600 !important;
            padding: 15px !important;
        }

        .dataframe tbody tr:nth-child(odd) {
            background: rgba(102, 126, 234, 0.05) !important;
        }

        .dataframe tbody tr:hover {
            background: rgba(102, 126, 234, 0.1) !important;
        }

        /* ===== EXPANDER ===== */
        .streamlit-expanderHeader {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%) !important;
            border-radius: 15px !important;
            padding: 15px !important;
            font-weight: 600 !important;
            color: #667eea !important;
            border: 2px solid rgba(102, 126, 234, 0.3) !important;
        }

        .streamlit-expanderHeader:hover {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%) !important;
        }

        /* ===== SUCCESS/ERROR/INFO BOXES ===== */
        .stSuccess {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%) !important;
            color: white !important;
            border-radius: 15px !important;
            padding: 15px !important;
            border: none !important;
        }

        .stError {
            background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%) !important;
            color: white !important;
            border-radius: 15px !important;
            padding: 15px !important;
            border: none !important;
        }

        .stInfo {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border-radius: 15px !important;
            padding: 15px !important;
            border: none !important;
        }

        .stWarning {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
            color: white !important;
            border-radius: 15px !important;
            padding: 15px !important;
            border: none !important;
        }

        /* ===== CHAT MESSAGES ===== */
        .stChatMessage {
            background: rgba(255, 255, 255, 0.95) !important;
            border-radius: 20px !important;
            padding: 20px !important;
            margin: 15px 0 !important;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
        }

        .stChatMessage[data-testid*="user"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border-left: 6px solid #fff !important;
        }

        .stChatMessage[data-testid*="assistant"] {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%) !important;
            border-left: 6px solid #667eea !important;
        }

        /* ===== FILE UPLOADER ===== */
        .stFileUploader {
            background: rgba(255, 255, 255, 0.9) !important;
            border-radius: 20px !important;
            border: 3px dashed #667eea !important;
            padding: 30px !important;
            transition: all 0.3s ease !important;
        }

        .stFileUploader:hover {
            border-color: #764ba2 !important;
            background: rgba(102, 126, 234, 0.05) !important;
        }

        /* ===== PROGRESS BAR ===== */
        .stProgress > div > div {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            border-radius: 10px !important;
        }

        /* ===== RADIO BUTTONS & CHECKBOXES ===== */
        .stRadio > label,
        .stCheckbox > label {
            font-weight: 600 !important;
            color: #2d3748 !important;
        }

        /* ===== SELECTBOX ===== */
        .stSelectbox > div > div {
            border-radius: 15px !important;
            border: 2px solid #667eea !important;
        }

        /* ===== IMAGES ===== */
        img {
            border-radius: 15px !important;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
            transition: all 0.3s ease !important;
        }

        img:hover {
            transform: scale(1.02) !important;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2) !important;
        }

        /* ===== COLUMNS ===== */
        [data-testid="column"] {
            background: rgba(255, 255, 255, 0.5) !important;
            border-radius: 15px !important;
            padding: 15px !important;
            margin: 5px !important;
        }

        /* ===== SPINNER ===== */
        .stSpinner > div {
            border-top-color: #667eea !important;
            border-right-color: #764ba2 !important;
        }

        /* ===== TOOLTIPS ===== */
        .stTooltipIcon {
            color: #667eea !important;
        }

        /* ===== MARKDOWN TABLES ===== */
        table {
            border-radius: 15px !important;
            overflow: hidden !important;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
        }

        table thead {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
        }

        table tbody tr:nth-child(odd) {
            background: rgba(102, 126, 234, 0.05) !important;
        }

        /* ===== SCROLLBAR ===== */
        ::-webkit-scrollbar {
            width: 12px;
            height: 12px;
        }

        ::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
        }

        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        }

        /* ===== ANIMATION FOR PAGE LOAD ===== */
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .main > div {
            animation: fadeIn 0.5s ease-in-out;
        }
    </style>
    """, unsafe_allow_html=True)


def create_metric_card(label, value, delta=None, delta_color="normal"):
    """Create a professional metric card with gradient styling"""
    delta_html = ""
    if delta:
        color = "#38ef7d" if delta_color == "normal" else "#f45c43"
        delta_html = f'<div style="color: {color}; font-size: 14px; font-weight: 600; margin-top: 5px;">{"↑" if delta_color == "normal" else "↓"} {delta}</div>'

    return f"""
    <div style="
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 255, 255, 0.85) 100%);
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 2px solid rgba(102, 126, 234, 0.2);
        transition: all 0.3s ease;
        height: 100%;
    ">
        <div style="color: #667eea; font-size: 14px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px;">
            {label}
        </div>
        <div style="
            font-size: 36px;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        ">
            {value}
        </div>
        {delta_html}
    </div>
    """


def create_feature_card(icon, title, description):
    """Create a professional feature card"""
    return f"""
    <div style="
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 255, 255, 0.85) 100%);
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border-left: 6px solid;
        border-image: linear-gradient(135deg, #667eea 0%, #764ba2 100%) 1;
        transition: all 0.3s ease;
        height: 100%;
    ">
        <div style="font-size: 48px; margin-bottom: 15px;">{icon}</div>
        <h3 style="
            color: #667eea;
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 15px;
        ">{title}</h3>
        <p style="
            color: #4a5568;
            font-size: 16px;
            line-height: 1.6;
        ">{description}</p>
    </div>
    """
