import streamlit as st
from datetime import datetime
from utils.content_planner import ContentPlanner
import random

st.set_page_config(page_title="Content Ideas", page_icon="💡", layout="wide")

def main():
    st.title("💡 Content Ideas & Inspiration")
    
    planner = ContentPlanner()
    
    # Sidebar for idea management
    with st.sidebar:
        st.header("💡 Idea Stats")
        
        all_ideas = planner.get_content_ideas()
        unused_ideas = planner.get_content_ideas(unused_only=True)
        
        st.metric("Total Ideas", len(all_ideas))
        st.metric("Unused Ideas", len(unused_ideas))
        st.metric("Ideas Used", len(all_ideas) - len(unused_ideas))
        
        st.markdown("---")
        
        # Categories breakdown
        if all_ideas:
            st.subheader("📊 Categories")
            categories = {}
            for idea in all_ideas:
                cat = idea['category']
                categories[cat] = categories.get(cat, 0) + 1
            
            for category, count in categories.items():
                st.write(f"• {category}: {count}")
        
        st.markdown("---")
        
        # Priority breakdown  
        if all_ideas:
            st.subheader("🎯 Priority")
            priorities = {}
            for idea in all_ideas:
                priority = idea['priority']
                priorities[priority] = priorities.get(priority, 0) + 1
            
            for priority, count in priorities.items():
                st.write(f"• {priority}: {count}")
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["➕ Add Ideas", "📝 My Ideas", "🏷️ Hashtag Library", "🎲 Inspiration"])
    
    with tab1:
        display_add_idea_form(planner)
    
    with tab2:
        display_ideas_list(planner)
    
    with tab3:
        display_hashtag_library(planner)
    
    with tab4:
        display_inspiration_generator(planner)

def display_add_idea_form(planner):
    """Display form to add new content ideas"""
    st.subheader("➕ Add New Content Idea")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.form("add_idea_form"):
            title = st.text_input(
                "Idea Title",
                placeholder="Give your idea a catchy title..."
            )
            
            description = st.text_area(
                "Description",
                placeholder="Describe your content idea in detail...",
                height=100
            )
            
            category = st.selectbox(
                "Category",
                options=["General", "Lifestyle", "Business", "Food", "Travel", 
                        "Fashion", "Fitness", "Technology", "Art", "Education"]
            )
            
            priority = st.selectbox(
                "Priority",
                options=["Low", "Medium", "High"],
                index=1
            )
            
            hashtags = st.text_input(
                "Suggested Hashtags",
                placeholder="#hashtag1 #hashtag2 #hashtag3"
            )
            
            if st.form_submit_button("💡 Add Idea"):
                if title and description:
                    planner.add_content_idea(title, description, hashtags, priority, category)
                    st.success("💡 Idea added successfully!")
                    st.rerun()
                else:
                    st.error("Please fill in both title and description.")
    
    with col2:
        st.write("**💡 Idea Tips**")
        st.info("""
        **Good content ideas include:**
        - Clear, descriptive titles
        - Detailed descriptions
        - Relevant hashtag suggestions
        - Proper categorization
        - Priority levels for planning
        
        **Categories help with:**
        - Organization
        - Finding specific content types
        - Hashtag suggestions
        - Content planning
        """)
        
        # Quick idea templates
        st.write("**🚀 Quick Templates**")
        templates = [
            ("Behind the Scenes", "Show how you create/work", "#behindthescenes #process"),
            ("Tutorial Tuesday", "Educational content", "#tutorial #howto #learn"),
            ("Motivation Monday", "Inspirational content", "#motivation #mondaymood"),
            ("FAQ Friday", "Answer common questions", "#faq #questions #help"),
            ("User Generated Content", "Feature customer content", "#ugc #community #feature")
        ]
        
        for template_title, template_desc, template_tags in templates:
            if st.button(f"📋 {template_title}", key=f"template_{template_title}"):
                # Pre-fill form with template (in real app, this would populate the form fields)
                planner.add_content_idea(
                    template_title, 
                    template_desc, 
                    template_tags, 
                    "Medium", 
                    "General"
                )
                st.success(f"Added template: {template_title}")
                st.rerun()

def display_ideas_list(planner):
    """Display list of all content ideas"""
    st.subheader("📝 Your Content Ideas")
    
    all_ideas = planner.get_content_ideas()
    
    if not all_ideas:
        st.info("💡 No ideas yet! Start by adding some content ideas to get inspired.")
        return
    
    # Filter options
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        category_filter = st.selectbox(
            "Filter by Category",
            options=["All"] + list(set(idea['category'] for idea in all_ideas))
        )
    
    with col2:
        priority_filter = st.selectbox(
            "Filter by Priority", 
            options=["All", "High", "Medium", "Low"]
        )
    
    with col3:
        status_filter = st.selectbox(
            "Filter by Status",
            options=["All", "Unused Only", "Used Only"]
        )
    
    with col4:
        sort_by = st.selectbox(
            "Sort By",
            options=["Newest First", "Oldest First", "Priority", "Title"]
        )
    
    # Apply filters
    filtered_ideas = all_ideas.copy()
    
    if category_filter != "All":
        filtered_ideas = [idea for idea in filtered_ideas if idea['category'] == category_filter]
    
    if priority_filter != "All":
        filtered_ideas = [idea for idea in filtered_ideas if idea['priority'] == priority_filter]
    
    if status_filter == "Unused Only":
        filtered_ideas = [idea for idea in filtered_ideas if not idea['used']]
    elif status_filter == "Used Only":
        filtered_ideas = [idea for idea in filtered_ideas if idea['used']]
    
    # Sort ideas
    if sort_by == "Newest First":
        filtered_ideas.sort(key=lambda x: x['created_at'], reverse=True)
    elif sort_by == "Oldest First":
        filtered_ideas.sort(key=lambda x: x['created_at'])
    elif sort_by == "Priority":
        priority_order = {"High": 3, "Medium": 2, "Low": 1}
        filtered_ideas.sort(key=lambda x: priority_order[x['priority']], reverse=True)
    elif sort_by == "Title":
        filtered_ideas.sort(key=lambda x: x['title'].lower())
    
    st.write(f"**Showing {len(filtered_ideas)} ideas**")
    
    # Display ideas
    for idea in filtered_ideas:
        priority_color = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
        status_emoji = "✅" if idea['used'] else "💡"
        
        with st.expander(f"{status_emoji} {idea['title']} {priority_color[idea['priority']]}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Description:** {idea['description']}")
                st.write(f"**Category:** {idea['category']}")
                st.write(f"**Priority:** {idea['priority']}")
                st.write(f"**Hashtags:** {idea['hashtags']}")
                st.write(f"**Created:** {datetime.fromisoformat(idea['created_at']).strftime('%Y-%m-%d %H:%M')}")
                st.write(f"**Status:** {'Used' if idea['used'] else 'Available'}")
            
            with col2:
                if not idea['used']:
                    if st.button("✅ Mark as Used", key=f"use_{idea['id']}"):
                        planner.mark_idea_as_used(idea['id'])
                        st.success("Idea marked as used!")
                        st.rerun()
                    
                    if st.button("📅 Add to Calendar", key=f"calendar_{idea['id']}"):
                        st.session_state[f'schedule_idea_{idea["id"]}'] = True
                        st.rerun()
                
                if st.button("🗑️ Delete", key=f"delete_{idea['id']}"):
                    planner.delete_content_idea(idea['id'])
                    st.success("Idea deleted!")
                    st.rerun()
            
            # Schedule idea form
            if st.session_state.get(f'schedule_idea_{idea["id"]}', False):
                schedule_idea_form(planner, idea)

def schedule_idea_form(planner, idea):
    """Form to schedule an idea to the content calendar"""
    st.write(f"**Schedule: {idea['title']}**")
    
    with st.form(f"schedule_form_{idea['id']}"):
        from datetime import date, timedelta
        
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
            value=idea['description'],
            height=100
        )
        
        hashtags = st.text_input(
            "Hashtags",
            value=idea['hashtags']
        )
        
        notes = st.text_area(
            "Additional Notes",
            placeholder="Any additional planning notes..."
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("📅 Add to Calendar"):
                date_str = post_date.strftime('%Y-%m-%d')
                
                if date_str in st.session_state[planner.calendar_key]:
                    st.error(f"Content already planned for {date_str}")
                else:
                    planner.add_calendar_item(date_str, content_type, caption, hashtags, notes)
                    planner.mark_idea_as_used(idea['id'])
                    st.session_state[f'schedule_idea_{idea["id"]}'] = False
                    st.success(f"Idea scheduled for {date_str} and marked as used!")
                    st.rerun()
        
        with col2:
            if st.form_submit_button("❌ Cancel"):
                st.session_state[f'schedule_idea_{idea["id"]}'] = False
                st.rerun()

def display_hashtag_library(planner):
    """Display hashtag suggestions by category"""
    st.subheader("🏷️ Hashtag Library & Suggestions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📚 Hashtag Categories**")
        
        categories = ["General", "Lifestyle", "Business", "Food", "Travel", 
                     "Fashion", "Fitness", "Technology", "Art", "Education"]
        
        selected_category = st.selectbox("Select Category", categories)
        
        hashtags = planner.get_hashtag_suggestions(selected_category)
        
        st.write(f"**Suggested hashtags for {selected_category}:**")
        hashtag_text = " ".join(hashtags)
        
        st.code(hashtag_text)
        
        if st.button("📋 Copy Hashtags"):
            st.success("Hashtags copied to clipboard! (In a real app)")
        
        # Hashtag tips
        st.info("""
        **💡 Hashtag Tips:**
        - Use 5-10 hashtags per post
        - Mix popular and niche hashtags
        - Research hashtags before using
        - Avoid banned hashtags
        - Create branded hashtags
        - Track hashtag performance
        """)
    
    with col2:
        st.write("**🔍 Hashtag Research Tools**")
        
        research_hashtag = st.text_input(
            "Research Hashtag",
            placeholder="Enter a hashtag to get similar suggestions"
        )
        
        if research_hashtag:
            # Simulated hashtag suggestions (in real app, would use API)
            base_tag = research_hashtag.replace("#", "")
            suggestions = [
                f"#{base_tag}",
                f"#{base_tag}tips",
                f"#{base_tag}life",
                f"#{base_tag}lover",
                f"#{base_tag}community",
                f"#{base_tag}inspiration",
                f"#{base_tag}daily",
                f"#{base_tag}style",
                f"#{base_tag}guide",
                f"#{base_tag}goals"
            ]
            
            st.write("**Similar hashtags:**")
            for suggestion in suggestions:
                st.write(f"• {suggestion}")
        
        st.markdown("---")
        
        st.write("**📊 Popular Hashtag Combinations**")
        
        combinations = {
            "Engagement Boosters": ["#like4like", "#follow4follow", "#instagood", "#photooftheday"],
            "Lifestyle": ["#lifestyle", "#daily", "#mood", "#vibes"],
            "Business": ["#entrepreneur", "#success", "#business", "#growth"],
            "Food": ["#foodie", "#yummy", "#delicious", "#foodporn"],
            "Travel": ["#travel", "#wanderlust", "#adventure", "#explore"]
        }
        
        for combo_name, tags in combinations.items():
            with st.expander(combo_name):
                st.write(" ".join(tags))

def display_inspiration_generator(planner):
    """Display content inspiration generator"""
    st.subheader("🎲 Content Inspiration Generator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**🎯 Random Content Ideas**")
        
        if st.button("🎲 Generate Random Idea"):
            ideas = generate_random_ideas()
            random_idea = random.choice(ideas)
            
            st.success("💡 **Random Idea Generated!**")
            st.write(f"**Title:** {random_idea['title']}")
            st.write(f"**Description:** {random_idea['description']}")
            st.write(f"**Category:** {random_idea['category']}")
            st.write(f"**Hashtags:** {random_idea['hashtags']}")
            
            if st.button("💾 Save This Idea"):
                planner.add_content_idea(
                    random_idea['title'],
                    random_idea['description'],
                    random_idea['hashtags'],
                    "Medium",
                    random_idea['category']
                )
                st.success("Idea saved to your collection!")
                st.rerun()
        
        st.markdown("---")
        
        st.write("**🎨 Content Prompts**")
        prompts = [
            "Show your workspace/behind the scenes",
            "Share a tip or hack you've learned",
            "Post about your morning routine",
            "Feature a customer or team member",
            "Share an inspiring quote with your take on it",
            "Show before and after of a project",
            "Answer a frequently asked question",
            "Share what you're currently learning",
            "Post about your goals for the week/month",
            "Show your favorite tools or resources"
        ]
        
        selected_prompt = st.selectbox("Choose a prompt:", ["Select a prompt..."] + prompts)
        
        if selected_prompt != "Select a prompt...":
            st.write(f"**Your prompt:** {selected_prompt}")
            
            if st.button("💾 Save as Idea"):
                planner.add_content_idea(
                    f"Prompt: {selected_prompt[:30]}...",
                    selected_prompt,
                    "#content #inspiration",
                    "Medium",
                    "General"
                )
                st.success("Prompt saved as an idea!")
                st.rerun()
    
    with col2:
        st.write("**📅 Content Themes by Day**")
        
        weekly_themes = {
            "Monday": ["Motivation Monday", "Monday Mood", "Week Goals"],
            "Tuesday": ["Tutorial Tuesday", "Tip Tuesday", "Tech Tuesday"],
            "Wednesday": ["Wisdom Wednesday", "What's Working Wednesday", "Workout Wednesday"],
            "Thursday": ["Throwback Thursday", "Thoughts Thursday", "Thanks Thursday"],
            "Friday": ["Feature Friday", "Fun Facts Friday", "Friday Feels"],
            "Saturday": ["Saturday Spotlight", "Self-care Saturday", "Style Saturday"],
            "Sunday": ["Sunday Summary", "Self-reflection Sunday", "Sunday Setup"]
        }
        
        for day, themes in weekly_themes.items():
            with st.expander(f"📅 {day}"):
                for theme in themes:
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        st.write(f"• {theme}")
                    with col_b:
                        if st.button("➕", key=f"add_theme_{theme}"):
                            planner.add_content_idea(
                                theme,
                                f"Create content for {theme}",
                                f"#{theme.lower().replace(' ', '')} #{day.lower()}",
                                "Medium",
                                "General"
                            )
                            st.success(f"Added {theme}!")
                            st.rerun()
        
        st.markdown("---")
        
        st.write("**🎭 Content Types to Try**")
        content_types = [
            ("Polls & Questions", "Engage audience with interactive content"),
            ("User Generated Content", "Feature your community"),
            ("Educational Carousel", "Teach something in multiple slides"),
            ("Day in the Life", "Show your authentic daily routine"),
            ("Product/Service Spotlight", "Highlight what you offer"),
            ("Team Feature", "Introduce team members"),
            ("Process Video", "Show how you do what you do"),
            ("Quick Tips", "Share valuable bite-sized advice")
        ]
        
        for content_type, description in content_types:
            with st.expander(content_type):
                st.write(description)
                if st.button("💡 Add as Idea", key=f"add_type_{content_type}"):
                    planner.add_content_idea(
                        content_type,
                        description,
                        "#content #engagement",
                        "Medium",
                        "General"
                    )
                    st.success(f"Added {content_type} as an idea!")
                    st.rerun()

def generate_random_ideas():
    """Generate random content ideas"""
    return [
        {
            "title": "Morning Routine Breakdown",
            "description": "Share your morning routine and how it sets you up for success",
            "category": "Lifestyle",
            "hashtags": "#morningroutine #productivity #lifestyle #motivation"
        },
        {
            "title": "Tool Tuesday Feature",
            "description": "Highlight a tool, app, or resource that makes your work easier",
            "category": "Business",
            "hashtags": "#tools #productivity #business #efficiency"
        },
        {
            "title": "Behind the Scenes Process",
            "description": "Show the process behind creating your product or service",
            "category": "Business",
            "hashtags": "#behindthescenes #process #work #transparency"
        },
        {
            "title": "Customer Success Story",
            "description": "Feature a customer and their success story with your product/service",
            "category": "Business",
            "hashtags": "#customerstory #success #testimonial #community"
        },
        {
            "title": "Quick Tip Thursday",
            "description": "Share a quick, actionable tip related to your niche",
            "category": "Education",
            "hashtags": "#tips #education #quicktip #value"
        }
    ]

if __name__ == "__main__":
    main()
