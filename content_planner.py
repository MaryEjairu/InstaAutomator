import pandas as pd
from datetime import datetime, timedelta, date
import streamlit as st
import json

class ContentPlanner:
    """Handle content planning and calendar functionality"""
    
    def __init__(self):
        self.calendar_key = 'content_calendar'
        self.ideas_key = 'content_ideas'
        
        # Initialize session state
        if self.calendar_key not in st.session_state:
            st.session_state[self.calendar_key] = {}
        
        if self.ideas_key not in st.session_state:
            st.session_state[self.ideas_key] = []
    
    def add_calendar_item(self, date_str, content_type, caption, hashtags, notes=""):
        """Add item to content calendar"""
        calendar_item = {
            'content_type': content_type,
            'caption': caption,
            'hashtags': hashtags,
            'notes': notes,
            'created_at': datetime.now().isoformat(),
            'status': 'planned'
        }
        
        st.session_state[self.calendar_key][date_str] = calendar_item
    
    def get_calendar_items(self, start_date=None, end_date=None):
        """Get calendar items for date range"""
        items = st.session_state[self.calendar_key]
        
        if start_date and end_date:
            filtered_items = {}
            for date_str, item in items.items():
                item_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                if start_date <= item_date <= end_date:
                    filtered_items[date_str] = item
            return filtered_items
        
        return items
    
    def update_calendar_item(self, date_str, field, value):
        """Update specific field of calendar item"""
        if date_str in st.session_state[self.calendar_key]:
            st.session_state[self.calendar_key][date_str][field] = value
    
    def delete_calendar_item(self, date_str):
        """Delete calendar item"""
        if date_str in st.session_state[self.calendar_key]:
            del st.session_state[self.calendar_key][date_str]
    
    def add_content_idea(self, title, description, hashtags, priority="Medium", category="General"):
        """Add content idea"""
        idea = {
            'id': len(st.session_state[self.ideas_key]) + 1,
            'title': title,
            'description': description,
            'hashtags': hashtags,
            'priority': priority,
            'category': category,
            'created_at': datetime.now().isoformat(),
            'status': 'idea',
            'used': False
        }
        
        st.session_state[self.ideas_key].append(idea)
    
    def get_content_ideas(self, category=None, priority=None, unused_only=False):
        """Get content ideas with filters"""
        ideas = st.session_state[self.ideas_key]
        
        if category:
            ideas = [idea for idea in ideas if idea['category'] == category]
        
        if priority:
            ideas = [idea for idea in ideas if idea['priority'] == priority]
        
        if unused_only:
            ideas = [idea for idea in ideas if not idea['used']]
        
        return ideas
    
    def mark_idea_as_used(self, idea_id):
        """Mark idea as used"""
        for idea in st.session_state[self.ideas_key]:
            if idea['id'] == idea_id:
                idea['used'] = True
                break
    
    def delete_content_idea(self, idea_id):
        """Delete content idea"""
        st.session_state[self.ideas_key] = [
            idea for idea in st.session_state[self.ideas_key] 
            if idea['id'] != idea_id
        ]
    
    def get_hashtag_suggestions(self, category="General"):
        """Get hashtag suggestions based on category"""
        hashtag_library = {
            "General": ["#instagram", "#content", "#socialmedia", "#marketing", "#brand", "#engagement"],
            "Lifestyle": ["#lifestyle", "#daily", "#motivation", "#inspiration", "#wellness", "#selfcare"],
            "Business": ["#business", "#entrepreneur", "#success", "#productivity", "#growth", "#leadership"],
            "Food": ["#food", "#foodie", "#delicious", "#recipe", "#cooking", "#yummy", "#tasty"],
            "Travel": ["#travel", "#wanderlust", "#adventure", "#explore", "#vacation", "#photography"],
            "Fashion": ["#fashion", "#style", "#outfit", "#ootd", "#trendy", "#fashionista"],
            "Fitness": ["#fitness", "#workout", "#health", "#gym", "#exercise", "#fit", "#motivation"],
            "Technology": ["#tech", "#technology", "#innovation", "#digital", "#gadgets", "#software"],
            "Art": ["#art", "#creative", "#design", "#artist", "#artwork", "#illustration", "#photography"],
            "Education": ["#education", "#learning", "#knowledge", "#tips", "#tutorial", "#skills", "#development"]
        }
        
        return hashtag_library.get(category, hashtag_library["General"])
    
    def export_calendar_data(self, format_type="json"):
        """Export calendar data"""
        calendar_data = st.session_state[self.calendar_key]
        
        if format_type == "json":
            return json.dumps(calendar_data, indent=2)
        
        elif format_type == "csv":
            # Convert to DataFrame
            rows = []
            for date_str, item in calendar_data.items():
                row = {
                    'date': date_str,
                    'content_type': item['content_type'],
                    'caption': item['caption'],
                    'hashtags': item['hashtags'],
                    'notes': item['notes'],
                    'status': item['status']
                }
                rows.append(row)
            
            df = pd.DataFrame(rows)
            return df.to_csv(index=False)
        
        return ""
    
    def export_ideas_data(self, format_type="json"):
        """Export content ideas data"""
        ideas_data = st.session_state[self.ideas_key]
        
        if format_type == "json":
            return json.dumps(ideas_data, indent=2)
        
        elif format_type == "csv":
            df = pd.DataFrame(ideas_data)
            return df.to_csv(index=False)
        
        return ""
    
    def get_calendar_stats(self):
        """Get calendar statistics"""
        calendar_data = st.session_state[self.calendar_key]
        ideas_data = st.session_state[self.ideas_key]
        
        stats = {
            'total_planned_posts': len(calendar_data),
            'total_ideas': len(ideas_data),
            'unused_ideas': len([idea for idea in ideas_data if not idea['used']]),
            'content_types': {},
            'upcoming_posts_7_days': 0,
            'upcoming_posts_30_days': 0
        }
        
        # Count content types
        for item in calendar_data.values():
            content_type = item['content_type']
            stats['content_types'][content_type] = stats['content_types'].get(content_type, 0) + 1
        
        # Count upcoming posts
        today = date.today()
        week_ahead = today + timedelta(days=7)
        month_ahead = today + timedelta(days=30)
        
        for date_str in calendar_data.keys():
            post_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            if today <= post_date <= week_ahead:
                stats['upcoming_posts_7_days'] += 1
            if today <= post_date <= month_ahead:
                stats['upcoming_posts_30_days'] += 1
        
        return stats
