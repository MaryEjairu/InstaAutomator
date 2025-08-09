import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import calendar
from utils.content_planner import ContentPlanner

st.set_page_config(page_title="Content Calendar", page_icon="📅", layout="wide")

def main():
    st.title("📅 Content Calendar & Planning")
    
    planner = ContentPlanner()
    
    # Sidebar for calendar controls
    with st.sidebar:
        st.header("📅 Calendar Controls")
        
        # Month selector
        current_date = datetime.now()
        selected_month = st.selectbox(
            "Select Month",
            options=list(range(1, 13)),
            index=current_date.month - 1,
            format_func=lambda x: calendar.month_name[x]
        )
        
        selected_year = st.selectbox(
            "Select Year",
            options=list(range(current_date.year - 1, current_date.year + 3)),
            index=1
        )
        
        st.markdown("---")
        
        # Quick stats
        st.subheader("📊 Calendar Stats")
        stats = planner.get_calendar_stats()
        
        st.metric("Total Planned Posts", stats['total_planned_posts'])
        st.metric("Upcoming (7 days)", stats['upcoming_posts_7_days'])
        st.metric("Upcoming (30 days)", stats['upcoming_posts_30_days'])
        
        if stats['content_types']:
            st.write("**Content Types:**")
            for content_type, count in stats['content_types'].items():
                st.write(f"• {content_type}: {count}")
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["📅 Calendar View", "➕ Add Content", "📋 Planned Posts"])
    
    with tab1:
        display_calendar_view(planner, selected_year, selected_month)
    
    with tab2:
        display_add_content_form(planner)
    
    with tab3:
        display_planned_posts(planner)

def display_calendar_view(planner, year, month):
    """Display the calendar view with planned content"""
    st.subheader(f"📅 {calendar.month_name[month]} {year}")
    
    # Get calendar data for the month
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
    
    calendar_items = planner.get_calendar_items(start_date, end_date)
    
    # Create calendar layout
    cal = calendar.monthcalendar(year, month)
    weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    
    # Display weekday headers
    header_cols = st.columns(7)
    for i, day in enumerate(weekdays):
        header_cols[i].write(f"**{day}**")
    
    # Display calendar days
    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            with cols[i]:
                if day == 0:
                    st.write("")
                else:
                    day_date = date(year, month, day)
                    date_str = day_date.strftime('%Y-%m-%d')
                    
                    # Check if there's content planned for this day
                    if date_str in calendar_items:
                        item = calendar_items[date_str]
                        
                        # Display day with content indicator
                        st.markdown(f"""
                        <div style="border: 2px solid #4CAF50; border-radius: 5px; padding: 5px; margin-bottom: 5px;">
                            <strong>{day}</strong><br>
                            <small>{item['content_type']}</small>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Show content preview on click
                        if st.button(f"View", key=f"view_{date_str}"):
                            st.session_state[f'show_content_{date_str}'] = True
                        
                        # Display content details if selected
                        if st.session_state.get(f'show_content_{date_str}', False):
                            with st.expander(f"📝 Content for {date_str}", expanded=True):
                                st.write(f"**Type:** {item['content_type']}")
                                st.write(f"**Caption:** {item['caption']}")
                                st.write(f"**Hashtags:** {item['hashtags']}")
                                if item['notes']:
                                    st.write(f"**Notes:** {item['notes']}")
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button("✏️ Edit", key=f"edit_{date_str}"):
                                        st.session_state[f'edit_content_{date_str}'] = True
                                with col2:
                                    if st.button("🗑️ Delete", key=f"delete_{date_str}"):
                                        planner.delete_calendar_item(date_str)
                                        st.success(f"Content for {date_str} deleted!")
                                        st.rerun()
                        
                        # Edit form
                        if st.session_state.get(f'edit_content_{date_str}', False):
                            edit_content_form(planner, date_str, item)
                    else:
                        # Display empty day
                        st.markdown(f"""
                        <div style="border: 1px solid #ddd; border-radius: 5px; padding: 5px; margin-bottom: 5px; text-align: center;">
                            {day}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Quick add button
                        if st.button(f"➕", key=f"add_{date_str}", help="Add content"):
                            st.session_state[f'quick_add_{date_str}'] = True
                        
                        # Quick add form
                        if st.session_state.get(f'quick_add_{date_str}', False):
                            quick_add_form(planner, date_str)

def edit_content_form(planner, date_str, item):
    """Display edit form for existing content"""
    st.write(f"**Editing content for {date_str}**")
    
    with st.form(f"edit_form_{date_str}"):
        content_type = st.selectbox(
            "Content Type",
            options=["photo", "video", "carousel", "story", "reel"],
            index=["photo", "video", "carousel", "story", "reel"].index(item['content_type'])
        )
        
        caption = st.text_area("Caption", value=item['caption'])
        hashtags = st.text_input("Hashtags", value=item['hashtags'])
        notes = st.text_area("Notes", value=item.get('notes', ''))
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("💾 Save Changes"):
                planner.add_calendar_item(date_str, content_type, caption, hashtags, notes)
                st.session_state[f'edit_content_{date_str}'] = False
                st.success("Content updated!")
                st.rerun()
        
        with col2:
            if st.form_submit_button("❌ Cancel"):
                st.session_state[f'edit_content_{date_str}'] = False
                st.rerun()

def quick_add_form(planner, date_str):
    """Display quick add form for new content"""
    st.write(f"**Add content for {date_str}**")
    
    with st.form(f"quick_add_form_{date_str}"):
        content_type = st.selectbox(
            "Content Type",
            options=["photo", "video", "carousel", "story", "reel"]
        )
        
        caption = st.text_area("Caption", placeholder="Enter your post caption...")
        hashtags = st.text_input("Hashtags", placeholder="#hashtag1 #hashtag2")
        notes = st.text_area("Notes", placeholder="Any additional notes...")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("➕ Add Content"):
                planner.add_calendar_item(date_str, content_type, caption, hashtags, notes)
                st.session_state[f'quick_add_{date_str}'] = False
                st.success(f"Content added for {date_str}!")
                st.rerun()
        
        with col2:
            if st.form_submit_button("❌ Cancel"):
                st.session_state[f'quick_add_{date_str}'] = False
                st.rerun()

def display_add_content_form(planner):
    """Display form to add new content"""
    st.subheader("➕ Plan New Content")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.form("add_content_form"):
            st.write("**Content Details**")
            
            post_date = st.date_input(
                "Post Date",
                value=date.today() + timedelta(days=1),
                min_value=date.today()
            )
            
            content_type = st.selectbox(
                "Content Type",
                options=["photo", "video", "carousel", "story", "reel"]
            )
            
            caption = st.text_area(
                "Caption",
                placeholder="Write your post caption here...",
                height=100
            )
            
            hashtags = st.text_input(
                "Hashtags",
                placeholder="#hashtag1 #hashtag2 #hashtag3"
            )
            
            notes = st.text_area(
                "Notes",
                placeholder="Any additional notes or reminders...",
                height=60
            )
            
            if st.form_submit_button("📅 Add to Calendar"):
                date_str = post_date.strftime('%Y-%m-%d')
                
                if date_str in st.session_state[planner.calendar_key]:
                    st.error(f"Content already planned for {date_str}. Please choose a different date.")
                else:
                    planner.add_calendar_item(date_str, content_type, caption, hashtags, notes)
                    st.success(f"Content scheduled for {date_str}!")
                    st.rerun()
    
    with col2:
        st.write("**Tips for Content Planning**")
        
        st.info("""
        📝 **Caption Tips:**
        - Start with a hook to grab attention
        - Include a call-to-action
        - Keep it authentic to your brand voice
        - Ask questions to encourage engagement
        
        🏷️ **Hashtag Tips:**
        - Use 5-10 relevant hashtags
        - Mix popular and niche hashtags
        - Research hashtags in your niche
        - Avoid banned hashtags
        
        ⏰ **Timing Tips:**
        - Post when your audience is most active
        - Consider time zones of your followers
        - Maintain consistency in posting schedule
        """)
        
        # Show optimal posting times if data is available
        if st.session_state.get('processed_data') is not None:
            from utils.analytics import Analytics
            analytics = Analytics(st.session_state.processed_data)
            optimal_times = analytics.find_optimal_posting_times()
            
            st.write("**📊 Your Optimal Posting Times:**")
            for day, times in optimal_times.items():
                if times != ["No data"]:
                    st.write(f"• **{day[:3]}:** {', '.join(times)}")

def display_planned_posts(planner):
    """Display list of all planned posts"""
    st.subheader("📋 All Planned Posts")
    
    calendar_items = planner.get_calendar_items()
    
    if not calendar_items:
        st.info("📝 No content planned yet. Start by adding some posts to your calendar!")
        return
    
    # Sort by date
    sorted_items = sorted(calendar_items.items(), key=lambda x: x[0])
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        content_type_filter = st.selectbox(
            "Filter by Content Type",
            options=["All"] + ["photo", "video", "carousel", "story", "reel"]
        )
    
    with col2:
        date_filter = st.selectbox(
            "Filter by Time",
            options=["All", "This Week", "This Month", "Next Month"]
        )
    
    with col3:
        sort_order = st.selectbox(
            "Sort Order",
            options=["Date (Ascending)", "Date (Descending)"]
        )
    
    # Apply filters
    filtered_items = sorted_items.copy()
    
    if content_type_filter != "All":
        filtered_items = [(date_str, item) for date_str, item in filtered_items 
                         if item['content_type'] == content_type_filter]
    
    if date_filter != "All":
        today = date.today()
        if date_filter == "This Week":
            week_start = today - timedelta(days=today.weekday())
            week_end = week_start + timedelta(days=6)
            filtered_items = [(date_str, item) for date_str, item in filtered_items
                            if week_start <= datetime.strptime(date_str, '%Y-%m-%d').date() <= week_end]
        elif date_filter == "This Month":
            month_start = today.replace(day=1)
            if today.month == 12:
                month_end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                month_end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
            filtered_items = [(date_str, item) for date_str, item in filtered_items
                            if month_start <= datetime.strptime(date_str, '%Y-%m-%d').date() <= month_end]
    
    if sort_order == "Date (Descending)":
        filtered_items.reverse()
    
    # Display filtered items
    st.write(f"**Showing {len(filtered_items)} posts**")
    
    for date_str, item in filtered_items:
        post_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        days_until = (post_date - date.today()).days
        
        with st.expander(f"📅 {date_str} ({item['content_type']}) - {days_until} days"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Content Type:** {item['content_type']}")
                st.write(f"**Caption:** {item['caption']}")
                st.write(f"**Hashtags:** {item['hashtags']}")
                if item.get('notes'):
                    st.write(f"**Notes:** {item['notes']}")
                
                st.write(f"**Scheduled for:** {post_date.strftime('%A, %B %d, %Y')}")
                if days_until == 0:
                    st.write("🎯 **Posting Today!**")
                elif days_until == 1:
                    st.write("⏰ **Posting Tomorrow**")
                elif days_until > 0:
                    st.write(f"📅 **In {days_until} days**")
                else:
                    st.write(f"⚠️ **{abs(days_until)} days overdue**")
            
            with col2:
                if st.button("✏️ Edit", key=f"edit_list_{date_str}"):
                    st.session_state[f'edit_content_{date_str}'] = True
                    st.rerun()
                
                if st.button("🗑️ Delete", key=f"delete_list_{date_str}"):
                    planner.delete_calendar_item(date_str)
                    st.success("Content deleted!")
                    st.rerun()
                
                if st.button("✅ Mark Posted", key=f"posted_{date_str}"):
                    planner.update_calendar_item(date_str, 'status', 'posted')
                    st.success("Marked as posted!")
                    st.rerun()
    
    # Export options
    st.markdown("---")
    st.subheader("📤 Export Calendar Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Export as CSV"):
            csv_data = planner.export_calendar_data("csv")
            st.download_button(
                label="💾 Download CSV",
                data=csv_data,
                file_name=f"content_calendar_{date.today().strftime('%Y-%m-%d')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📋 Export as JSON"):
            json_data = planner.export_calendar_data("json")
            st.download_button(
                label="💾 Download JSON",
                data=json_data,
                file_name=f"content_calendar_{date.today().strftime('%Y-%m-%d')}.json",
                mime="application/json"
            )

if __name__ == "__main__":
    main()
