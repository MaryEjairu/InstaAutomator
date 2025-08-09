# Instagram Automation Bot

A Python bot that automates common Instagram activities such as liking posts by hashtag, sending direct messages to followers, and commenting on posts using predefined messages.

## Features

- Auto-like posts based on specified hashtags  
- Send personalized direct messages to followers  
- Auto-comment on posts under chosen hashtags with randomized comments  
- Mimics human behavior with randomized delays to avoid detection  
- Secure login using environment variables for credentials  

## Prerequisites

- Python 3.7 or higher  
- Instagram account  
- Access to Instagram credentials (username and password)  
- Installed dependencies (see `requirements.txt`)

## Installation

1. Clone the repository:  
   ```bash
   git clone https://github.com/MaryEjairu/InstaAutomator.git
   cd InstaAutomator

2. (Optional) Create and activate a virtual environment:
    ```
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate


3. Install dependencies:
   ```
   pip install -r requirements.txt


5. Set environment variables for Instagram credentials
   ```
   export IG_USERNAME="your_username"
   export IG_PASSWORD="your_password"

**(On Windows, use set instead of export)**



## Usage

1. Run the bot script:
   ```
   python bot.py


**Customize the hashtags, direct message text, and comments list inside the script as needed.**

## Security

- Credentials are loaded from environment variables to avoid hardcoding sensitive info.

- Use a dedicated Instagram account to reduce risk of bans.


## Limitations and Warnings

- Instagram’s policies prohibit automation that violates their terms of service; use responsibly.

- Excessive automated actions may lead to account restrictions or bans.

- Adjust delays and action limits in the script to mimic natural activity.


## Contributing

Feel free to submit issues or pull requests to improve this bot!


**Built with ❤️ by Mary Ejairu**
