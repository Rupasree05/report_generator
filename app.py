import streamlit as st
import pandas as pd
import speech_recognition as sr
from agents import generate_dashboard
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from pptx import Presentation
import io
import matplotlib.pyplot as plt
import re

st.set_page_config(page_title="AI Dashboard", layout="wide")

# ---------- UI STYLE ----------
st.markdown("""
<style>
.metric-card {
    background-color: #111827;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ---------- VOICE INPUT ----------
import streamlit as st

st.title("AI Report Generator")

topic = st.text_input("Enter your topic:")

if st.button("Generate Report"):
    if topic:
        st.write("Generating report for:", topic)
        data = generate_dashboard(topic)
        st.write(data)

# ---------- PDF ----------
def create_pdf(data, topic):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    content = []

    content.append(Paragraph(f"<b>Report: {topic}</b>", styles["Title"]))
    content.append(Spacer(1, 20))

    for i, section in enumerate(data, start=1):

        if "Error" in section["content"]:
            continue

        content.append(
            Paragraph(f"<b>{i}. {section['title']}</b>", styles["Heading2"])
        )
        content.append(Spacer(1, 10))

        content.append(Paragraph(section["content"], styles["Normal"]))
        content.append(Spacer(1, 10))

        for p in section["points"]:
            content.append(Paragraph(f"• {p}", styles["Normal"]))
            content.append(Spacer(1, 5))

        content.append(Spacer(1, 20))

    doc.build(content)
    buffer.seek(0)
    return buffer
# ---------- ALL CHARTS (AFTER CONTENT) ----------
    st.markdown("## 📊 Overall Analysis")

    all_stats = {}

# collect stats from all sections
    for section in data:
        stats = section.get("stats", {})
        for k, v in stats.items():
            try:
                all_stats[k] = int(v)
            except:
                all_stats[k] = 50

    import pandas as pd
    df = pd.DataFrame(list(all_stats.items()), columns=["Metric", "Value"])

    if not df.empty:
        st.bar_chart(df.set_index("Metric"))
        st.line_chart(df.set_index("Metric"))

        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        df.set_index("Metric").plot.pie(y="Value", autopct="%1.1f%%", ax=ax)
        st.pyplot(fig)
    else:
        st.warning("No chart data available")


# ---------- PPT ----------
def create_ppt(data):
    prs = Presentation()

    # Title slide
    slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(slide_layout)
    slide.shapes.title.text = "AI Report"
    slide.placeholders[1].text = "Generated using Agentic AI"

    for section in data:
        slide_layout = prs.slide_layouts[1]
        slide = prs.slides.add_slide(slide_layout)

        slide.shapes.title.text = section["title"]

        points = section["points"][:4]
        content = "\n".join([f"• {p}" for p in points])

        slide.placeholders[1].text = content

    buffer = io.BytesIO()
    prs.save(buffer)
    buffer.seek(0)
    return buffer

# ---------- HEADER ----------
st.title("🤖 Autonomous Report Generator")

# ---------- SESSION ----------
if "topic" not in st.session_state:
    st.session_state.topic = ""

topic = st.text_input("Enter your topic", value=st.session_state.topic)

if st.button("🎤 Voice Input"):
    topic = st.text_input("Enter your topic:")

# ---------- GENERATE ----------
if st.button("Generate Report", key="generate_btn"):

    if topic:
        data = generate_dashboard(topic)

        st.success("Report Generated!")

        # ---------- DISPLAY ----------
        st.markdown(f"# Report: {topic}")

        for i, section in enumerate(data, start=1):
            st.markdown(f"## {i}. {section['title']}")
            st.write(section["content"])

            for idx, p in enumerate(section["points"], start=1):
                st.write(f"{idx}. {p}")

        # ---------- DOWNLOADS ----------
        clean_topic = re.sub(r'[^a-zA-Z0-9 ]', '', topic)

        pdf_name = clean_topic.replace(" ", "_") + ".pdf"
        ppt_name = clean_topic.replace(" ", "_") + ".pptx"

        col1, col2 = st.columns(2)

        with col1:
            pdf_file = create_pdf(data, topic)
            st.download_button("📄 Download PDF", pdf_file, file_name=pdf_name)

        with col2:
            ppt_file = create_ppt(data)
            st.download_button("📊 Download PPT", ppt_file, file_name=ppt_name)

    else:
        st.warning("Please enter a topic")
