import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from utils.data_processor import DataProcessor
from utils.analytics import Analytics

# Page configuration
st.set_page_config(
    page_title="Instagram Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None

def main():
    st.title("📊 Instagram Analytics & Content Planning Dashboard")
    st.markdown("---")
    
    # Sidebar for data upload
    with st.sidebar:
        st.header("📁 Data Upload")
        uploaded_file = st.file_uploader(
            "Upload your Instagram data CSV",
            type=['csv'],
            help="Upload a CSV file containing your Instagram post data with columns: date, likes, comments, reach, impressions, post_type, hashtags"
        )
        
        if uploaded_file is not None:
            try:
                # Load and validate data
                data = pd.read_csv(uploaded_file)
                processor = DataProcessor()
                
                if processor.validate_data(data):
                    st.session_state.data = data
                    st.session_state.processed_data = processor.process_data(data)
                    st.success("✅ Data uploaded successfully!")
                    
                    # Display data info
                    st.info(f"📈 {len(data)} posts loaded")
                    st.info(f"📅 Date range: {data['date'].min()} to {data['date'].max()}")
                else:
                    st.error("❌ Invalid data format. Please check your CSV file.")
            except Exception as e:
                st.error(f"❌ Error loading data: {str(e)}")
    
    # Main content area
    if st.session_state.processed_data is not None:
        display_overview()
    else:
        display_welcome()

def display_welcome():
    """Display welcome message when no data is uploaded"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        ## Welcome to Your Instagram Analytics Dashboard! 🎉
        
        ### Get Started:
        1. **Upload your data** using the file uploader in the sidebar
        2. **Explore analytics** across different pages
        3. **Plan content** using the calendar feature
        4. **Track ideas** and hashtag suggestions
        5. **Export reports** for your team
        
        ### Required CSV Format:
        Your CSV should include these columns:
        - `date`: Post date (YYYY-MM-DD)
        - `likes`: Number of likes
        - `comments`: Number of comments  
        - `reach`: Post reach
        - `impressions`: Post impressions
        - `post_type`: Type of post (photo, video, carousel)
        - `hashtags`: Hashtags used (optional)
        
        ### Features:
        - 📊 **Analytics**: Key metrics and performance trends
        - 📅 **Content Calendar**: Plan and schedule posts
        - 💡 **Content Ideas**: Track ideas with hashtag suggestions
        - 📈 **Reports**: Export data and insights
        """)

def display_overview():
    """Display overview metrics and charts"""
    data = st.session_state.processed_data
    analytics = Analytics(data)
    
    # Key metrics row
    st.subheader("📊 Key Performance Metrics")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_posts = len(data)
        st.metric("Total Posts", f"{total_posts:,}")
    
    with col2:
        total_likes = data['likes'].sum()
        st.metric("Total Likes", f"{total_likes:,}")
    
    with col3:
        total_comments = data['comments'].sum()
        st.metric("Total Comments", f"{total_comments:,}")
    
    with col4:
        avg_engagement = analytics.calculate_engagement_rate()
        st.metric("Avg Engagement", f"{avg_engagement:.2f}%")
    
    with col5:
        total_reach = data['reach'].sum()
        st.metric("Total Reach", f"{total_reach:,}")
    
    st.markdown("---")
    
    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Engagement Over Time")
        engagement_chart = analytics.create_engagement_timeline()
        st.plotly_chart(engagement_chart, use_container_width=True)
    
    with col2:
        st.subheader("📊 Post Type Performance")
        post_type_chart = analytics.create_post_type_analysis()
        st.plotly_chart(post_type_chart, use_container_width=True)
    
    # Additional insights
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⏰ Best Posting Times")
        optimal_times = analytics.find_optimal_posting_times()
        
        for day, times in optimal_times.items():
            st.write(f"**{day}:** {', '.join(times)}")
    
    with col2:
        st.subheader("🔝 Top Performing Posts")
        top_posts = analytics.get_top_posts()
        
        for idx, (_, post) in enumerate(top_posts.iterrows(), 1):
            engagement = (post['likes'] + post['comments']) / post['reach'] * 100 if post['reach'] > 0 else 0
            st.write(f"{idx}. **{post['date']}** - {engagement:.1f}% engagement ({post['likes']} likes, {post['comments']} comments)")
    
    st.markdown("---")
    
    # Navigation info
    st.info("""
    🧭 **Explore More:**
    - **📊 Analytics**: Detailed performance analysis and trends
    - **📅 Content Calendar**: Plan and schedule your upcoming posts
    - **💡 Content Ideas**: Track ideas and get hashtag suggestions
    - **📈 Reports**: Export detailed reports and insights
    """)

if __name__ == "__main__":
    main()
