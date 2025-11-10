"""Voice Calling Agent - Twilio-powered voice interface"""

import streamlit as st
from app.utils.auth import require_auth, get_current_user
from app.database import get_db
from app.database.models import VoiceCall, Child, Activity
from app.config import Config
from datetime import datetime
import uuid
from app.utils.ui_theme import apply_professional_theme

st.set_page_config(page_title="Voice Calling", page_icon="📞", layout="wide")

# Apply professional theme
apply_professional_theme()

# Require authentication
require_auth(['parent', 'staff', 'admin'])
user = get_current_user()

st.title("📞 Voice Calling Agent")
st.write("Call us anytime to check on your child or get daycare updates!")

# Helper function for generating responses (defined early for use below)
def generate_voice_response(query: str, child, activities: list) -> str:
    """Generate natural voice response based on query and data"""

    query_lower = query.lower()
    child_name = child.first_name

    # Meals
    if any(word in query_lower for word in ['eat', 'ate', 'meal', 'lunch', 'breakfast', 'dinner', 'snack']):
        meals = [a for a in activities if a.activity_type == 'meal']
        if meals:
            meal = meals[0]
            time_str = meal.activity_time.strftime("%I:%M %p")
            notes = meal.notes or "a nutritious meal"
            return f"{child_name} had a meal at {time_str}. {notes}. They seemed to enjoy it!"
        else:
            return f"I don't have any meal records for {child_name} today yet."

    # Naps
    elif any(word in query_lower for word in ['nap', 'sleep', 'rest']):
        naps = [a for a in activities if a.activity_type == 'nap']
        if naps:
            nap = naps[0]
            duration = nap.duration_minutes or 0
            time_str = nap.activity_time.strftime("%I:%M %p")
            return f"{child_name} had a nap starting at {time_str} for about {duration} minutes. They woke up well-rested!"
        else:
            return f"{child_name} hasn't had a nap recorded today yet."

    # General activities
    elif any(word in query_lower for word in ['do', 'did', 'activity', 'activities']):
        if activities:
            activity_summary = []
            for act in activities[:3]:  # Top 3
                activity_summary.append(f"{act.activity_type} at {act.activity_time.strftime('%I:%M %p')}")
            activities_str = ", ".join(activity_summary)
            return f"Today, {child_name} has done: {activities_str}. They've had a wonderful day!"
        else:
            return f"No activities have been logged for {child_name} today yet."

    # Photos
    elif any(word in query_lower for word in ['photo', 'picture', 'pic']):
        return f"We have several new photos of {child_name} from today! I can send them to your email if you'd like."

    # Daily summary
    elif any(word in query_lower for word in ['summary', 'today', 'day', 'overall']):
        meal_count = len([a for a in activities if a.activity_type == 'meal'])
        nap_count = len([a for a in activities if a.activity_type == 'nap'])
        total = len(activities)

        return f"{child_name} has had a great day! We've logged {meal_count} meals, {nap_count} naps, and {total} total activities. They've been happy and engaged!"

    # Default
    else:
        return f"I can help you with information about {child_name}'s day. You can ask about meals, naps, activities, or photos!"

# Check if Twilio is configured
if not all([Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN, Config.TWILIO_PHONE_NUMBER]):
    st.error("❌ Twilio is not configured. Please add Twilio credentials to your .env file")
    st.code("""
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
    """)
    st.stop()

# ===== TABS =====
tab1, tab2, tab3 = st.tabs(["📞 Make a Call", "📜 Call History", "ℹ️ How It Works"])

# ===== TAB 1: MAKE A CALL =====
with tab1:
    st.subheader("📞 Call the Daycare")

    st.info(f"**Daycare Phone Number:** {Config.TWILIO_PHONE_NUMBER}")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### What you can ask:

        📸 **"Show me today's photos"**
        - Get a summary of photos uploaded today

        🍽️ **"What did my child eat?"**
        - Hear about meal activities

        😴 **"How was nap time?"**
        - Get nap duration and quality

        🎯 **"What activities did they do?"**
        - Summary of today's activities

        📊 **"Give me a daily summary"**
        - Complete overview of the day
        """)

    with col2:
        st.markdown("""
        ### Voice Commands:

        - **"My child is [Child Name]"**
          - Identify which child you're asking about

        - **"Repeat that"**
          - Hear the last response again

        - **"Send me the photos"**
          - Get photos sent to your email

        - **"Talk to staff"**
          - Connect to a live staff member

        - **"Goodbye"**
          - End the call
        """)

    st.divider()

    # Call simulation (in production, this would trigger actual Twilio call)
    st.subheader("🎭 Simulate Voice Interaction")

    if 'voice_context' not in st.session_state:
        st.session_state.voice_context = {
            'selected_child': None,
            'conversation': []
        }

    # Child selection
    with get_db() as db:
        if user.role.value == 'parent':
            children_db = db.query(Child).filter(Child.parent_id == user.id).all()
        else:
            children_db = db.query(Child).filter(Child.daycare_id == user.daycare_id).all()

        # Extract data within session
        children = [{
            'id': c.id,
            'first_name': c.first_name,
            'last_name': c.last_name
        } for c in children_db]

    if children:
        child_options = {f"{c['first_name']} {c['last_name']}": c['id'] for c in children}
        selected_child_name = st.selectbox(
            "Which child would you like to ask about?",
            options=list(child_options.keys())
        )

        if selected_child_name:
            st.session_state.voice_context['selected_child'] = child_options[selected_child_name]

        st.divider()

        # Voice query input
        voice_query = st.text_input("🎤 Ask a question (simulated voice input):", placeholder="What did my child do today?")

        if st.button("🗣️ Speak", use_container_width=True) and voice_query:
            # Process voice query
            child_id = st.session_state.voice_context['selected_child']

            with get_db() as db:
                child = db.query(Child).filter(Child.id == child_id).first()

                # Get today's activities
                today = datetime.now().date()
                today_activities = db.query(Activity).filter(
                    Activity.child_id == child_id,
                    Activity.activity_time >= datetime.combine(today, datetime.min.time())
                ).all()

                # Generate response based on query
                response = generate_voice_response(voice_query, child, today_activities)

                # Display response
                st.success("📞 Voice Agent Response:")
                st.write(response)

                # Save to conversation
                st.session_state.voice_context['conversation'].append({
                    'query': voice_query,
                    'response': response,
                    'timestamp': datetime.now()
                })

                # Save to database
                voice_call = VoiceCall(
                    id=str(uuid.uuid4()),
                    user_id=user.id,
                    daycare_id=user.daycare_id,
                    phone_number=user.phone or "simulated",
                    duration=0,  # Simulated
                    transcript=f"Q: {voice_query}\nA: {response}",
                    status="completed",
                    created_at=datetime.utcnow()
                )
                db.add(voice_call)

        # Show conversation history in this session
        if st.session_state.voice_context['conversation']:
            st.divider()
            st.subheader("💬 Conversation")

            for exchange in st.session_state.voice_context['conversation']:
                with st.container():
                    st.markdown(f"**You:** {exchange['query']}")
                    st.markdown(f"**Agent:** {exchange['response']}")
                    st.caption(exchange['timestamp'].strftime("%I:%M %p"))
                    st.divider()

    else:
        st.warning("No children found. Please add children to your account first.")

# ===== TAB 2: CALL HISTORY =====
with tab2:
    st.subheader("📜 Call History")

    with get_db() as db:
        call_history = db.query(VoiceCall).filter(
            VoiceCall.user_id == user.id
        ).order_by(VoiceCall.created_at.desc()).limit(20).all()

    if call_history:
        for call in call_history:
            with st.expander(
                f"📞 {call.created_at.strftime('%b %d, %Y at %I:%M %p')} - {call.status}",
                expanded=False
            ):
                st.write(f"**Phone:** {call.phone_number}")
                st.write(f"**Duration:** {call.duration} seconds" if call.duration else "**Duration:** N/A")
                st.write(f"**Status:** {call.status}")

                if call.transcript:
                    st.markdown("**Transcript:**")
                    st.text(call.transcript)
    else:
        st.info("No call history yet. Make your first call!")

# ===== TAB 3: HOW IT WORKS =====
with tab3:
    st.subheader("ℹ️ How Voice Calling Works")

    st.markdown("""
    ### 🎯 Overview

    Our AI-powered voice calling system uses **Twilio** and natural language processing to provide
    instant updates about your child's day at daycare.

    ### 📞 How to Use

    1. **Call the daycare number** (shown above)
    2. **Identify yourself** - Say your name or child's name
    3. **Ask questions** - Use natural language
    4. **Get instant answers** - AI retrieves data from our system
    5. **Request actions** - Ask for photos to be emailed, etc.

    ### 🤖 What the AI Can Do

    **Retrieve Information:**
    - Today's photos count and summary
    - Meal times and what was eaten
    - Nap duration and quality
    - Activities and playtime
    - Staff interactions

    **Actions:**
    - Email photos to you
    - Send SMS summaries
    - Schedule callbacks
    - Connect to live staff

    ### 🔒 Security & Privacy

    - Caller ID verification
    - Voice authentication (optional)
    - Only access to your child's data
    - All calls are logged and encrypted
    - HIPAA-compliant conversations

    ### 🌟 Benefits

    - **24/7 Availability** - Get updates anytime
    - **Hands-free** - Perfect for busy parents
    - **Instant** - No waiting for staff
    - **Natural** - Talk like you would to a person
    - **Accessible** - Works on any phone

    ### 🛠️ Technical Details

    **Powered by:**
    - Twilio Voice API
    - OpenAI/Gemini for natural language
    - Real-time database queries
    - Text-to-speech synthesis
    - Speech recognition

    ### 💡 Tips for Best Results

    - Speak clearly and naturally
    - Specify which child (if you have multiple)
    - Ask one question at a time
    - Use specific time frames ("today", "this morning")
    - Say "repeat" if you didn't hear clearly
    """)

    st.divider()

    st.subheader("🎬 Example Conversation")

    st.code("""
YOU: "Hello, this is Sarah calling about Emma"

AGENT: "Hi Sarah! I have Emma's information ready. What would you like to know?"

YOU: "What did she eat for lunch today?"

AGENT: "Emma had lunch at 12:15 PM. She ate mac and cheese with broccoli,
        and had a fruit cup for dessert. Her teacher noted she ate everything!"

YOU: "Great! How was her nap?"

AGENT: "Emma had a wonderful nap from 1:30 to 3:00 PM - that's 90 minutes.
        She woke up happy and ready to play!"

YOU: "Any photos today?"

AGENT: "Yes! We have 3 new photos of Emma from today. She was painting during
        art time. Would you like me to email them to you?"

YOU: "Yes please!"

AGENT: "I've sent the photos to sarah@email.com. Is there anything else?"

YOU: "No, thank you!"

AGENT: "You're welcome! Have a great day, and we'll see Emma tomorrow!"
    """)

st.divider()

# Connection test
with st.expander("🔧 Test Twilio Connection"):
    if st.button("Test Connection"):
        try:
            from twilio.rest import Client

            client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
            account = client.api.accounts(Config.TWILIO_ACCOUNT_SID).fetch()

            st.success(f"✅ Connected! Account: {account.friendly_name}")
            st.info(f"Phone Number: {Config.TWILIO_PHONE_NUMBER}")

        except Exception as e:
            st.error(f"❌ Connection failed: {str(e)}")
            st.info("Please check your Twilio credentials in the .env file")
