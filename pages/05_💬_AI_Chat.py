"""AI Chat Assistant - Natural language interface for daycare queries"""

import streamlit as st
from app.utils.auth import require_auth, get_current_user
from app.database import get_db
from app.database.models import ChatHistory, Child, Photo, Activity
from app.services.llm import get_llm_service
from datetime import datetime, timedelta
import uuid
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from app.utils.ui_theme import apply_professional_theme

st.set_page_config(page_title="AI Chat Assistant", page_icon="💬", layout="wide")

# Apply professional theme
apply_professional_theme()

# Require authentication (all roles can use chat)
require_auth(['parent', 'staff', 'admin'])
user = get_current_user()

st.title("💬 AI Chat Assistant")
st.write("Ask me anything about your daycare, children, photos, or activities!")

# Initialize chat history in session state
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []

# Initialize LLM service
try:
    llm_service = get_llm_service()
except Exception as e:
    st.error(f"⚠️ AI Chat is not configured: {str(e)}")
    st.info("""
    **To enable AI Chat, configure an LLM provider in your `.env` file:**

    **Option 1: OpenAI**
    ```
    LLM_PROVIDER=openai
    OPENAI_API_KEY=sk-your-key-here
    ```

    **Option 2: Gemini**
    ```
    LLM_PROVIDER=gemini
    GEMINI_API_KEY=your-key-here
    ```

    **Option 3: Local Ollama**
    ```
    LLM_PROVIDER=ollama
    ```

    Then restart the application.
    """)
    st.stop()

# System prompt based on user role
def get_system_prompt():
    """Generate context-aware system prompt"""

    with get_db() as db:
        if user.role.value == 'parent':
            # Get parent's children
            children = db.query(Child).filter(Child.parent_id == user.id).all()
            child_names = ", ".join([f"{c.first_name}" for c in children]) if children else "none"

            context = f"""You are a helpful AI assistant for a daycare photo-sharing platform.
You're assisting a parent named {user.first_name}.

Their children: {child_names}

You can help with:
- Viewing recent photos and activities
- Understanding their child's daily routine
- Answering questions about meals, naps, and activities
- Finding specific photos or moments
- Explaining daycare policies and procedures

Be warm, friendly, and supportive. Focus on their children's wellbeing and development."""

        elif user.role.value == 'staff':
            context = f"""You are a helpful AI assistant for daycare staff.
You're assisting {user.first_name}, a staff member.

You can help with:
- Logging activities efficiently
- Best practices for photo documentation
- Child development insights
- Activity ideas and suggestions
- Administrative tasks guidance

Be professional, efficient, and supportive of their work."""

        else:  # admin
            context = f"""You are a helpful AI assistant for daycare administrators.
You're assisting {user.first_name}, an administrator.

You can help with:
- User management and permissions
- Analytics and reporting
- System configuration
- Billing and subscription questions
- Best practices for daycare operations

Be professional, detailed, and solution-oriented."""

    return context

# Helper function to generate activity charts
def generate_activity_charts(query_lower: str):
    """Generate interactive Plotly charts for activity data"""
    with get_db() as db:
        if user.role.value == 'parent':
            children = db.query(Child).filter(Child.parent_id == user.id).all()
            child_ids = [c.id for c in children]
        else:
            # For staff/admin, get all children in their daycare
            children = db.query(Child).filter(Child.daycare_id == user.daycare_id).all()
            child_ids = [c.id for c in children]

        if not child_ids:
            return

        # Get activities from the last 7 days
        week_ago = datetime.now() - timedelta(days=7)
        activities = db.query(Activity).filter(
            Activity.child_id.in_(child_ids),
            Activity.activity_time >= week_ago
        ).all()

        if not activities:
            st.info("No activity data available for the last 7 days.")
            return

        # Prepare data for charts
        activity_data = []
        for act in activities:
            child = next((c for c in children if c.id == act.child_id), None)
            activity_data.append({
                'activity_type': act.activity_type,
                'child_name': child.first_name if child else "Unknown",
                'activity_time': act.activity_time,
                'duration': act.duration_minutes or 0,
                'mood': act.mood or 'N/A'
            })

        df = pd.DataFrame(activity_data)

        if df.empty:
            st.info("No activity data to display.")
            return

        # Create two columns for charts
        col1, col2 = st.columns(2)

        with col1:
            # Pie chart - Activity distribution
            activity_counts = df['activity_type'].value_counts()
            fig_pie = px.pie(
                values=activity_counts.values,
                names=activity_counts.index,
                title='Activity Distribution (Last 7 Days)',
                color_discrete_sequence=px.colors.sequential.Purples_r
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie.update_layout(
                showlegend=True,
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with col2:
            # Bar chart - Activities by type
            activity_type_counts = df.groupby('activity_type').size().reset_index(name='count')
            fig_bar = px.bar(
                activity_type_counts,
                x='activity_type',
                y='count',
                title='Activities by Type',
                color='count',
                color_continuous_scale='Purples'
            )
            fig_bar.update_layout(
                xaxis_title='Activity Type',
                yaxis_title='Count',
                showlegend=False,
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        # Additional time-based chart
        st.markdown("### Activity Timeline")
        df['date'] = pd.to_datetime(df['activity_time']).dt.date
        daily_counts = df.groupby(['date', 'activity_type']).size().reset_index(name='count')

        fig_timeline = px.bar(
            daily_counts,
            x='date',
            y='count',
            color='activity_type',
            title='Daily Activity Breakdown',
            color_discrete_sequence=px.colors.sequential.Purples_r
        )
        fig_timeline.update_layout(
            xaxis_title='Date',
            yaxis_title='Number of Activities',
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_timeline, use_container_width=True)


# Helper function to display photos in grid
def display_photo_grid(query_lower: str):
    """Display photos in a 3-column grid"""
    with get_db() as db:
        if user.role.value == 'parent':
            children = db.query(Child).filter(Child.parent_id == user.id).all()
            child_ids = [c.id for c in children]
        else:
            # For staff/admin, get all children in their daycare
            children = db.query(Child).filter(Child.daycare_id == user.daycare_id).all()
            child_ids = [c.id for c in children]

        if not child_ids:
            return

        # Get recent photos
        recent_photos = db.query(Photo).filter(
            Photo.child_id.in_(child_ids),
            Photo.is_deleted == False
        ).order_by(Photo.uploaded_at.desc()).limit(12).all()

        if not recent_photos:
            st.info("No photos available to display.")
            return

        st.markdown("### Recent Photos")

        # Create 3-column grid
        cols_per_row = 3
        for i in range(0, len(recent_photos), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, col in enumerate(cols):
                idx = i + j
                if idx < len(recent_photos):
                    photo = recent_photos[idx]
                    child = next((c for c in children if c.id == photo.child_id), None)
                    child_name = child.first_name if child else "Unknown"

                    with col:
                        # Display photo
                        try:
                            st.image(
                                photo.url,
                                caption=f"{child_name} - {photo.captured_at.strftime('%b %d, %Y')}",
                                use_container_width=True
                            )
                            if photo.caption:
                                st.caption(photo.caption)
                        except Exception as e:
                            st.error(f"Error loading photo: {str(e)}")


# Helper function to get relevant context from database
def get_conversation_context(query: str):
    """Get relevant data from database based on query"""

    context_data = []
    query_lower = query.lower()

    with get_db() as db:
        # Check if query is about photos
        if any(word in query_lower for word in ['photo', 'picture', 'image', 'pic']):
            if user.role.value == 'parent':
                children = db.query(Child).filter(Child.parent_id == user.id).all()
                child_ids = [c.id for c in children]

                recent_photos = db.query(Photo).filter(
                    Photo.child_id.in_(child_ids)
                ).order_by(Photo.uploaded_at.desc()).limit(5).all()

                if recent_photos:
                    context_data.append(f"Recent photos: {len(recent_photos)} photos in the last few days")

        # Check if query is about activities
        if any(word in query_lower for word in ['activity', 'activities', 'meal', 'nap', 'play']):
            if user.role.value == 'parent':
                children = db.query(Child).filter(Child.parent_id == user.id).all()
                child_ids = [c.id for c in children]

                recent_activities = db.query(Activity).filter(
                    Activity.child_id.in_(child_ids)
                ).order_by(Activity.activity_time.desc()).limit(5).all()

                if recent_activities:
                    activity_summary = []
                    for act in recent_activities:
                        child = next((c for c in children if c.id == act.child_id), None)
                        child_name = child.first_name if child else "Unknown"
                        activity_summary.append(
                            f"{act.activity_type} for {child_name} at {act.activity_time.strftime('%I:%M %p')}"
                        )
                    context_data.append("Recent activities:\n" + "\n".join(activity_summary))

        # Check if query is about today
        if 'today' in query_lower:
            today = datetime.now().date()

            if user.role.value == 'parent':
                children = db.query(Child).filter(Child.parent_id == user.id).all()
                child_ids = [c.id for c in children]

                today_activities = db.query(Activity).filter(
                    Activity.child_id.in_(child_ids),
                    Activity.activity_time >= datetime.combine(today, datetime.min.time())
                ).all()

                if today_activities:
                    context_data.append(f"Today's activities: {len(today_activities)} activities logged")

    return "\n".join(context_data) if context_data else ""

# Display chat history
for message in st.session_state.chat_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me anything..."):
    # Add user message to chat
    st.session_state.chat_messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # Get conversation context from database
    db_context = get_conversation_context(prompt)

    # Prepare messages for LLM
    system_prompt = get_system_prompt()

    if db_context:
        system_prompt += f"\n\nCurrent context:\n{db_context}"

    messages = [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.chat_messages]

    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = llm_service.chat(
                    messages=messages,
                    system_prompt=system_prompt,
                    temperature=0.7
                )

                st.markdown(response)

                # Check if query requires charts or photos
                query_lower = prompt.lower()

                # Generate charts if query is about statistics or activities
                if any(word in query_lower for word in ['chart', 'statistics', 'activity', 'stat', 'graph', 'data']):
                    st.markdown("---")
                    st.markdown("### Activity Statistics")
                    generate_activity_charts(query_lower)

                # Display photos if query is about photos
                if any(word in query_lower for word in ['photo', 'picture', 'image', 'pic']):
                    st.markdown("---")
                    display_photo_grid(query_lower)

                # Add assistant response to chat
                st.session_state.chat_messages.append({"role": "assistant", "content": response})

                # Save to database
                try:
                    with get_db() as db:
                        chat_entry = ChatHistory(
                            id=str(uuid.uuid4()),
                            user_id=user.id,
                            daycare_id=user.daycare_id,
                            message=prompt,
                            response=response,
                            created_at=datetime.utcnow()
                        )
                        db.add(chat_entry)
                        db.commit()
                except Exception as db_err:
                    # Log error but don't crash - chat still works
                    pass

            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("Please check your LLM provider configuration in the .env file")

# Sidebar with suggestions and history
with st.sidebar:
    st.header("💡 Suggested Questions")

    if user.role.value == 'parent':
        suggestions = [
            "What photos were uploaded today?",
            "What activities did my child do?",
            "Did my child have a good nap?",
            "What did my child eat for lunch?",
            "Show me this week's highlights"
        ]
    elif user.role.value == 'staff':
        suggestions = [
            "What activities should I log?",
            "Best practices for photo documentation",
            "Activity ideas for toddlers",
            "How to handle allergies?",
            "Daily routine suggestions"
        ]
    else:  # admin
        suggestions = [
            "Show me this month's statistics",
            "How many users are active?",
            "What's our photo upload trend?",
            "Subscription management tips",
            "User engagement insights"
        ]

    for suggestion in suggestions:
        if st.button(suggestion, key=f"suggest_{suggestion}", use_container_width=True):
            # Simulate clicking the suggestion
            st.session_state.chat_messages.append({"role": "user", "content": suggestion})
            st.rerun()

    st.divider()

    # Clear chat button
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_messages = []
        st.rerun()

    st.divider()

    # Chat history
    st.header("📜 Recent Chats")

    with get_db() as db:
        recent_chats_db = db.query(ChatHistory).filter(
            ChatHistory.user_id == user.id
        ).order_by(ChatHistory.created_at.desc()).limit(5).all()

        # Extract within session
        recent_chats = [{
            'message': chat.message,
            'response': chat.response,
            'created_at': chat.created_at
        } for chat in recent_chats_db]

    if recent_chats:
        for chat in recent_chats:
            with st.expander(f"{chat['message'][:30]}...", expanded=False):
                st.caption(chat['created_at'].strftime("%b %d, %I:%M %p"))
                st.write(f"**Q:** {chat['message']}")
                st.write(f"**A:** {chat['response']}")
    else:
        st.info("No chat history yet")

# Features info
st.divider()

with st.expander("ℹ️ How to use the AI Chat Assistant"):
    st.markdown("""
    ### What can I ask?

    **For Parents:**
    - "What did my child do today?"
    - "Show me recent photos"
    - "Did my child eat well?"
    - "How was nap time?"

    **For Staff:**
    - "Activity ideas for 2-year-olds"
    - "Best practices for meal time"
    - "How to document activities?"

    **For Admins:**
    - "Show me usage statistics"
    - "How many photos this week?"
    - "User engagement trends"

    ### Features:
    - Natural language understanding
    - Context-aware responses
    - Access to your daycare data
    - Personalized suggestions
    - Chat history

    ### Tips:
    - Be specific in your questions
    - You can ask follow-up questions
    - Use the suggested questions to get started
    """)

# LLM provider info - Removed for cleaner UI
