import streamlit as st
from textblob import TextBlob
import pandas as pd
import google.generativeai as genai


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="EmoCare | AI Mental Health Support",
    page_icon="💙",
    layout="wide"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

/* Main application background */
.stApp {
    background: linear-gradient(135deg, #0f172a, #111827);
}

/* Main content width */
.block-container {
    max-width: 900px;
    padding-top: 2rem;
    padding-bottom: 5rem;
}

/* Main title */
.main-title {
    text-align: center;
    font-size: 48px;
    font-weight: 700;
    margin-bottom: 5px;
}

/* Subtitle */
.subtitle {
    text-align: center;
    color: #9ca3af;
    font-size: 17px;
    margin-bottom: 30px;
}

/* Welcome card */
.welcome-card {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 22px;
    margin-bottom: 25px;
    text-align: center;
}

.welcome-card h3 {
    margin-bottom: 8px;
}

.welcome-card p {
    color: #b8bec9;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #111827;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background-color: rgba(255, 255, 255, 0.04);
    border-radius: 15px;
    padding: 10px;
    margin-bottom: 10px;
}

/* Disclaimer */
.disclaimer {
    background-color: rgba(255, 193, 7, 0.08);
    border-left: 4px solid #fbbf24;
    padding: 14px;
    border-radius: 8px;
    font-size: 13px;
    margin-top: 30px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# GEMINI API CONFIGURATION
# =========================================================

genai.configure(
    api_key=st.secrets["GEMINI_API_KEY"]
)

# IMPORTANT:
# Keep the Gemini model name that works with your API key.
model = genai.GenerativeModel(
    "gemini-3.1-flash-lite"
)


# =========================================================
# GENERATE AI RESPONSE
# =========================================================

def generate_response(prompt):

    try:

        response = model.generate_content(
            f"""
            You are EmoCare, a compassionate AI mental health
            support assistant.

            Your role is to listen to users and provide
            empathetic, supportive, and encouraging responses.

            Keep your responses conversational, warm,
            and easy to understand.

            Important rules:

            - Do not diagnose mental health conditions.
            - Do not prescribe medication.
            - Do not claim to replace a therapist or doctor.
            - Encourage professional help when appropriate.
            - If a user appears to be in immediate danger or
              expresses thoughts of self-harm, encourage them
              to contact local emergency services or a crisis
              support service immediately.

            User message:

            {prompt}
            """
        )

        return response.text

    except Exception as e:

        return f"Sorry, I encountered an error: {e}"


# =========================================================
# SENTIMENT ANALYSIS
# =========================================================

def analyze_sentiment(text):

    analysis = TextBlob(text)

    polarity = analysis.sentiment.polarity

    if polarity > 0.5:

        return "Very Positive", polarity

    elif polarity > 0.1:

        return "Positive", polarity

    elif polarity >= -0.1:

        return "Neutral", polarity

    elif polarity > -0.5:

        return "Negative", polarity

    else:

        return "Very Negative", polarity


# =========================================================
# COPING STRATEGIES
# =========================================================

def provide_coping_strategy(sentiment):

    strategies = {

        "Very Positive":
            "🌟 You're feeling great! Consider writing down "
            "what made today positive.",

        "Positive":
            "😊 Keep doing the things that are helping you "
            "feel good.",

        "Neutral":
            "🌿 Consider doing something you enjoy, such as "
            "listening to music, journaling, or taking a short walk.",

        "Negative":
            "💙 Consider taking a short break, breathing slowly, "
            "or talking with someone you trust.",

        "Very Negative":
            "🤝 Consider reaching out to someone you trust or "
            "speaking with a qualified mental health professional."
    }

    return strategies.get(
        sentiment,
        "🌿 Take things one step at a time."
    )


# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:

    st.session_state.messages = [

        {
            "role": "assistant",
            "content":
                "Hi! I'm EmoCare 💙. I'm here to listen and "
                "support you. How are you feeling today?"
        }

    ]


if "mood_tracker" not in st.session_state:

    st.session_state.mood_tracker = []


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title("💙 EmoCare")

    st.caption(
        "Your AI-powered emotional support companion"
    )

    st.divider()


    # =====================================================
    # MOOD TRACKER
    # =====================================================

    st.subheader("📊 Mood Tracker")


    if st.session_state.mood_tracker:

        # Convert stored mood data into DataFrame

        mood_data = pd.DataFrame(

            st.session_state.mood_tracker,

            columns=[
                "Message",
                "Sentiment",
                "Polarity"
            ]

        )


        # Create message numbers for X-axis

        mood_data["Message Number"] = range(
            1,
            len(mood_data) + 1
        )


        # Display mood graph

        st.line_chart(

            mood_data,

            x="Message Number",

            y="Polarity"

        )


        # Display latest mood

        latest_sentiment = mood_data.iloc[-1][
            "Sentiment"
        ]


        st.write(
            f"Current mood: **{latest_sentiment}**"
        )


        # Display polarity score

        latest_polarity = mood_data.iloc[-1][
            "Polarity"
        ]


        st.write(
            f"Sentiment score: **{latest_polarity:.2f}**"
        )


    else:

        st.info(
            "Start chatting to track your mood."
        )


    st.divider()


    # =====================================================
    # SUPPORT RESOURCES
    # =====================================================

    st.subheader(
        "🆘 Support Resources"
    )


    st.write(
        "If you are in immediate danger, contact your "
        "local emergency services."
    )


    st.write(
        "You can also reach out to a trusted friend, "
        "family member, counselor, or qualified mental "
        "health professional."
    )


    st.divider()


    # =====================================================
    # CLEAR CONVERSATION BUTTON
    # =====================================================

    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True
    ):

        # Reset chat

        st.session_state.messages = [

            {
                "role": "assistant",
                "content":
                    "Hi! I'm EmoCare 💙. I'm here to listen. "
                    "How are you feeling today?"
            }

        ]


        # Reset graph

        st.session_state.mood_tracker = []


        st.rerun()


# =========================================================
# MAIN HEADER
# =========================================================

st.markdown(
    """

    <div class="main-title">
        💙 EmoCare
    </div>

    <div class="subtitle">
        Your AI companion for emotional support and mental wellness
    </div>

    """,

    unsafe_allow_html=True
)


# =========================================================
# WELCOME CARD
# =========================================================

if len(st.session_state.messages) == 1:

    st.markdown(
        """

        <div class="welcome-card">

            <h3>
                A safe space to share how you feel 🌿
            </h3>

            <p>
                Talk about what's on your mind.
                EmoCare will listen and provide
                supportive and thoughtful responses.
            </p>

        </div>

        """,

        unsafe_allow_html=True
    )


# =========================================================
# DISPLAY CHAT HISTORY
# =========================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# =========================================================
# CHAT INPUT
# =========================================================

user_message = st.chat_input(
    "Tell me how you're feeling..."
)


# =========================================================
# PROCESS USER MESSAGE
# =========================================================

if user_message:


    # -----------------------------------------------------
    # STORE USER MESSAGE
    # -----------------------------------------------------

    st.session_state.messages.append(

        {
            "role": "user",
            "content": user_message
        }

    )


    # -----------------------------------------------------
    # DISPLAY USER MESSAGE
    # -----------------------------------------------------

    with st.chat_message(
        "user"
    ):

        st.markdown(
            user_message
        )


    # -----------------------------------------------------
    # ANALYZE SENTIMENT
    # -----------------------------------------------------

    sentiment, polarity = analyze_sentiment(
        user_message
    )


    # -----------------------------------------------------
    # STORE SENTIMENT FOR MOOD GRAPH
    # -----------------------------------------------------

    st.session_state.mood_tracker.append(

        (
            user_message,
            sentiment,
            polarity
        )

    )


    # -----------------------------------------------------
    # GENERATE AI RESPONSE
    # -----------------------------------------------------

    with st.chat_message(
        "assistant"
    ):


        with st.spinner(
            "EmoCare is thinking..."
        ):


            response = generate_response(
                user_message
            )


        # Display AI response

        st.markdown(
            response
        )


        # Generate coping strategy

        coping_strategy = provide_coping_strategy(
            sentiment
        )


        # Display wellness suggestion

        st.info(
            f"💡 **Wellness suggestion:** "
            f"{coping_strategy}"
        )


    # -----------------------------------------------------
    # STORE AI RESPONSE
    # -----------------------------------------------------

    st.session_state.messages.append(

        {
            "role": "assistant",
            "content": response
        }

    )


    # Rerun so sidebar mood graph updates immediately

    st.rerun()


# =========================================================
# DISCLAIMER
# =========================================================

st.markdown(
    """

    <div class="disclaimer">

        ⚠️ <b>Important:</b>

        EmoCare is an AI-based emotional support tool
        and is not a substitute for professional mental
        health care, diagnosis, or treatment.

        If you are experiencing an emergency or are in
        immediate danger, contact your local emergency
        services.

    </div>

    """,

    unsafe_allow_html=True
)
