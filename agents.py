import os
import json
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

client = Groq(api_key=st.secrets["GROQ_API_KEY"])
MODEL = "llama-3.1-8b-instant"


# ---------------- PLANNER ---------------- #
def planner_agent(topic):
    return [
        "Introduction",
        "Advantages",
        "Challenges",
        "Real-world Examples",
        "Future Scope"
    ]


# ---------------- EXECUTOR ---------------- #
def executor_agent(topic, step):

    prompt = f"""
    Topic: {topic}
    Section: {step}

    Generate structured report:

    1. Detailed explanation (6–10 lines)
    2. 5 clear points
    3. 3 numeric stats (important metrics)

    Return ONLY JSON:

    {{
        "title": "{step}",
        "content": "detailed explanation",
        "points": [
            "point1",
            "point2",
            "point3",
            "point4",
            "point5"
        ],
        "stats": {{
            "Metric1": 60,
            "Metric2": 80,
            "Metric3": 40
        }}
    }}
    """

    res = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}]
    )

    data = res.choices[0].message.content.strip()
    data = data.replace("```json", "").replace("```", "")

    try:
        parsed = json.loads(data)

        # ✅ Ensure stats always valid
        stats = parsed.get("stats", {})
        clean_stats = {}

        for k, v in stats.items():
            try:
                clean_stats[k] = int(v)
            except:
                clean_stats[k] = 50

        if len(clean_stats) < 3:
            clean_stats = {
                "Metric1": 60,
                "Metric2": 75,
                "Metric3": 45
            }

        return {
            "title": parsed.get("title", step),
            "content": parsed.get("content", ""),
            "points": parsed.get("points", []),
            "stats": clean_stats
        }

    except:
        return {
            "title": step,
            "content": "Error generating content",
            "points": [],
            "stats": {
                "Metric1": 60,
                "Metric2": 75,
                "Metric3": 45
            }
        }


# ---------------- MAIN ---------------- #
def generate_dashboard(topic):
    steps = planner_agent(topic)

    dashboard = []

    for step in steps:
        result = executor_agent(topic, step)
        dashboard.append(result)

    return dashboard
