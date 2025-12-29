import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Marketing Funnel Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_excel("demo_data.xlsx", sheet_name="STAGE 5")

    def extract_funnel_row(row):
        status = row["Person Status"]
        citizenship = str(row.get("Person Citizenship", "")).strip().lower()
        is_domestic = "Domestic" if citizenship == "united states" else "International"
        return {
            "Funnel Stage": "Prospect" if status == "Prospect" else
                            "Inquiry" if status == "Inquiry" else
                            "Applicant" if status == "Applicant" else
                            "Enrolled" if status == "Enrolled" else None,
            "Term": row.get("Person Inquiry Term") if status == "Inquiry" else row.get("Applications Applied Term"),
            "Program": row.get("Person Inquiry Program") if status == "Inquiry" else row.get("Applications Applied Program"),
            "Campaign": str(row.get("Ping UTM Campaign")),
            "Source": str(row.get("Ping UTM Source")),
            "Medium": str(row.get("Ping UTM Medium")),
            "Modality": row.get("Application APOS Program Modality"),
            "Citizenship": row.get("Person Citizenship"),
            "Residency": is_domestic,
            "Created Date": pd.to_datetime(row.get("Applications Created Date"), errors='coerce'),
            "Submitted Date": pd.to_datetime(row.get("Applications Submitted Date"), errors='coerce'),
            "Payment Date": pd.to_datetime(row.get("App Fee Received Date"), errors='coerce')
        }

    funnel_data = df[df["Person Status"].isin(["Prospect", "Inquiry", "Applicant", "Enrolled"])]
    funnel_records = funnel_data.apply(extract_funnel_row, axis=1)
    df_parsed = pd.DataFrame(funnel_records.tolist()).dropna(subset=["Funnel Stage"])
    return df_parsed

df = load_data()

st.title("# PIPELINE DEVELOPER RESEARCH LAB", unsafe_allow_html=True)
st.markdown("### Applied Research • AI Systems • Data Analytics")
")

st.markdown("""
    <style>
        .stDownloadButton, .stDataFrame > div:nth-child(1) > button {display: none;}
    </style>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Marketing Funnel", "Demographics & Modality", "Domestic vs International"])

# PAGE 1 and PAGE 2 logic unchanged above...


# ------------------- PAGE 1 -------------------
with tab1:
    st.header("📈 Funnel Overview")

    with st.sidebar:
        st.header("🔍 Filters")
        terms = ["All Terms"] + sorted(df["Term"].dropna().unique().tolist())
        selected_term = st.selectbox("Select Term", terms)
        programs = ["All Programs"] + sorted(df["Program"].dropna().unique().tolist())
        selected_program = st.selectbox("Select Program", programs)

    filtered_df = df.copy()
    if selected_term != "All Terms":
        filtered_df = filtered_df[filtered_df["Term"] == selected_term]
    if selected_program != "All Programs":
        filtered_df = filtered_df[filtered_df["Program"] == selected_program]

    funnel_order = ["Prospect", "Inquiry", "Applicant", "Enrolled"]
    funnel_counts = filtered_df["Funnel Stage"].value_counts().reindex(funnel_order).fillna(0).astype(int)

    conversions = {
        "Stage": ["Prospect → Inquiry", "Inquiry → Applicant", "Applicant → Enrolled"],
        "Conversion Rate": [
            round((funnel_counts["Inquiry"] / funnel_counts["Prospect"] * 100), 1) if funnel_counts["Prospect"] > 0 else 0,
            round((funnel_counts["Applicant"] / funnel_counts["Inquiry"] * 100), 1) if funnel_counts["Inquiry"] > 0 else 0,
            round((funnel_counts["Enrolled"] / funnel_counts["Applicant"] * 100), 1) if funnel_counts["Applicant"] > 0 else 0
        ]
    }
    conversions_df = pd.DataFrame(conversions)

    st.subheader(f"Funnel Counts for: {selected_program} / {selected_term}")
    st.dataframe(funnel_counts.reset_index().rename(columns={"index": "Stage", "Funnel Stage": "Count"}))
    st.subheader("📊 Conversion Rates")
    st.dataframe(conversions_df)

    fig = px.bar(x=funnel_counts.index, y=funnel_counts.values, labels={'x': 'Funnel Stage', 'y': 'Count'}, text=funnel_counts.values)
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📣 UTM Campaign, Source & Medium Performance")

    campaign_counts = filtered_df["Campaign"].astype(str).value_counts().reset_index()
    campaign_counts.columns = ["UTM Campaign", "Count"]
    fig_campaign = px.bar(campaign_counts.head(15), x="Count", y="UTM Campaign", orientation='h', title="Top 15 Campaigns", text="Count")
    st.plotly_chart(fig_campaign, use_container_width=True)

    source_counts = filtered_df["Source"].astype(str).value_counts().reset_index()
    source_counts.columns = ["UTM Source", "Count"]
    fig_source = px.pie(source_counts.head(10), names="UTM Source", values="Count", hole=0.4, title="Top Sources")
    st.plotly_chart(fig_source, use_container_width=True)

    medium_counts = filtered_df["Medium"].astype(str).value_counts().reset_index()
    medium_counts.columns = ["UTM Medium", "Count"]
    fig_medium = px.funnel(medium_counts.head(10), y="UTM Medium", x="Count", title="Medium Funnel")
    st.plotly_chart(fig_medium, use_container_width=True)

# ------------------- PAGE 2 -------------------
with tab2:
    st.header("👥 Demographics & Modality")

    with st.sidebar:
        st.header("🔍 Demographics Filters")
        terms2 = ["All Terms"] + sorted(df["Term"].dropna().unique().tolist())
        selected_term2 = st.selectbox("Select Term (Page 2)", terms2)
        programs2 = ["All Programs"] + sorted(df["Program"].dropna().unique().tolist())
        selected_program2 = st.selectbox("Select Program (Page 2)", programs2)

    demo_df = df[df["Funnel Stage"] == "Enrolled"].copy()
    if selected_term2 != "All Terms":
        demo_df = demo_df[demo_df["Term"] == selected_term2]
    if selected_program2 != "All Programs":
        demo_df = demo_df[demo_df["Program"] == selected_program2]

    st.subheader("🏫 Enrollments by Modality")
    modality_counts = demo_df["Modality"].value_counts().reset_index()
    modality_counts.columns = ["Modality", "Count"]
    fig_modality = px.pie(modality_counts, names="Modality", values="Count", hole=0.4)
    st.plotly_chart(fig_modality, use_container_width=True)

    st.subheader("📅 Enrollment Modality by Term")
    modality_term = demo_df.groupby(["Term", "Modality"]).size().reset_index(name="Count")
    fig_modality_term = px.bar(modality_term, x="Term", y="Count", color="Modality", barmode="group")
    st.plotly_chart(fig_modality_term, use_container_width=True)

    st.subheader("🏆 Top Programs by Modality")
    program_modality = demo_df.groupby(["Program", "Modality"]).size().reset_index(name="Count")
    fig_prog_mod = px.bar(program_modality, x="Count", y="Program", color="Modality", orientation="h")
    st.plotly_chart(fig_prog_mod, use_container_width=True)

    st.subheader("⏱️ Application Timeline Analysis")
    timeline_df = demo_df.copy()
    timeline_df["Created_to_Submitted"] = (timeline_df["Submitted Date"] - timeline_df["Created Date"]).dt.days
    timeline_df["Submitted_to_Paid"] = (timeline_df["Payment Date"] - timeline_df["Submitted Date"]).dt.days
    timeline_df = timeline_df.dropna(subset=["Submitted Date"])
    timeline_df["Month"] = timeline_df["Submitted Date"].dt.to_period("M").dt.to_timestamp()

    ts_grouped = timeline_df.groupby("Month").agg({
        "Created_to_Submitted": "mean",
        "Submitted_to_Paid": "mean"
    }).reset_index()

    fig1 = px.line(ts_grouped, x="Month", y="Created_to_Submitted", title="Avg Days: Created → Submitted")
    fig2 = px.line(ts_grouped, x="Month", y="Submitted_to_Paid", title="Avg Days: Submitted → Payment")
    st.plotly_chart(fig1, use_container_width=True)
    st.plotly_chart(fig2, use_container_width=True)
# PAGE 1 and PAGE 2 logic unchanged above...


# ------------------- PAGE 3 -------------------
with tab3:
    st.header("🌎 Domestic vs International")

    # Sidebar filters for Page 3
    with st.sidebar:
        st.header("🌐 International Filters")
        terms3 = ["All Terms"] + sorted(df["Term"].dropna().unique().tolist())
        selected_term3 = st.selectbox("Select Term (Page 3)", terms3)
        programs3 = ["All Programs"] + sorted(df["Program"].dropna().unique().tolist())
        selected_program3 = st.selectbox("Select Program (Page 3)", programs3)

    intl_df = df.copy()
    if selected_term3 != "All Terms":
        intl_df = intl_df[intl_df["Term"] == selected_term3]
    if selected_program3 != "All Programs":
        intl_df = intl_df[intl_df["Program"] == selected_program3]

    # Pie chart - Domestic vs International (All funnel stages)
    st.subheader("🌍 Domestic vs International")
    pie_data = intl_df["Residency"].value_counts().reset_index()
    pie_data.columns = ["Residency", "Count"]
    fig_pie = px.pie(pie_data, names="Residency", values="Count", hole=0.4)
    st.plotly_chart(fig_pie, use_container_width=True)

    # Domestic vs International by Person Status
    st.subheader("🧮 Domestic & International Leads by Status")
    stacked_data = intl_df[intl_df["Funnel Stage"].isin(["Inquiry", "Applicant", "Enrolled"])]
    bar_df = stacked_data.groupby(["Residency", "Funnel Stage"]).size().reset_index(name="Count")
    fig_bar = px.bar(bar_df, x="Funnel Stage", y="Count", color="Residency", barmode="group")
    st.plotly_chart(fig_bar, use_container_width=True)

    # Country-level map
    st.subheader("🗺️ Applicant Distribution by Country")
    map_df = intl_df[intl_df["Funnel Stage"] == "Applicant"]
    country_df = map_df["Citizenship"].value_counts().reset_index()
    country_df.columns = ["Country", "Applicants"]
    fig_map = px.choropleth(country_df, locations="Country", locationmode="country names",
                            color="Applicants", title="Applicants by Country")
    st.plotly_chart(fig_map, use_container_width=True)

    # Application Trends Over Time (Created Date x Residency)
    st.subheader("📈 Application Trends Over Time")
    time_df = intl_df.dropna(subset=["Created Date"])
    time_df = time_df[time_df["Created Date"] >= "2022-01-01"]
    time_df["Month"] = time_df["Created Date"].dt.to_period("M").dt.to_timestamp()
    trend_df = time_df.groupby(["Month", "Residency"]).size().reset_index(name="Applications")
    fig_trend = px.line(trend_df, x="Month", y="Applications", color="Residency")
    st.plotly_chart(fig_trend, use_container_width=True)

    # Leads Breakdown by Term
    st.subheader("📅 Leads Breakdown by Term")
    term_df = intl_df.copy()
    term_df["Year"] = term_df["Term"].astype(str).str.extract(r"(20\d{2})")
    term_df = term_df[term_df["Year"].astype(float) >= 2022]
    term_df = term_df.groupby(["Term", "Funnel Stage"]).size().reset_index(name="Count")
    fig_term = px.bar(term_df, x="Term", y="Count", color="Funnel Stage", barmode="group")
    st.plotly_chart(fig_term, use_container_width=True)
