# Terricon-Valley-bot

A Telegram bot for Terricon Valley internship program, built with Python.

Bot name: Terricons_bot

## Setup

1. The bot is already created with token provided.

2. Set up Yandex Tables:
   - Create a Yandex Cloud account.
   - Create a table in Yandex Tables.
   - Get API key and sheet ID.

3. Update `.env` with your Yandex credentials:
   ```
   YANDEX_API_KEY=your_yandex_api_key_here
   YANDEX_SHEET_ID=your_sheet_id_here
   ```

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Run the bot:
   ```
   python main.py
   ```

## Features

- Welcome message with Start button.
- Main menu with navigation to information sections.
- Confirmation and data collection for practice registration.
- Saving data to Yandex Sheets.
- Handling registration screenshots.
- Resources and instructions display.