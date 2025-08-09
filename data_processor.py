import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class DataProcessor:
    """Handle data processing and validation for Instagram analytics"""
    
    def __init__(self):
        self.required_columns = ['date', 'likes', 'comments', 'reach', 'impressions', 'post_type']
        self.optional_columns = ['hashtags', 'caption', 'time']
    
    def validate_data(self, data):
        """Validate if the uploaded data has required columns"""
        try:
            # Check if required columns exist
            missing_columns = [col for col in self.required_columns if col not in data.columns]
            
            if missing_columns:
                return False
            
            # Check data types
            if not pd.api.types.is_numeric_dtype(data['likes']):
                return False
            if not pd.api.types.is_numeric_dtype(data['comments']):
                return False
            if not pd.api.types.is_numeric_dtype(data['reach']):
                return False
            if not pd.api.types.is_numeric_dtype(data['impressions']):
                return False
            
            return True
        except Exception:
            return False
    
    def process_data(self, data):
        """Process and clean the data"""
        processed_data = data.copy()
        
        # Convert date column to datetime
        processed_data['date'] = pd.to_datetime(processed_data['date'])
        
        # Fill missing values
        processed_data['likes'] = processed_data['likes'].fillna(0)
        processed_data['comments'] = processed_data['comments'].fillna(0)
        processed_data['reach'] = processed_data['reach'].fillna(0)
        processed_data['impressions'] = processed_data['impressions'].fillna(0)
        
        # Add calculated columns
        processed_data['engagement'] = processed_data['likes'] + processed_data['comments']
        processed_data['engagement_rate'] = (
            processed_data['engagement'] / processed_data['reach'] * 100
        ).fillna(0)
        
        # Extract time features
        processed_data['day_of_week'] = processed_data['date'].dt.day_name()
        processed_data['hour'] = processed_data['date'].dt.hour
        processed_data['month'] = processed_data['date'].dt.month
        processed_data['week'] = processed_data['date'].dt.isocalendar().week
        
        # Handle hashtags if present
        if 'hashtags' in processed_data.columns:
            processed_data['hashtags'] = processed_data['hashtags'].fillna('')
            processed_data['hashtag_count'] = processed_data['hashtags'].str.count('#')
        
        # Sort by date
        processed_data = processed_data.sort_values('date').reset_index(drop=True)
        
        return processed_data
    
    def filter_data(self, data, start_date=None, end_date=None, post_types=None):
        """Filter data based on date range and post types"""
        filtered_data = data.copy()
        
        if start_date:
            filtered_data = filtered_data[filtered_data['date'] >= start_date]
        
        if end_date:
            filtered_data = filtered_data[filtered_data['date'] <= end_date]
        
        if post_types:
            filtered_data = filtered_data[filtered_data['post_type'].isin(post_types)]
        
        return filtered_data
    
    def aggregate_by_period(self, data, period='D'):
        """Aggregate data by time period (D=daily, W=weekly, M=monthly)"""
        aggregated = data.groupby(data['date'].dt.to_period(period)).agg({
            'likes': 'sum',
            'comments': 'sum',
            'reach': 'sum',
            'impressions': 'sum',
            'engagement': 'sum',
            'engagement_rate': 'mean',
            'date': 'count'
        }).rename(columns={'date': 'post_count'})
        
        aggregated.index = aggregated.index.to_timestamp()
        return aggregated.reset_index()
