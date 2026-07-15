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
    max-width: 950px;
    padding-top: 2rem;
    padding-bottom: 6rem;
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

/* Chat message styling */
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

/* Footer */
.footer {
    text-align: center;
    color: #6b7280;
    font-size: 12px;
    margin-top: 25px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# GEMINI API CONFIGURATION
# =========================================================

genai.configure(
    api_key=st.secrets["GEMINI_API_KEY"]
)

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
You are EmoCare, a compassionate AI emotional support assistant.

Your role is to listen to users and provide empathetic,
supportive, thoughtful, and encouraging responses.

Keep responses conversational, warm, helpful, and concise.

Important rules:

- Do not diagnose mental health conditions.
- Do not prescribe medication.
- Do not claim to replace a therapist, psychologist, or doctor.
- Encourage professional help when appropriate.
- Do not make promises about confidentiality.
- If a user appears to be in immediate danger or expresses
  thoughts of suicide or self-harm, encourage them to contact
  local emergency services or an appropriate crisis support
  service immediately.

User message:

{prompt}
"""
        )

        return response.text

    except Exception as e:

        return (
            "I'm sorry, I'm having trouble generating a response "
            f"right now. Error: {e}"
        )


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
# COPING / WELLNESS STRATEGIES
# =========================================================

def provide_coping_strategy(sentiment):

    strategies = {

        "Very Positive":
            "🌟 You're feeling positive! Consider writing down "
            "what made you feel good today.",

        "Positive":
            "😊 Keep doing the things that are helping you feel "
            "good and connected.",

        "Neutral":
            "🌿 Consider doing something you enjoy, such as "
            "listening to music, journaling, stretching, or "
            "taking a short walk.",

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
# INITIAL SESSION STATE
# =========================================================

WELCOME_MESSAGE = (
    "Hi! I'm EmoCare 💙. I'm here to listen and support you. "
    "How are you feeling today?"
)


if "messages" not in st.session_state:

    st.session_state.messages = [
        {
            "role": "assistant",
            "content": WELCOME_MESSAGE
        }
    ]


if "mood_tracker" not in st.session_state:

    st.session_state.mood_tracker = []


# =========================================================
# FIX OLD SESSION DATA
# =========================================================
#
# This prevents the TypeError you received:
# message["role"]
#
# Your previous version stored messages as tuples.
# The new version stores messages as dictionaries.
#
# If old data is detected, the conversation is safely reset.
# =========================================================

valid_messages = True

if not isinstance(st.session_state.messages, list):

    valid_messages = False

else:

    for message in st.session_state.messages:

        if not isinstance(message, dict):

            valid_messages = False
            break

        if "role" not in message or "content" not in message:

            valid_messages = False
            break


if not valid_messages:

    st.session_state.messages = [
        {
            "role": "assistant",
            "content": WELCOME_MESSAGE
        }
    ]


# =========================================================
# FIX OLD MOOD TRACKER DATA
# =========================================================

if not isinstance(st.session_state.mood_tracker, list):

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

        try:

            # Convert mood history into DataFrame

            mood_data = pd.DataFrame(
                st.session_state.mood_tracker,
                columns=[
                    "Message",
                    "Sentiment",
                    "Polarity"
                ]
            )


            # Make sure polarity values are numeric

            mood_data["Polarity"] = pd.to_numeric(
                mood_data["Polarity"],
                errors="coerce"
            )


            # Remove invalid values

            mood_data = mood_data.dropna(
                subset=["Polarity"]
            )


            # Add sequential message numbers

            mood_data["Message Number"] = range(
                1,
                len(mood_data) + 1
            )


            if not mood_data.empty:

                # Mood trend graph

                st.line_chart(
                    mood_data,
                    x="Message Number",
                    y="Polarity",
                    use_container_width=True
                )


                # Latest sentiment

                latest_sentiment = mood_data.iloc[-1][
                    "Sentiment"
                ]


                latest_polarity = mood_data.iloc[-1][
                    "Polarity"
                ]


                st.write(
                    f"Current mood: **{latest_sentiment}**"
                )


                st.write(
                    f"Sentiment score: **{latest_polarity:.2f}**"
                )


                st.caption(
                    "Score range: -1 (negative) to +1 (positive)"
                )


            else:

                st.info(
                    "No valid mood data available yet."
                )


        except Exception:

            st.info(
                "Start a new conversation to track your mood."
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
        "If you are in immediate danger, contact your local "
        "emergency services."
    )


    st.write(
        "You can also reach out to a trusted friend, family "
        "member, counselor, or qualified mental health professional."
    )


    st.divider()


    # =====================================================
    # CLEAR CONVERSATION
    # =====================================================

    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True
    ):

        # Reset messages

        st.session_state.messages = [
            {
                "role": "assistant",
                "content": WELCOME_MESSAGE
            }
        ]


        # Reset mood tracker and graph

        st.session_state.mood_tracker = []


        # Refresh application

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
                EmoCare will listen and provide supportive
                and thoughtful responses.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# DISPLAY EXISTING CHAT HISTORY
# =========================================================

for message in st.session_state.messages:

    # Extra safety check
    # Prevents crash if unexpected session data exists

    if (
        isinstance(message, dict)
        and "role" in message
        and "content" in message
    ):

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
# PROCESS NEW USER MESSAGE
# =========================================================

if user_message:


    # -----------------------------------------------------
    # ADD USER MESSAGE TO CHAT HISTORY
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
    # ANALYZE USER SENTIMENT
    # -----------------------------------------------------

    sentiment, polarity = analyze_sentiment(
        user_message
    )


    # -----------------------------------------------------
    # SAVE SENTIMENT TO MOOD TRACKER
    # -----------------------------------------------------

    st.session_state.mood_tracker.append(
        (
            user_message,
            sentiment,
            float(polarity)
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


        # -------------------------------------------------
        # WELLNESS SUGGESTION
        # -------------------------------------------------

        coping_strategy = provide_coping_strategy(
            sentiment
        )


        st.info(
            f"💡 **Wellness suggestion:** {coping_strategy}"
        )


    # -----------------------------------------------------
    # SAVE AI RESPONSE
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )


# =========================================================
# DISCLAIMER
# =========================================================

st.markdown(
    """
    <div class="disclaimer">

        ⚠️ <b>Important:</b>

        EmoCare is an AI-based emotional support tool and is
        not a substitute for professional mental health care,
        diagnosis, or treatment.

        If you are experiencing an emergency or are in
        immediate danger, contact your local emergency services.

    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">
        EmoCare 💙 • AI-powered emotional support
    </div>
    """,
    unsafe_allow_html=True
)
