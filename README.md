# WhatsApp Chat Analyzer

This application processes WhatsApp chat exports and generates analytical reports about your messaging history. It extracts messages from WhatsApp chat exports and creates a summary of daily interactions with your contacts.

## Features

- Process WhatsApp chat exports (in ZIP format)
- Parse and organize messages into a structured format
- Generate daily interaction summaries with contacts
- Sort and organize results by contact name and date
- Consolidated, easy-to-use command line interface

## Prerequisites

- Python 3.6 or higher
- Required Python packages (listed in `requirements.txt`):
  - pandas (version 1.5.0 or higher)

## Installation

1. Clone this repository or download the source code
2. Navigate to the project directory
3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Preparing Your Data

1. Export your WhatsApp chats:
   - Open a chat in WhatsApp
   - Tap on the three dots (menu) > More > Export chat
   - Choose "Without Media" or "Include Media" as preferred
   - Share the exported ZIP file to your computer

2. Place all exported ZIP files in the `conversations` directory:
   - Create a directory named `conversations` in the project root if it doesn't exist
   - Move all your exported WhatsApp chat ZIP files to this directory

## Usage

### Basic Usage

Run the main script to process all chat exports and generate the daily interactions summary in one step:

```bash
python whatsapp_analyzer.py
```

This will:
1. Run tests to ensure everything is working correctly
2. Extract and process all messages from the WhatsApp exports in the `conversations` directory
3. Save the processed messages to `whatsapp_messages.csv`
4. Create a daily interactions summary and save it to `daily_interactions.csv`
5. Display a preview of both files

### Advanced Options

The script supports several command-line arguments for customization:

```bash
python whatsapp_analyzer.py --input-dir PATH --days NUMBER --exclude NAME --skip-tests
```

Key options:
- `--input-dir PATH`: Specify a different directory for chat exports (default: `conversations`)
- `--messages-csv FILE`: Custom filename for messages output (default: `whatsapp_messages.csv`)
- `--daily-csv FILE`: Custom filename for daily interactions output (default: `daily_interactions.csv`)
- `--days NUMBER`: Number of days to look back for messages (default: 30)
- `--exclude NAME`: Name to exclude from results (e.g., your own name)
- `--skip-tests`: Skip running the unit tests
- `--skip-messages`: Skip processing messages and use existing CSV file

### Examples

Process chats from the past 60 days, excluding your messages:
```bash
python whatsapp_analyzer.py --days 60 --exclude "Your Name"
```

Use a different directory for chat exports:
```bash
python whatsapp_analyzer.py --input-dir "my_whatsapp_exports"
```

Skip message processing and just create daily interactions from existing file:
```bash
python whatsapp_analyzer.py --skip-messages
```

## Output Files

- `whatsapp_messages.csv`: Contains all the extracted messages with timestamps and sender information
- `daily_interactions.csv`: Contains a record of which days you interacted with each contact

## Troubleshooting

### No Messages Found
- Ensure your WhatsApp exports are in ZIP format
- Verify that the ZIP files are placed in the `conversations` directory
- Check that the ZIP files contain valid WhatsApp chat exports

### Date Format Issues
- The application is designed to handle the standard WhatsApp message format
- If your WhatsApp export uses a different date/time format, you may need to modify the parsing logic in the script

## License

This project is open source and available for personal use.

## Contributing

Contributions, suggestions, and bug reports are welcome! 