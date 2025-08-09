import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
from utils.analytics import Analytics
from utils.content_planner import ContentPlanner
from utils.data_processor import DataProcessor
import json

st.set_page_config(page_title="Reports", page_icon="📈", layout="wide")

def main():
    st.title("📈 Reports & Insights")
    
    # Check if data is loaded
    if st.session_state.get('processed_data') is None:
        st.warning("⚠️ No analytics data loaded. Please upload your Instagram data on the main page first.")
        st.info("📊 You can still export content planning data below.")
        display_planning_reports_only()
        return
    
    data = st.session_state.processed_data
    analytics = Analytics(data)
    planner = ContentPlanner()
    
    # Sidebar for report options
    with st.sidebar:
        st.header("📊 Report Options")
        
        report_type = st.selectbox(
            "Report Type",
            options=["Performance Summary", "Detailed Analytics", "Content Planning", "Combined Report"]
        )
        
        # Date range for analytics
        st.subheader("📅 Analytics Date Range")
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
        
        # Export format
        st.subheader("📤 Export Format")
        export_format = st.selectbox(
            "Format",
            options=["PDF Summary", "CSV Data", "JSON Data", "Text Report"]
        )
        
        st.markdown("---")
        
        # Quick stats
        filtered_data = filter_data_by_date(data, start_date, end_date)
        st.metric("Posts in Range", len(filtered_data))
        st.metric("Total Engagement", f"{filtered_data['engagement'].sum():,}")
        st.metric("Avg Engagement Rate", f"{filtered_data['engagement_rate'].mean():.2f}%")
    
    # Main content based on report type
    if report_type == "Performance Summary":
        display_performance_summary(analytics, filtered_data, start_date, end_date, export_format)
    elif report_type == "Detailed Analytics":
        display_detailed_analytics(analytics, filtered_data, start_date, end_date, export_format)
    elif report_type == "Content Planning":
        display_content_planning_report(planner, export_format)
    elif report_type == "Combined Report":
        display_combined_report(analytics, planner, filtered_data, start_date, end_date, export_format)

def display_planning_reports_only():
    """Display only content planning reports when no analytics data is available"""
    st.subheader("📅 Content Planning Reports")
    
    planner = ContentPlanner()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📊 Planning Statistics**")
        stats = planner.get_calendar_stats()
        
        for key, value in stats.items():
            if key != 'content_types':
                st.metric(key.replace('_', ' ').title(), value)
        
        if stats['content_types']:
            st.write("**Content Types:**")
            for content_type, count in stats['content_types'].items():
                st.write(f"• {content_type}: {count}")
    
    with col2:
        st.write("**📤 Export Options**")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("📅 Export Calendar"):
                csv_data = planner.export_calendar_data("csv")
                st.download_button(
                    "💾 Download Calendar CSV",
                    data=csv_data,
                    file_name=f"content_calendar_{date.today().strftime('%Y-%m-%d')}.csv",
                    mime="text/csv"
                )
        
        with col_b:
            if st.button("💡 Export Ideas"):
                csv_data = planner.export_ideas_data("csv")
                st.download_button(
                    "💾 Download Ideas CSV",
                    data=csv_data,
                    file_name=f"content_ideas_{date.today().strftime('%Y-%m-%d')}.csv",
                    mime="text/csv"
                )

def filter_data_by_date(data, start_date, end_date):
    """Filter data by date range"""
    mask = (data['date'].dt.date >= start_date) & (data['date'].dt.date <= end_date)
    return data[mask]

def display_performance_summary(analytics, data, start_date, end_date, export_format):
    """Display performance summary report"""
    st.subheader("📊 Performance Summary Report")
    st.write(f"**Period:** {start_date} to {end_date}")
    
    # Key metrics grid
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Posts", len(data))
        st.metric("Total Likes", f"{data['likes'].sum():,}")
    
    with col2:
        st.metric("Total Comments", f"{data['comments'].sum():,}")
        st.metric("Total Reach", f"{data['reach'].sum():,}")
    
    with col3:
        st.metric("Avg Engagement Rate", f"{data['engagement_rate'].mean():.2f}%")
        st.metric("Best Engagement", f"{data['engagement_rate'].max():.2f}%")
    
    with col4:
        st.metric("Total Impressions", f"{data['impressions'].sum():,}")
        st.metric("Avg Daily Posts", f"{len(data) / max(1, (end_date - start_date).days):.1f}")
    
    st.markdown("---")
    
    # Performance charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Engagement Trend")
        daily_engagement = data.groupby(data['date'].dt.date)['engagement'].sum().reset_index()
        fig = px.line(daily_engagement, x='date', y='engagement', title="Daily Engagement")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 Content Type Performance")
        post_type_performance = data.groupby('post_type')['engagement_rate'].mean().reset_index()
        fig = px.bar(post_type_performance, x='post_type', y='engagement_rate', 
                    title="Avg Engagement Rate by Type")
        st.plotly_chart(fig, use_container_width=True)
    
    # Top performers
    st.subheader("🏆 Top Performing Posts")
    top_posts = data.nlargest(5, 'engagement_rate')[['date', 'post_type', 'likes', 'comments', 'engagement_rate']]
    st.dataframe(top_posts, use_container_width=True)
    
    # Insights
    st.subheader("💡 Key Insights")
    
    insights = generate_insights(data)
    for insight in insights:
        st.write(f"• {insight}")
    
    # Export button
    st.markdown("---")
    export_data = create_performance_export(data, start_date, end_date, export_format)
    
    if export_data:
        file_extension = get_file_extension(export_format)
        st.download_button(
            f"📥 Export {export_format}",
            data=export_data,
            file_name=f"performance_summary_{start_date}_to_{end_date}.{file_extension}",
            mime=get_mime_type(export_format)
        )

def display_detailed_analytics(analytics, data, start_date, end_date, export_format):
    """Display detailed analytics report"""
    st.subheader("🔍 Detailed Analytics Report")
    st.write(f"**Period:** {start_date} to {end_date}")
    
    # Comprehensive metrics
    metrics_data = {
        'Metric': [
            'Total Posts', 'Total Likes', 'Total Comments', 'Total Shares',
            'Total Reach', 'Total Impressions', 'Average Engagement Rate',
            'Median Engagement Rate', 'Best Performing Post', 'Worst Performing Post',
            'Most Active Day', 'Least Active Day', 'Average Posts per Day'
        ],
        'Value': [
            len(data),
            data['likes'].sum(),
            data['comments'].sum(),
            data.get('shares', pd.Series([0] * len(data))).sum(),
            data['reach'].sum(),
            data['impressions'].sum(),
            f"{data['engagement_rate'].mean():.2f}%",
            f"{data['engagement_rate'].median():.2f}%",
            f"{data['engagement_rate'].max():.2f}%",
            f"{data['engagement_rate'].min():.2f}%",
            data.groupby('day_of_week').size().idxmax(),
            data.groupby('day_of_week').size().idxmin(),
            f"{len(data) / max(1, (end_date - start_date).days):.1f}"
        ]
    }
    
    metrics_df = pd.DataFrame(metrics_data)
    st.dataframe(metrics_df, use_container_width=True)
    
    # Detailed charts
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Performance", "⏰ Timing", "📈 Trends", "🔍 Deep Dive"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Engagement distribution
            fig = px.histogram(data, x='engagement_rate', bins=20, title="Engagement Rate Distribution")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Likes vs Comments scatter
            fig = px.scatter(data, x='likes', y='comments', color='post_type', 
                           title="Likes vs Comments by Post Type")
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        if 'hour' in data.columns:
            col1, col2 = st.columns(2)
            
            with col1:
                hourly_engagement = data.groupby('hour')['engagement_rate'].mean().reset_index()
                fig = px.line(hourly_engagement, x='hour', y='engagement_rate', 
                            title="Average Engagement by Hour")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                daily_posts = data['day_of_week'].value_counts().reset_index()
                fig = px.bar(daily_posts, x='index', y='day_of_week', 
                           title="Posts by Day of Week")
                st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            # Weekly trends
            data['week'] = data['date'].dt.isocalendar().week
            weekly_data = data.groupby('week').agg({
                'engagement': 'sum',
                'reach': 'sum',
                'likes': 'sum',
                'comments': 'sum'
            }).reset_index()
            
            fig = px.line(weekly_data, x='week', y=['engagement', 'reach'], 
                         title="Weekly Engagement vs Reach")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Monthly comparison
            data['month'] = data['date'].dt.month
            monthly_data = data.groupby('month')['engagement_rate'].mean().reset_index()
            fig = px.bar(monthly_data, x='month', y='engagement_rate', 
                        title="Average Engagement Rate by Month")
            st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        # Correlation analysis
        numeric_cols = ['likes', 'comments', 'reach', 'impressions', 'engagement_rate']
        if 'hashtag_count' in data.columns:
            numeric_cols.append('hashtag_count')
        
        corr_matrix = data[numeric_cols].corr()
        fig = px.imshow(corr_matrix, text_auto=True, title="Correlation Matrix")
        st.plotly_chart(fig, use_container_width=True)
        
        # Statistical summary
        st.subheader("📊 Statistical Summary")
        st.dataframe(data[numeric_cols].describe(), use_container_width=True)
    
    # Export detailed report
    st.markdown("---")
    export_data = create_detailed_export(data, analytics, start_date, end_date, export_format)
    
    if export_data:
        file_extension = get_file_extension(export_format)
        st.download_button(
            f"📥 Export Detailed {export_format}",
            data=export_data,
            file_name=f"detailed_analytics_{start_date}_to_{end_date}.{file_extension}",
            mime=get_mime_type(export_format)
        )

def display_content_planning_report(planner, export_format):
    """Display content planning report"""
    st.subheader("📅 Content Planning Report")
    
    calendar_items = planner.get_calendar_items()
    ideas = planner.get_content_ideas()
    stats = planner.get_calendar_stats()
    
    # Planning overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Planned Posts", stats['total_planned_posts'])
        st.metric("Content Ideas", stats['total_ideas'])
    
    with col2:
        st.metric("Upcoming (7 days)", stats['upcoming_posts_7_days'])
        st.metric("Unused Ideas", stats['unused_ideas'])
    
    with col3:
        st.metric("Upcoming (30 days)", stats['upcoming_posts_30_days'])
        if stats['content_types']:
            most_common_type = max(stats['content_types'], key=stats['content_types'].get)
            st.metric("Most Planned Type", most_common_type)
    
    # Content type breakdown
    if stats['content_types']:
        st.subheader("📊 Content Type Distribution")
        
        content_df = pd.DataFrame([
            {'Content Type': k, 'Count': v} for k, v in stats['content_types'].items()
        ])
        
        fig = px.pie(content_df, values='Count', names='Content Type', 
                    title="Planned Content by Type")
        st.plotly_chart(fig, use_container_width=True)
    
    # Upcoming content calendar
    st.subheader("📅 Upcoming Content (Next 30 Days)")
    
    today = date.today()
    future_date = today + timedelta(days=30)
    upcoming_items = planner.get_calendar_items(today, future_date)
    
    if upcoming_items:
        upcoming_data = []
        for date_str, item in upcoming_items.items():
            post_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            days_until = (post_date - today).days
            
            upcoming_data.append({
                'Date': date_str,
                'Days Until': days_until,
                'Content Type': item['content_type'],
                'Caption Preview': item['caption'][:50] + '...' if len(item['caption']) > 50 else item['caption'],
                'Hashtags': item['hashtags'][:30] + '...' if len(item['hashtags']) > 30 else item['hashtags']
            })
        
        upcoming_df = pd.DataFrame(upcoming_data)
        st.dataframe(upcoming_df, use_container_width=True)
    else:
        st.info("No upcoming content planned for the next 30 days.")
    
    # Ideas breakdown
    st.subheader("💡 Content Ideas Overview")
    
    if ideas:
        ideas_by_category = {}
        ideas_by_priority = {}
        
        for idea in ideas:
            # Category breakdown
            cat = idea['category']
            ideas_by_category[cat] = ideas_by_category.get(cat, 0) + 1
            
            # Priority breakdown
            priority = idea['priority']
            ideas_by_priority[priority] = ideas_by_priority.get(priority, 0) + 1
        
        col1, col2 = st.columns(2)
        
        with col1:
            cat_df = pd.DataFrame([
                {'Category': k, 'Count': v} for k, v in ideas_by_category.items()
            ])
            fig = px.bar(cat_df, x='Category', y='Count', title="Ideas by Category")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            priority_df = pd.DataFrame([
                {'Priority': k, 'Count': v} for k, v in ideas_by_priority.items()
            ])
            fig = px.pie(priority_df, values='Count', names='Priority', 
                        title="Ideas by Priority")
            st.plotly_chart(fig, use_container_width=True)
    
    # Export planning report
    st.markdown("---")
    export_data = create_planning_export(planner, stats, export_format)
    
    if export_data:
        file_extension = get_file_extension(export_format)
        st.download_button(
            f"📥 Export Planning {export_format}",
            data=export_data,
            file_name=f"content_planning_report_{date.today().strftime('%Y-%m-%d')}.{file_extension}",
            mime=get_mime_type(export_format)
        )

def display_combined_report(analytics, planner, data, start_date, end_date, export_format):
    """Display combined analytics and planning report"""
    st.subheader("📊 Combined Analytics & Planning Report")
    st.write(f"**Analytics Period:** {start_date} to {end_date}")
    
    # Executive summary
    st.subheader("📋 Executive Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📊 Analytics Summary**")
        st.metric("Posts Analyzed", len(data))
        st.metric("Avg Engagement Rate", f"{data['engagement_rate'].mean():.2f}%")
        st.metric("Total Reach", f"{data['reach'].sum():,}")
        st.metric("Total Engagement", f"{data['engagement'].sum():,}")
    
    with col2:
        st.write("**📅 Planning Summary**")
        stats = planner.get_calendar_stats()
        st.metric("Posts Planned", stats['total_planned_posts'])
        st.metric("Content Ideas", stats['total_ideas'])
        st.metric("Upcoming (7 days)", stats['upcoming_posts_7_days'])
        st.metric("Unused Ideas", stats['unused_ideas'])
    
    # Performance vs Planning insights
    st.subheader("🔍 Performance vs Planning Insights")
    
    insights = []
    
    # Content type analysis
    if data['post_type'].value_counts().index[0]:
        best_performing_type = data.groupby('post_type')['engagement_rate'].mean().idxmax()
        insights.append(f"📊 Best performing content type: {best_performing_type}")
    
    if stats['content_types']:
        most_planned_type = max(stats['content_types'], key=stats['content_types'].get)
        insights.append(f"📅 Most planned content type: {most_planned_type}")
    
    # Posting frequency insights
    avg_posts_period = len(data) / max(1, (end_date - start_date).days)
    upcoming_posts_rate = stats['upcoming_posts_30_days'] / 30
    
    insights.append(f"📈 Historical posting rate: {avg_posts_period:.1f} posts/day")
    insights.append(f"📅 Planned posting rate: {upcoming_posts_rate:.1f} posts/day")
    
    if upcoming_posts_rate > avg_posts_period * 1.2:
        insights.append("⚠️ Planning to post more frequently than historical average")
    elif upcoming_posts_rate < avg_posts_period * 0.8:
        insights.append("⚠️ Planning to post less frequently than historical average")
    
    for insight in insights:
        st.write(f"• {insight}")
    
    # Recommendations
    st.subheader("💡 Recommendations")
    
    recommendations = generate_recommendations(data, stats)
    for rec in recommendations:
        st.write(f"• {rec}")
    
    # Combined charts
    st.subheader("📊 Combined Analysis")
    
    tab1, tab2, tab3 = st.tabs(["Performance Trends", "Content Planning", "Insights"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Historical performance
            daily_engagement = data.groupby(data['date'].dt.date)['engagement'].sum().reset_index()
            fig = px.line(daily_engagement, x='date', y='engagement', 
                         title="Historical Daily Engagement")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Content type performance vs planning
            historical_types = data['post_type'].value_counts().to_dict()
            planned_types = stats['content_types']
            
            comparison_data = []
            all_types = set(list(historical_types.keys()) + list(planned_types.keys()))
            
            for content_type in all_types:
                comparison_data.append({
                    'Content Type': content_type,
                    'Historical Count': historical_types.get(content_type, 0),
                    'Planned Count': planned_types.get(content_type, 0)
                })
            
            comp_df = pd.DataFrame(comparison_data)
            fig = px.bar(comp_df, x='Content Type', y=['Historical Count', 'Planned Count'],
                        title="Historical vs Planned Content Types", barmode='group')
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Planning timeline
        today = date.today()
        future_date = today + timedelta(days=30)
        upcoming_items = planner.get_calendar_items(today, future_date)
        
        if upcoming_items:
            planning_data = []
            for date_str, item in upcoming_items.items():
                planning_data.append({
                    'Date': date_str,
                    'Content Type': item['content_type'],
                    'Planned': 1
                })
            
            plan_df = pd.DataFrame(planning_data)
            plan_df['Date'] = pd.to_datetime(plan_df['Date'])
            
            fig = px.scatter(plan_df, x='Date', y='Planned', color='Content Type',
                           title="Planned Content Timeline (Next 30 Days)")
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Performance insights
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**🏆 Top Insights from Analytics**")
            analytics_insights = generate_insights(data)
            for insight in analytics_insights[:5]:
                st.write(f"• {insight}")
        
        with col2:
            st.write("**📅 Planning Optimization Opportunities**")
            planning_insights = generate_planning_insights(data, stats)
            for insight in planning_insights:
                st.write(f"• {insight}")
    
    # Export combined report
    st.markdown("---")
    export_data = create_combined_export(analytics, planner, data, stats, start_date, end_date, export_format)
    
    if export_data:
        file_extension = get_file_extension(export_format)
        st.download_button(
            f"📥 Export Combined {export_format}",
            data=export_data,
            file_name=f"combined_report_{start_date}_to_{end_date}.{file_extension}",
            mime=get_mime_type(export_format)
        )

def generate_insights(data):
    """Generate insights from analytics data"""
    insights = []
    
    # Best performing post type
    best_type = data.groupby('post_type')['engagement_rate'].mean().idxmax()
    best_rate = data.groupby('post_type')['engagement_rate'].mean().max()
    insights.append(f"{best_type.title()} posts perform best with {best_rate:.2f}% avg engagement")
    
    # Best day of week
    if 'day_of_week' in data.columns:
        best_day = data.groupby('day_of_week')['engagement_rate'].mean().idxmax()
        insights.append(f"Best performing day: {best_day}")
    
    # Engagement trend
    if len(data) > 7:
        recent_avg = data.tail(7)['engagement_rate'].mean()
        overall_avg = data['engagement_rate'].mean()
        if recent_avg > overall_avg * 1.1:
            insights.append("Recent performance is trending upward")
        elif recent_avg < overall_avg * 0.9:
            insights.append("Recent performance is below average")
    
    # Hashtag impact
    if 'hashtag_count' in data.columns:
        optimal_hashtags = data.loc[data['engagement_rate'].idxmax(), 'hashtag_count']
        insights.append(f"Highest engaging post used {optimal_hashtags} hashtags")
    
    return insights

def generate_recommendations(data, stats):
    """Generate recommendations based on analytics and planning data"""
    recommendations = []
    
    # Content type recommendations
    best_performing_type = data.groupby('post_type')['engagement_rate'].mean().idxmax()
    if stats['content_types']:
        most_planned_type = max(stats['content_types'], key=stats['content_types'].get)
        if best_performing_type != most_planned_type:
            recommendations.append(f"Consider planning more {best_performing_type} posts (your best performer)")
    
    # Posting frequency
    historical_rate = len(data) / 30  # Approximate monthly rate
    planned_rate = stats['upcoming_posts_30_days']
    
    if planned_rate < historical_rate * 0.7:
        recommendations.append("Consider increasing posting frequency to match historical performance")
    elif planned_rate > historical_rate * 1.5:
        recommendations.append("High posting frequency planned - ensure quality remains consistent")
    
    # Engagement optimization
    avg_engagement = data['engagement_rate'].mean()
    if avg_engagement < 3:
        recommendations.append("Focus on creating more engaging content - consider interactive posts")
    
    # Content ideas utilization
    if stats['unused_ideas'] > 10:
        recommendations.append("You have many unused content ideas - consider implementing them")
    
    return recommendations

def generate_planning_insights(data, stats):
    """Generate insights about content planning"""
    insights = []
    
    # Ideas vs planned ratio
    if stats['total_ideas'] > 0:
        utilization_rate = (stats['total_ideas'] - stats['unused_ideas']) / stats['total_ideas'] * 100
        insights.append(f"Content idea utilization rate: {utilization_rate:.1f}%")
    
    # Planning horizon
    if stats['upcoming_posts_7_days'] == 0:
        insights.append("No posts planned for next 7 days - consider short-term planning")
    
    if stats['upcoming_posts_30_days'] < 10:
        insights.append("Limited content planned for next 30 days")
    
    # Content type diversity
    if stats['content_types']:
        type_count = len(stats['content_types'])
        if type_count == 1:
            insights.append("All planned content is the same type - consider diversifying")
        elif type_count > 3:
            insights.append("Good content type diversity in planning")
    
    return insights

def create_performance_export(data, start_date, end_date, format_type):
    """Create exportable performance data"""
    if format_type == "CSV Data":
        return data.to_csv(index=False)
    
    elif format_type == "JSON Data":
        return data.to_json(orient='records', date_format='iso')
    
    elif format_type == "Text Report":
        report = f"""Instagram Performance Summary Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Period: {start_date} to {end_date}

=== KEY METRICS ===
Total Posts: {len(data)}
Total Likes: {data['likes'].sum():,}
Total Comments: {data['comments'].sum():,}
Total Engagement: {data['engagement'].sum():,}
Average Engagement Rate: {data['engagement_rate'].mean():.2f}%
Total Reach: {data['reach'].sum():,}
Total Impressions: {data['impressions'].sum():,}

=== TOP PERFORMING POSTS ===
"""
        
        top_posts = data.nlargest(5, 'engagement_rate')
        for idx, (_, post) in enumerate(top_posts.iterrows(), 1):
            report += f"\n{idx}. {post['date'].strftime('%Y-%m-%d')} - {post['engagement_rate']:.2f}% engagement"
        
        report += "\n\n=== INSIGHTS ===\n"
        insights = generate_insights(data)
        for insight in insights:
            report += f"• {insight}\n"
        
        return report
    
    return None

def create_detailed_export(data, analytics, start_date, end_date, format_type):
    """Create detailed analytics export"""
    if format_type == "CSV Data":
        return data.to_csv(index=False)
    elif format_type == "JSON Data":
        return data.to_json(orient='records', date_format='iso')
    elif format_type == "Text Report":
        # Create comprehensive text report
        optimal_times = analytics.find_optimal_posting_times()
        
        report = f"""Instagram Detailed Analytics Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Period: {start_date} to {end_date}

=== COMPREHENSIVE METRICS ===
Total Posts: {len(data)}
Date Range: {data['date'].min().strftime('%Y-%m-%d')} to {data['date'].max().strftime('%Y-%m-%d')}
Average Posts per Day: {len(data) / max(1, (end_date - start_date).days):.1f}

Engagement Metrics:
- Total Likes: {data['likes'].sum():,}
- Total Comments: {data['comments'].sum():,}
- Total Engagement: {data['engagement'].sum():,}
- Average Engagement Rate: {data['engagement_rate'].mean():.2f}%
- Median Engagement Rate: {data['engagement_rate'].median():.2f}%
- Best Engagement Rate: {data['engagement_rate'].max():.2f}%

Reach & Impressions:
- Total Reach: {data['reach'].sum():,}
- Total Impressions: {data['impressions'].sum():,}
- Average Reach per Post: {data['reach'].mean():.0f}
- Average Impressions per Post: {data['impressions'].mean():.0f}

=== CONTENT TYPE ANALYSIS ===
"""
        
        post_type_stats = data.groupby('post_type').agg({
            'engagement_rate': 'mean',
            'likes': 'mean',
            'comments': 'mean',
            'reach': 'mean'
        }).round(2)
        
        for post_type, stats in post_type_stats.iterrows():
            report += f"\n{post_type.upper()}:\n"
            report += f"  - Avg Engagement Rate: {stats['engagement_rate']:.2f}%\n"
            report += f"  - Avg Likes: {stats['likes']:.0f}\n"
            report += f"  - Avg Comments: {stats['comments']:.0f}\n"
            report += f"  - Avg Reach: {stats['reach']:.0f}\n"
        
        report += "\n=== OPTIMAL POSTING TIMES ===\n"
        for day, times in optimal_times.items():
            report += f"{day}: {', '.join(times)}\n"
        
        report += "\n=== TOP PERFORMING POSTS ===\n"
        top_posts = data.nlargest(10, 'engagement_rate')
        for idx, (_, post) in enumerate(top_posts.iterrows(), 1):
            report += f"{idx}. {post['date'].strftime('%Y-%m-%d')} - {post['post_type']} - {post['engagement_rate']:.2f}% engagement\n"
        
        return report
    
    return None

def create_planning_export(planner, stats, format_type):
    """Create planning report export"""
    if format_type == "CSV Data":
        return planner.export_calendar_data("csv")
    elif format_type == "JSON Data":
        return planner.export_calendar_data("json")
    elif format_type == "Text Report":
        report = f"""Content Planning Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

=== PLANNING STATISTICS ===
Total Planned Posts: {stats['total_planned_posts']}
Total Content Ideas: {stats['total_ideas']}
Unused Ideas: {stats['unused_ideas']}
Upcoming Posts (7 days): {stats['upcoming_posts_7_days']}
Upcoming Posts (30 days): {stats['upcoming_posts_30_days']}

=== CONTENT TYPE DISTRIBUTION ===
"""
        
        if stats['content_types']:
            for content_type, count in stats['content_types'].items():
                percentage = (count / stats['total_planned_posts']) * 100
                report += f"{content_type}: {count} posts ({percentage:.1f}%)\n"
        
        # Add upcoming content
        today = date.today()
        future_date = today + timedelta(days=30)
        upcoming_items = planner.get_calendar_items(today, future_date)
        
        if upcoming_items:
            report += "\n=== UPCOMING CONTENT (Next 30 Days) ===\n"
            for date_str, item in sorted(upcoming_items.items()):
                report += f"{date_str} - {item['content_type']} - {item['caption'][:50]}...\n"
        
        return report
    
    return None

def create_combined_export(analytics, planner, data, stats, start_date, end_date, format_type):
    """Create combined report export"""
    if format_type == "Text Report":
        # Combine both reports
        perf_report = create_performance_export(data, start_date, end_date, format_type)
        plan_report = create_planning_export(planner, stats, format_type)
        
        combined = f"""COMBINED INSTAGRAM ANALYTICS & PLANNING REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{perf_report}

{'='*50}

{plan_report}

=== RECOMMENDATIONS ===
"""
        
        recommendations = generate_recommendations(data, stats)
        for rec in recommendations:
            combined += f"• {rec}\n"
        
        return combined
    
    elif format_type == "JSON Data":
        combined_data = {
            'analytics': data.to_dict('records'),
            'planning': {
                'calendar': planner.get_calendar_items(),
                'ideas': planner.get_content_ideas(),
                'stats': stats
            },
            'generated_at': datetime.now().isoformat(),
            'period': f"{start_date} to {end_date}"
        }
        return json.dumps(combined_data, indent=2, default=str)
    
    return None

def get_file_extension(format_type):
    """Get file extension for format"""
    extensions = {
        "CSV Data": "csv",
        "JSON Data": "json", 
        "Text Report": "txt",
        "PDF Summary": "txt"  # Simplified to txt for now
    }
    return extensions.get(format_type, "txt")

def get_mime_type(format_type):
    """Get MIME type for format"""
    mime_types = {
        "CSV Data": "text/csv",
        "JSON Data": "application/json",
        "Text Report": "text/plain",
        "PDF Summary": "text/plain"
    }
    return mime_types.get(format_type, "text/plain")

if __name__ == "__main__":
    main()
