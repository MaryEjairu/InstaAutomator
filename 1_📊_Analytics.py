import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
from utils.analytics import Analytics
from utils.data_processor import DataProcessor

st.set_page_config(page_title="Analytics", page_icon="📊", layout="wide")

def main():
    st.title("📊 Advanced Analytics")
    
    # Check if data is loaded
    if st.session_state.get('processed_data') is None:
        st.warning("⚠️ No data loaded. Please upload your Instagram data on the main page first.")
        return
    
    data = st.session_state.processed_data
    analytics = Analytics(data)
    
    # Sidebar filters
    with st.sidebar:
        st.header("🔍 Filters")
        
        # Date range filter
        st.subheader("Date Range")
        min_date = data['date'].min().date()
        max_date = data['date'].max().date()
        
        start_date = st.date_input(
            "Start Date",
            value=max_date - timedelta(days=30),
            min_value=min_date,
            max_value=max_date
        )
        
        end_date = st.date_input(
            "End Date",
            value=max_date,
            min_value=min_date,
            max_value=max_date
        )
        
        # Post type filter
        post_types = data['post_type'].unique().tolist()
        selected_post_types = st.multiselect(
            "Post Types",
            options=post_types,
            default=post_types
        )
        
        # Apply filters
        processor = DataProcessor()
        filtered_data = processor.filter_data(
            data, 
            pd.to_datetime(start_date), 
            pd.to_datetime(end_date), 
            selected_post_types
        )
        
        st.info(f"📊 {len(filtered_data)} posts in selection")
    
    if len(filtered_data) == 0:
        st.error("❌ No data matches the selected filters.")
        return
    
    # Update analytics with filtered data
    analytics = Analytics(filtered_data)
    
    # Key metrics
    st.subheader("📈 Key Performance Indicators")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        avg_likes = filtered_data['likes'].mean()
        st.metric("Avg Likes", f"{avg_likes:,.0f}")
    
    with col2:
        avg_comments = filtered_data['comments'].mean()
        st.metric("Avg Comments", f"{avg_comments:,.0f}")
    
    with col3:
        avg_engagement_rate = analytics.calculate_engagement_rate()
        st.metric("Avg Engagement Rate", f"{avg_engagement_rate:.2f}%")
    
    with col4:
        avg_reach = filtered_data['reach'].mean()
        st.metric("Avg Reach", f"{avg_reach:,.0f}")
    
    with col5:
        avg_impressions = filtered_data['impressions'].mean()
        st.metric("Avg Impressions", f"{avg_impressions:,.0f}")
    
    st.markdown("---")
    
    # Charts section
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Trends", "📈 Performance", "⏰ Timing", "🔍 Deep Dive"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Engagement Timeline")
            timeline_chart = analytics.create_engagement_timeline()
            st.plotly_chart(timeline_chart, use_container_width=True)
        
        with col2:
            st.subheader("Post Type Performance")
            post_type_chart = analytics.create_post_type_analysis()
            st.plotly_chart(post_type_chart, use_container_width=True)
        
        # Weekly trends
        st.subheader("Weekly Engagement Trend")
        weekly_data = processor.aggregate_by_period(filtered_data, 'W')
        
        if len(weekly_data) > 1:
            fig = px.line(
                weekly_data, 
                x='date', 
                y=['engagement', 'reach'], 
                title="Weekly Engagement vs Reach",
                labels={'date': 'Week', 'value': 'Count'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏆 Top Performing Posts")
            top_posts = analytics.get_top_posts(10)
            
            for idx, (_, post) in enumerate(top_posts.iterrows(), 1):
                with st.expander(f"#{idx} - {post['date'].strftime('%Y-%m-%d')} ({post['engagement_rate']:.2f}% engagement)"):
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("Likes", f"{post['likes']:,}")
                    with col_b:
                        st.metric("Comments", f"{post['comments']:,}")
                    with col_c:
                        st.metric("Reach", f"{post['reach']:,}")
                    
                    if 'hashtags' in post and pd.notna(post['hashtags']):
                        st.write("**Hashtags:**", post['hashtags'])
        
        with col2:
            st.subheader("📊 Content Type Comparison")
            comparison_data = analytics.create_content_type_comparison()
            st.dataframe(comparison_data, use_container_width=True)
    
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("⏰ Optimal Posting Times")
            optimal_times = analytics.find_optimal_posting_times()
            
            for day, times in optimal_times.items():
                if times != ["No data"]:
                    st.write(f"**{day}:** {', '.join(times)}")
                else:
                    st.write(f"**{day}:** No data available")
        
        with col2:
            st.subheader("📅 Posting Frequency")
            posting_frequency = filtered_data['day_of_week'].value_counts()
            
            fig = px.bar(
                x=posting_frequency.index,
                y=posting_frequency.values,
                title="Posts by Day of Week",
                labels={'x': 'Day of Week', 'y': 'Number of Posts'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Heatmap if hour data is available
        if 'hour' in filtered_data.columns:
            st.subheader("🔥 Engagement Heatmap")
            heatmap = analytics.create_weekly_heatmap()
            if heatmap:
                st.plotly_chart(heatmap, use_container_width=True)
    
    with tab4:
        col1, col2 = st.columns(2)
        
        with col1:
            # Hashtag analysis if available
            if 'hashtag_count' in filtered_data.columns:
                st.subheader("📝 Hashtag Performance")
                hashtag_chart = analytics.create_hashtag_analysis()
                if hashtag_chart:
                    st.plotly_chart(hashtag_chart, use_container_width=True)
                
                # Hashtag count distribution
                hashtag_dist = filtered_data['hashtag_count'].value_counts().sort_index()
                
                fig = px.bar(
                    x=hashtag_dist.index,
                    y=hashtag_dist.values,
                    title="Distribution of Hashtag Count",
                    labels={'x': 'Number of Hashtags', 'y': 'Number of Posts'}
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📊 Correlation Analysis")
            # Correlation matrix
            numeric_cols = ['likes', 'comments', 'reach', 'impressions', 'engagement_rate']
            if 'hashtag_count' in filtered_data.columns:
                numeric_cols.append('hashtag_count')
            
            corr_matrix = filtered_data[numeric_cols].corr()
            
            fig = px.imshow(
                corr_matrix,
                text_auto=True,
                aspect="auto",
                title="Correlation Matrix",
                color_continuous_scale='RdBu_r'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Trend analysis
        st.subheader("📈 30-Day Trend Analysis")
        trends = analytics.get_trend_analysis(30)
        
        if trends:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Posts (30 days)", trends['total_posts'])
            with col2:
                st.metric("Avg Likes", f"{trends['avg_likes']:.0f}")
            with col3:
                st.metric("Avg Comments", f"{trends['avg_comments']:.0f}")
            with col4:
                st.metric("Avg Engagement", f"{trends['avg_engagement_rate']:.2f}%")
    
    # Export section
    st.markdown("---")
    st.subheader("📤 Export Analytics Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Export Filtered Data as CSV"):
            csv_data = filtered_data.to_csv(index=False)
            st.download_button(
                label="💾 Download CSV",
                data=csv_data,
                file_name=f"instagram_analytics_{start_date}_to_{end_date}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📈 Export Summary Report"):
            # Create summary report
            summary = {
                'date_range': f"{start_date} to {end_date}",
                'total_posts': len(filtered_data),
                'avg_likes': filtered_data['likes'].mean(),
                'avg_comments': filtered_data['comments'].mean(),
                'avg_engagement_rate': analytics.calculate_engagement_rate(),
                'top_post_date': filtered_data.loc[filtered_data['engagement_rate'].idxmax(), 'date'].strftime('%Y-%m-%d'),
                'optimal_posting_times': optimal_times
            }
            
            report_text = f"""Instagram Analytics Summary Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Date Range: {summary['date_range']}
Total Posts: {summary['total_posts']}
Average Likes: {summary['avg_likes']:.0f}
Average Comments: {summary['avg_comments']:.0f}
Average Engagement Rate: {summary['avg_engagement_rate']:.2f}%
Best Performing Post: {summary['top_post_date']}

Optimal Posting Times:
{chr(10).join([f"{day}: {', '.join(times)}" for day, times in summary['optimal_posting_times'].items()])}
"""
            
            st.download_button(
                label="💾 Download Report",
                data=report_text,
                file_name=f"analytics_report_{start_date}_to_{end_date}.txt",
                mime="text/plain"
            )

if __name__ == "__main__":
    main()
