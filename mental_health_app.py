import streamlit as st
import pandas as pd
import numpy as np
import joblib

# =======================
# Helpers
# =======================
def phq9_severity(score: int) -> str:
    if score <= 4: return "Minimal"
    if score <= 9: return "Mild"
    if score <= 14: return "Moderate"
    if score <= 19: return "Moderately Severe"
    return "Severe"

def gad7_severity(score: int) -> str:
    if score <= 4: return "Minimal"
    if score <= 9: return "Mild"
    if score <= 14: return "Moderate"
    return "Severe"

def pss10_severity(score: int) -> str:
    if score <= 13: return "Low"
    if score <= 26: return "Moderate"
    return "High"

def calculate_overall_risk(phq9_score: int, gad7_score: int, pss10_score: int) -> str:
    """Return overall risk level (Low / Moderate / High) based on 3 scales."""
    risk = "Low"
    if phq9_score >= 20:
        risk = "High"
    elif phq9_score >= 15:
        risk = "Moderate"
    if gad7_score >= 15:
        risk = "High"
    elif gad7_score >= 10 and risk != "High":
        risk = "Moderate"
    if pss10_score >= 27:
        risk = "High"
    elif pss10_score >= 14 and risk != "High":
        risk = "Moderate"
    return risk

def render_mcq_block(title_prefix: str, questions: list[str], option_labels: list[str], option_values: dict[str,int], reverse_index_set=None):
    """Render MCQs and return (total_score, per_item_numeric_scores, per_item_text_choices)."""
    if reverse_index_set is None:
        reverse_index_set = set()
    num_scores = []
    txt_choices = []
    for i, q in enumerate(questions):
        choice = st.radio(
            f"{i+1}. {q}",
            options=option_labels,
            key=f"{title_prefix}_{i}",
            horizontal=True,
            index=0
        )
        val = option_values[choice]
        if i in reverse_index_set:
            val = (len(option_labels) - 1) - val
        num_scores.append(val)
        txt_choices.append(choice)
    return int(np.sum(num_scores)), num_scores, txt_choices

# =======================
# App
# =======================
st.set_page_config(page_title="Mind-Guard", page_icon="🧠", layout="wide")

# App Header
st.markdown(
    """
    <h1 style='text-align: center; font-size: 50px;'>🧠 MIND-GUARD 🧠</h1>
    <h2 style='text-align: center; font-size: 25px;'>ITS TIME TO SEARCH YOUR PSYCHOLOGY</h2>
    """,
    unsafe_allow_html=True
)

# ---------------- Sidebar: Demographics & Lifestyle ----------------
with st.sidebar:
    st.header("📜 Please Fill in the Following Details 📜")
    age = st.number_input("Age", min_value=10, max_value=100, value=25)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    employment_status = st.selectbox("Employment Status", ["Student", "Employed", "Self-Employed", "Unemployed"])
    work_environment = st.selectbox("Work Environment", ["On-site", "Hybrid", "Remote"])
    mental_health_history = st.selectbox("Mental Health History", ["Yes", "No"])
    seeks_treatment = st.selectbox("Seeks Treatment", ["Yes", "No"])
    sleep_hours = st.slider("Sleep Hours per Day", 0, 12, 7)
    physical_activity_days = st.slider("Physical Activity Days per Week", 0, 7, 3)

# ---------------- Main: Questionnaires ----------------
left, right = st.columns(2)

with left:
    # ---------------- PHQ-9 ----------------
    phq9_questions = [
        "Little interest or pleasure in doing things",
        "Feeling down, depressed or hopeless",
        "Trouble falling asleep, staying asleep, or sleeping too much",
        "Feeling tired or having little energy",
        "Poor appetite or overeating",
        "Feeling bad about yourself — or that you’re a failure or have let yourself or your family down",
        "Trouble concentrating on things, such as reading or watching television",
        "Moving or speaking so slowly that other people could have noticed; or the opposite — being so fidgety or restless",
        "Thoughts that you would be better off dead or of hurting yourself in some way",
    ]
    freq_labels = ["Not at all", "Several days", "More than half the days", "Nearly every day"]
    freq_values = {"Not at all":0, "Several days":1, "More than half the days":2, "Nearly every day":3}

    st.markdown("### PHQ-9 (Depression)")
    st.markdown("<p style='color: gray; font-size:14px;'>This section asks about your mood and depressive symptoms over the past two weeks. Please answer honestly.</p>", unsafe_allow_html=True)

    phq9_total, phq9_scores, phq9_choices = render_mcq_block("PHQ9", phq9_questions, freq_labels, freq_values)
    if phq9_scores[-1] > 0:
        st.error("If you've had thoughts of self-harm, please seek immediate help. You’re not alone — reach out to local emergency services or a trusted person.")
    st.write(f"**PHQ-9 total:** {phq9_total} / 27 · Severity: **{phq9_severity(phq9_total)}**")

    # ---------------- GAD-7 ----------------
    gad7_questions = [
        "Feeling nervous, anxious or on edge",
        "Not being able to stop or control worrying",
        "Worrying too much about different things",
        "Trouble relaxing",
        "Being so restless that it is hard to sit still",
        "Becoming easily annoyed or irritable",
        "Feeling afraid as if something awful might happen",
    ]
    st.markdown("### GAD-7 (Anxiety)")
    st.markdown("<p style='color: gray; font-size:14px;'>This section assesses your anxiety symptoms over the past two weeks. Choose the option that best describes your experience.</p>", unsafe_allow_html=True)

    gad7_total, gad7_scores, gad7_choices = render_mcq_block("GAD7", gad7_questions, freq_labels, freq_values)
    st.write(f"**GAD-7 total:** {gad7_total} / 21 · Severity: **{gad7_severity(gad7_total)}**")

    # ---------------- PSS-10 ----------------
    pss10_questions = [
        "In the last month, how often have you been upset because of something unexpected?",
        "In the last month, how often have you felt unable to control important things in your life?",
        "In the last month, how often have you felt nervous and stressed?",
        "In the last month, how often have you felt confident about handling personal problems?",
        "In the last month, how often have you felt that things were going your way?",
        "In the last month, how often have you found that you could not cope with all the things you had to do?",
        "In the last month, how often have you been able to control irritations in your life?",
        "In the last month, how often have you felt you were on top of things?",
        "In the last month, how often have you been angered because of things outside your control?",
        "In the last month, how often have you felt difficulties piling up so high that you could not overcome them?",
    ]
    pss10_labels = ["Never", "Almost Never", "Sometimes", "Fairly Often", "Very Often"]
    pss10_values = {"Never":0, "Almost Never":1, "Sometimes":2, "Fairly Often":3, "Very Often":4}
    reverse_items = {3,4,6,7}

    st.markdown("### PSS-10 (Stress)")
    st.markdown("<p style='color: gray; font-size:14px;'>The questions in this scale ask about your feelings and thoughts during the last month. Indicate how often you felt or thought a certain way.</p>", unsafe_allow_html=True)

    pss10_total, pss10_scores, pss10_choices = render_mcq_block("PSS10", pss10_questions, pss10_labels, pss10_values, reverse_index_set=reverse_items)
    st.write(f"**PSS-10 total:** {pss10_total} / 40 · Severity: **{pss10_severity(pss10_total)}**")

    # ---------------- MSPSS ----------------
    msp_questions = [
        "Someone you can count on to listen to you when you need to talk",
        "Someone to give you good advice about a crisis",
        "Someone to take you to the doctor if you needed it",
        "Someone who shows you love and affection",
        "Someone to give you information to help you understand a situation",
        "Someone to confide in or talk to about yourself or your problems",
        "Someone to get together with for relaxation",
        "Someone to prepare your meals if you were unable to do it yourself",
        "Someone whose advice you really want",
        "Someone to do things with to help you get your mind off things",
        "Someone to help with daily chores if you were sick",
        "Someone to share your most private worries and fears with",
        "Someone to turn to for suggestions about how to deal with a personal problem",
        "Someone to do something enjoyable with",
        "Someone who understands your problems",
        "Someone to love and make you feel wanted"
    ]
    msp_labels = ["None of the time", "A little of the time", "Some of the time", "Most of the time", "All of the time"]
    msp_values = {"None of the time":1, "A little of the time":2, "Some of the time":3, "Most of the time":4, "All of the time":5}

    st.markdown("### Multidimensional Scale of Perceived Social Support (MSPSS)")
    st.markdown("<p style='color: gray; font-size:14px;'>Let's see how you and your surroundings are doing!Please answer some easy questions according to your daily life.</p>", unsafe_allow_html=True)
    msp_total, msp_scores, msp_choices = render_mcq_block("MSPSS", msp_questions, msp_labels, msp_values)
    st.write(f"**Social Support Score (MSPSS):** {msp_total} / {len(msp_questions)*5} · Average: {msp_total/len(msp_questions):.2f}")

# ---------------- Right Column: ML Prediction + Recommendations ----------------
with right:
    st.header("🚨Its Time To Search Your PSYCHOLOGY 👇")
    st.caption("Predict overall risk from demographics + lifestyle + PHQ/GAD/PSS/MSPSS totals.")

    input_df = pd.DataFrame([{
        "age": age,
        "gender": gender,
        "employment_status": employment_status,
        "work_environment": work_environment,
        "mental_health_history": mental_health_history,
        "seeks_treatment": seeks_treatment,
        "sleep_hours": sleep_hours,
        "physical_activity_days": physical_activity_days,
        "depression_score": phq9_total,
        "anxiety_score": gad7_total,
        "productivity_score": pss10_total,
        "social_support_score": msp_total
    }])

    try:
        model = joblib.load("best_pipeline_XGBoost.pkl")
    except Exception:
        st.error("Could not load model file 'best_pipeline_XGBoost.pkl'. Place it in the same folder as this app.")
        st.stop()

    label_map = {0: "Low", 1: "Medium", 2: "High"}

    # Recommendations dictionary
    recommendations = {
        "Low": {
            "message": "Your mental health looks stable. Take some time to relax and enjoy life!",
            "books": ["The Alchemist by Paulo Coelho", "Atomic Habits by James Clear"],
            "movies": ["Inside Out", "Forrest Gump"],
            "activities": ["Meditation", "Daily journaling", "Light exercise"],
            "online_doctor": None
        },
        "Medium": {
            "message": "Your stress/anxiety levels are moderate. Consider self-care and supportive resources.",
            "books": ["Feeling Good by David D. Burns", "The Happiness Project by Gretchen Rubin"],
            "movies": ["Eat Pray Love", "The Pursuit of Happyness"],
            "activities": ["Mindfulness exercises", "Yoga", "Talking to friends/family"],
            "online_doctor": "https://www.betterhelp.com/"
        },
        "High": {
            "message": "Your risk is high. Immediate support is recommended.",
            "books": ["Lost Connections by Johann Hari"],
            "movies": ["Silver Linings Playbook", "A Beautiful Mind"],
            "activities": ["Seek professional help immediately", "Avoid isolation"],
            "online_doctor": "https://www.betterhelp.com/"
        }
    }

    if st.button("🔮 Mind Check"):
        try:
            pred_class = model.predict(input_df)[0]
            risk_label = label_map.get(int(pred_class), str(pred_class))
            st.success(f"Predicted Risk (ML): **{risk_label}**")
            
            # Display Probabilities
            try:
                proba = model.predict_proba(input_df)[0]
                st.write("### 📊 Prediction Probabilities")
                for cls, p in zip(getattr(model, "classes_", [0,1,2]), proba):
                    st.write(f"**{label_map.get(int(cls), str(cls))}** → {p*100:.2f}%")
            except Exception:
                st.info("Model does not expose class probabilities.")

            # Personalized Recommendations
            rec = recommendations.get(risk_label)
            if rec:
                st.markdown("---")
                st.header("💡 Personalized Recommendations")
                st.write(rec["message"])
                
                # Display in columns
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.subheader("📚 Books")
                    for b in rec["books"]:
                        st.write(f"- {b}")
                with col2:
                    st.subheader("🎬 Movies")
                    for m in rec["movies"]:
                        st.write(f"- {m}")
                with col3:
                    st.subheader("🏃 Activities")
                    for a in rec["activities"]:
                        st.write(f"- {a}")
                
                if rec["online_doctor"]:
                    st.markdown(f"**Online Help:** [Click here]({rec['online_doctor']})")
        
        except Exception as e:
            st.error(f"Prediction failed: {e}")


# ---------------- Combined Summary ----------------
st.markdown("---")
st.header("🧾 Combined Summary")
questionnaire_risk = calculate_overall_risk(phq9_total, gad7_total, pss10_total)
st.write(f"• Questionnaire-based Overall Risk: **{questionnaire_risk}**")
st.write(f"• PHQ-9: **{phq9_total}/27** ({phq9_severity(phq9_total)})")
st.write(f"• GAD-7: **{gad7_total}/21** ({gad7_severity(gad7_total)})")
st.write(f"• PSS-10: **{pss10_total}/40** ({pss10_severity(pss10_total)})")
st.write(f"• MSPSS: **{msp_total}/95** (Average: {msp_total/len(msp_questions):.2f})")
st.caption("ML model uses demographics + lifestyle + PHQ-9 + GAD-7 + PSS-10 + MSPSS for prediction.")

