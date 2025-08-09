# InstaInsights

A Instagram Analytics & Content Planning Dashboard. You can upload your Instagram data via CSV, explore detailed analytics, plan your content calendar, and optimize your social media strategy.

## Features

- Upload CSV data with Instagram post metrics  
- Visualize performance with charts and engagement insights  
- Plan and schedule posts using an interactive content calendar  
- Manage content ideas and track hashtag suggestions  
- Export detailed reports for your team or personal review  

## Required CSV Format

To get started, prepare a CSV file with these columns:

| Column       | Description                        | Format           |
|--------------|----------------------------------|------------------|
| `date`       | Date the post was published       | YYYY-MM-DD       |
| `likes`      | Number of likes on the post       | Integer          |
| `comments`   | Number of comments on the post    | Integer          |
| `reach`      | Number of unique accounts reached | Integer          |
| `impressions`| Number of total impressions       | Integer          |
| `post_type`  | Type of post (photo, video, carousel) | Text             |
| `hashtags`   | Hashtags used in the post (optional)  | Comma-separated  |

## Usage Instructions

1. **Prepare your CSV file**  
   Ensure your Instagram data CSV follows the required format above.

2. **Upload your CSV**  
   Use the file uploader in the dashboard sidebar to upload your data.

3. **Explore the Dashboard**  
   - View analytics pages for engagement, reach, and post types  
   - Use the content calendar to plan and organize posts  
   - Track content ideas and access hashtag recommendations

4. **Export Reports**  
   Generate and export reports to share with your team or for further analysis.

## Getting Started

### Installation (for local use)

    ```
    git clone https://github.com/yourusername/InstaInsights.git
    
    cd InstaInsights
    
    pip install -r requirements.txt
    
    python app.py

(Adjust commands as per your environment and project setup)


---

### Contributing

Contributions, issues, and feature requests are welcome! Feel free to open a pull request or submit issues.

**Built with ❤️ by Mary Ejairu**
