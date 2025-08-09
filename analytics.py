import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta

class Analytics:
    """Analytics functionality for Instagram data"""
    
    def __init__(self, data):
        self.data = data
    
    def calculate_engagement_rate(self):
        """Calculate average engagement rate"""
        return self.data['engagement_rate'].mean()
    
    def create_engagement_timeline(self):
        """Create engagement timeline chart"""
        # Group by date and calculate metrics
        daily_data = self.data.groupby('date').agg({
            'likes': 'sum',
            'comments': 'sum',
            'engagement': 'sum',
            'reach': 'sum'
        }).reset_index()
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Daily Engagement', 'Daily Reach'),
            vertical_spacing=0.1
        )
        
        # Engagement trace
        fig.add_trace(
            go.Scatter(
                x=daily_data['date'],
                y=daily_data['engagement'],
                mode='lines+markers',
                name='Engagement',
                line=dict(color='#1f77b4')
            ),
            row=1, col=1
        )
        
        # Reach trace
        fig.add_trace(
            go.Scatter(
                x=daily_data['date'],
                y=daily_data['reach'],
                mode='lines+markers',
                name='Reach',
                line=dict(color='#ff7f0e')
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            height=400,
            showlegend=True,
            title_text="Engagement and Reach Over Time"
        )
        
        return fig
    
    def create_post_type_analysis(self):
        """Create post type performance analysis"""
        post_type_data = self.data.groupby('post_type').agg({
            'likes': 'mean',
            'comments': 'mean',
            'engagement_rate': 'mean',
            'reach': 'mean'
        }).round(2).reset_index()
        
        fig = px.bar(
            post_type_data,
            x='post_type',
            y='engagement_rate',
            title='Average Engagement Rate by Post Type',
            labels={'engagement_rate': 'Engagement Rate (%)', 'post_type': 'Post Type'},
            color='engagement_rate',
            color_continuous_scale='viridis'
        )
        
        fig.update_layout(height=400)
        return fig
    
    def find_optimal_posting_times(self):
        """Find optimal posting times by day of week"""
        if 'hour' not in self.data.columns:
            return {"No time data available": []}
        
        # Group by day and hour, calculate average engagement
        time_analysis = self.data.groupby(['day_of_week', 'hour'])['engagement_rate'].mean().reset_index()
        
        optimal_times = {}
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for day in days_order:
            day_data = time_analysis[time_analysis['day_of_week'] == day]
            if not day_data.empty:
                # Get top 3 hours with highest engagement
                top_hours = day_data.nlargest(3, 'engagement_rate')['hour'].values
                optimal_times[day] = [f"{hour:02d}:00" for hour in sorted(top_hours)]
            else:
                optimal_times[day] = ["No data"]
        
        return optimal_times
    
    def get_top_posts(self, limit=5):
        """Get top performing posts"""
        return self.data.nlargest(limit, 'engagement_rate')
    
    def create_hashtag_analysis(self):
        """Analyze hashtag performance if hashtag data is available"""
        if 'hashtags' not in self.data.columns or 'hashtag_count' not in self.data.columns:
            return None
        
        # Analyze hashtag count vs engagement
        hashtag_performance = self.data.groupby('hashtag_count').agg({
            'engagement_rate': 'mean',
            'likes': 'mean',
            'comments': 'mean'
        }).reset_index()
        
        fig = px.scatter(
            hashtag_performance,
            x='hashtag_count',
            y='engagement_rate',
            size='likes',
            title='Hashtag Count vs Engagement Rate',
            labels={'hashtag_count': 'Number of Hashtags', 'engagement_rate': 'Engagement Rate (%)'}
        )
        
        return fig
    
    def create_weekly_heatmap(self):
        """Create a heatmap showing engagement by day and hour"""
        if 'hour' not in self.data.columns:
            return None
        
        # Create pivot table for heatmap
        heatmap_data = self.data.groupby(['day_of_week', 'hour'])['engagement_rate'].mean().reset_index()
        heatmap_pivot = heatmap_data.pivot(index='day_of_week', columns='hour', values='engagement_rate')
        
        # Reorder days
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        heatmap_pivot = heatmap_pivot.reindex(days_order)
        
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_pivot.values,
            x=heatmap_pivot.columns,
            y=heatmap_pivot.index,
            colorscale='viridis',
            hoverongaps=False
        ))
        
        fig.update_layout(
            title='Engagement Rate Heatmap by Day and Hour',
            xaxis_title='Hour of Day',
            yaxis_title='Day of Week',
            height=400
        )
        
        return fig
    
    def get_trend_analysis(self, days=30):
        """Get trend analysis for the last N days"""
        recent_date = self.data['date'].max()
        start_date = recent_date - timedelta(days=days)
        
        recent_data = self.data[self.data['date'] >= start_date]
        
        if len(recent_data) == 0:
            return {}
        
        # Calculate trends
        trends = {
            'total_posts': len(recent_data),
            'avg_likes': recent_data['likes'].mean(),
            'avg_comments': recent_data['comments'].mean(),
            'avg_engagement_rate': recent_data['engagement_rate'].mean(),
            'total_reach': recent_data['reach'].sum(),
            'best_post': recent_data.loc[recent_data['engagement_rate'].idxmax()] if len(recent_data) > 0 else None
        }
        
        return trends
    
    def create_content_type_comparison(self):
        """Compare performance across different content types"""
        comparison_data = self.data.groupby('post_type').agg({
            'likes': ['mean', 'max', 'min'],
            'comments': ['mean', 'max', 'min'],
            'engagement_rate': ['mean', 'max', 'min'],
            'reach': ['mean', 'max', 'min']
        }).round(2)
        
        # Flatten column names
        comparison_data.columns = ['_'.join(col).strip() for col in comparison_data.columns]
        comparison_data = comparison_data.reset_index()
        
        return comparison_data
