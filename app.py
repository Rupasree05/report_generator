import streamlit as st
import pandas as pd
from agents import generate_dashboard
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from pptx import Presentation
import io
import matplotlib.pyplot as plt
import re
import whisper
import tempfile

# ---------- CONFIG ----------
st.set_page_config(page_title="AI Dashboard", layout="wide")

# ---------- LOAD MODEL ----------
model = whisper.load_model("base")

# ---------- STYLE ----------
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

# ---------- TITLE ----------
st.title("🤖 Autonomous Report Generator")

# ---------- INPUT ----------
topic = st.text_input("Enter your topic:", key="topic_input")

# ---------- VOICE INPUT ----------
st.markdown("### 🎤 Voice Input")

audio_file = st.file_uploader("Upload audio (wav/mp3)", type=["wav", "mp3"])

def transcribe_audio(audio_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio_file.read())
        tmp_path = tmp.name

    result = model.transcribe(tmp_path)
    return result["text"]

if audio_file:
    st.audio(audio_file)

    if st.button("Convert Voice to Text", key="voice_btn"):
        topic = transcribe_audio(audio_file)
        st.success(f"Recognized: {topic}")

# ---------- PDF ----------
def create_pdf(data, topic):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    content = []
    content.append(Paragraph(f"<b>Report: {topic}</b>", styles["Title"]))
    content.append(Spacer(1, 20))

    for i, section in enumerate(data, start=1):
        content.append(Paragraph(f"<b>{i}. {section['title']}</b>", styles["Heading2"]))
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

# ---------- PPT ----------
def create_ppt(data):
    prs = Presentation()

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

# ---------- GENERATE ----------
if st.button("Generate Report", key="generate_btn"):

    if topic:
        data = generate_dashboard(topic)

        st.success("Report Generated!")

        # ---------- DISPLAY ----------
        st.markdown(f"# 📊 Report: {topic}")

        for i, section in enumerate(data, start=1):
            st.markdown(f"## {i}. {section['title']}")
            st.write(section["content"])

            for idx, p in enumerate(section["points"], start=1):
                st.write(f"{idx}. {p}")

        # ---------- CHART ----------
        st.markdown("## 📈 Analysis")

        all_stats = {}
        for section in data:
            stats = section.get("stats", {})
            for k, v in stats.items():
                try:
                    all_stats[k] = int(v)
                except:
                    all_stats[k] = 50

        df = pd.DataFrame(list(all_stats.items()), columns=["Metric", "Value"])

        if not df.empty:
            st.bar_chart(df.set_index("Metric"))
            st.line_chart(df.set_index("Metric"))

            fig, ax = plt.subplots()
            df.set_index("Metric").plot.pie(y="Value", autopct="%1.1f%%", ax=ax)
            st.pyplot(fig)
        else:
            st.warning("No chart data available")

        # ---------- DOWNLOAD ----------
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
        st.warning("Please enter or record a topic")
