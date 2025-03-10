import pandas as pd
import zipfile
import os
import re
import shutil
import unittest
import argparse
from datetime import datetime, timedelta

# Utility functions for processing chats

def create_temp_dir(base_directory):
    """Create a temporary directory inside the base directory."""
    temp_dir = os.path.join(base_directory, 'temp_extracted')
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    return temp_dir

def cleanup_temp_dir(temp_dir):
    """Clean up the temporary directory."""
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

def extract_zip_files(directory):
    """Extract all ZIP files in the given directory."""
    temp_dir = create_temp_dir(directory)
    extracted_files = []
    
    for filename in os.listdir(directory):
        if filename.endswith('.zip'):
            # Create a unique directory for each chat inside the temp directory
            chat_name = filename.replace('.zip', '')
            extract_dir = os.path.join(temp_dir, f'chat_{chat_name}')
            os.makedirs(extract_dir, exist_ok=True)
            
            zip_path = os.path.join(directory, filename)
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                    # Store the full path of the extracted file
                    for extracted_file in zip_ref.namelist():
                        full_path = os.path.join(extract_dir, extracted_file)
                        extracted_files.append(full_path)
                print(f"Successfully extracted {filename}")
            except Exception as e:
                print(f"Error extracting {filename}: {str(e)}")
    
    return temp_dir, extracted_files

def parse_whatsapp_message(line):
    """Parse a WhatsApp message line into its components."""
    # WhatsApp message format: [M/D/YY, H:MM:SS AM/PM] Name: Message
    pattern = r'^\[(\d{1,2}/\d{1,2}/\d{2},\s+\d{1,2}:\d{2}:\d{2}\s+[AaPpMm]{2})\]\s+([^:]+):\s+(.+)$'
    match = re.match(pattern, line)
    if match:
        date_str, name, message = match.groups()
        try:
            # Parse the date in the format "M/D/YY, H:MM:SS AM/PM"
            date = datetime.strptime(date_str, '%m/%d/%y, %I:%M:%S %p')
            return {'date': date, 'name': name.strip(), 'message': message.strip()}
        except ValueError as e:
            print(f"Error parsing date {date_str}: {str(e)}")
            return None
    return None

def process_chat_files(directory, days_limit=30, exclude_name=None):
    """Process WhatsApp chat files and return a DataFrame of messages."""
    messages = []
    time_limit = datetime.now() - timedelta(days=days_limit)
    
    # First, extract all zip files to a temporary directory
    temp_dir, extracted_files = extract_zip_files(directory)
    print(f"Extracted {len(extracted_files)} files")
    
    try:
        # Process each extracted text file
        for file_path in extracted_files:
            if file_path.endswith('.txt'):
                chat_name = os.path.basename(os.path.dirname(file_path)).replace('chat_WhatsApp Chat - ', '')
                print(f"\nProcessing chat with {chat_name}")
                
                try:
                    # Try different encodings
                    encodings = ['utf-8', 'utf-8-sig', 'latin1', 'cp1252']
                    content = None
                    
                    for encoding in encodings:
                        try:
                            with open(file_path, 'r', encoding=encoding) as file:
                                content = file.readlines()
                                print(f"Successfully read chat with {encoding} encoding")
                                break
                        except UnicodeDecodeError:
                            continue
                    
                    if content is None:
                        print(f"Could not read chat with any encoding")
                        continue
                    
                    file_messages = 0
                    for line in content:
                        line = line.strip()
                        # Skip empty lines or lines that don't look like messages
                        if not line or not line.startswith('['):
                            continue
                            
                        parsed = parse_whatsapp_message(line)
                        if parsed:
                            # Filter based on date and name
                            include_message = True
                            
                            if parsed['date'] < time_limit:
                                include_message = False
                            
                            if exclude_name and exclude_name in parsed['name']:
                                include_message = False
                            
                            if include_message:
                                messages.append({
                                    'Name': parsed['name'],
                                    'Date': parsed['date'],
                                    'Message': parsed['message']
                                })
                                file_messages += 1
                    
                    print(f"Found {file_messages} messages in chat with {chat_name}")
                    
                except Exception as e:
                    print(f"Error processing chat with {chat_name}: {str(e)}")
        
        # Create DataFrame and sort by date
        df = pd.DataFrame(messages)
        if not df.empty:
            df = df.sort_values('Date')
            # Format the date column to be more readable
            df['Date'] = df['Date'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        return df
    
    finally:
        # Clean up temporary directory
        cleanup_temp_dir(temp_dir)

def create_daily_interactions(df, output_csv='daily_interactions.csv'):
    """Create a daily interactions summary from the messages DataFrame."""
    if df.empty:
        print("No messages to process for daily interactions")
        return pd.DataFrame()
    
    # Make a copy to avoid modifying the original
    daily_df = df.copy()
    
    # Convert Date column to datetime
    daily_df['Date'] = pd.to_datetime(daily_df['Date'])
    
    # Extract just the date part (without time)
    daily_df['Date'] = daily_df['Date'].dt.date
    
    # Group by Name and Date, keeping only one interaction per day
    daily_df = daily_df.groupby(['Name', 'Date']).size().reset_index()
    
    # Drop the count column
    daily_df = daily_df[['Name', 'Date']]
    
    # Sort by name and then date
    daily_df = daily_df.sort_values(['Name', 'Date'])
    
    # Save to CSV if an output file is specified
    if output_csv:
        daily_df.to_csv(output_csv, index=False)
        print(f"\nCreated daily interactions file with {len(daily_df)} records")
    
    return daily_df

# Test class for daily interactions functionality
class TestDailyInteractions(unittest.TestCase):
    def setUp(self):
        # Create a test DataFrame with multiple messages per day from same person
        self.test_data = pd.DataFrame({
            'Name': ['John', 'John', 'Mary', 'John', 'Mary'],
            'Date': [
                '2024-01-01 10:00:00',
                '2024-01-01 11:00:00',  # Same day as first message
                '2024-01-01 12:00:00',
                '2024-01-02 10:00:00',  # Different day
                '2024-01-02 11:00:00'
            ],
            'Message': ['msg1', 'msg2', 'msg3', 'msg4', 'msg5']
        })
        self.test_data.to_csv('test_messages.csv', index=False)
    
    def test_daily_interactions(self):
        # Test with direct DataFrame input
        result_df = create_daily_interactions(self.test_data, 'test_daily.csv')
        
        # Verify the results
        self.assertEqual(len(result_df), 4)  # Should have 4 records (2 people × 2 days)
        
        # Check that each person has only one entry per day
        daily_counts = result_df.groupby(['Name', 'Date']).size()
        self.assertTrue(all(count == 1 for count in daily_counts))
        
        # Verify sorting by name then date
        names = result_df['Name'].tolist()
        self.assertEqual(names, sorted(names), "Results should be sorted by name")
        
        # For each name, verify dates are in order
        for name in result_df['Name'].unique():
            dates = result_df[result_df['Name'] == name]['Date'].tolist()
            self.assertEqual(dates, sorted(dates), f"Dates for {name} should be in order")
        
        # Clean up test files
        if os.path.exists('test_messages.csv'):
            os.remove('test_messages.csv')
        if os.path.exists('test_daily.csv'):
            os.remove('test_daily.csv')

def run_tests():
    """Run the unit tests."""
    print("Running tests...")
    unittest.main(argv=['dummy'], exit=False)
    print("Tests completed.")

def main():
    """Main function to process chat files and create daily interactions."""
    parser = argparse.ArgumentParser(description='WhatsApp Chat Analyzer')
    parser.add_argument('--input-dir', default='conversations', help='Directory containing WhatsApp chat exports (default: conversations)')
    parser.add_argument('--messages-csv', default='whatsapp_messages.csv', help='Output file for messages (default: whatsapp_messages.csv)')
    parser.add_argument('--daily-csv', default='daily_interactions.csv', help='Output file for daily interactions (default: daily_interactions.csv)')
    parser.add_argument('--days', type=int, default=30, help='Number of days to look back (default: 30)')
    parser.add_argument('--exclude', help='Name to exclude from results')
    parser.add_argument('--skip-tests', action='store_true', help='Skip running tests')
    parser.add_argument('--skip-messages', action='store_true', help='Skip processing messages, use existing CSV')
    
    args = parser.parse_args()
    
    if not args.skip_tests:
        run_tests()
    
    messages_df = None
    
    if args.skip_messages:
        # Use existing messages CSV
        if os.path.exists(args.messages_csv):
            print(f"\nUsing existing messages file: {args.messages_csv}")
            messages_df = pd.read_csv(args.messages_csv)
        else:
            print(f"Error: {args.messages_csv} not found. Cannot skip message processing.")
            return
    else:
        # Process chat files and save messages
        print(f"\nProcessing WhatsApp chats from {args.input_dir}...")
        messages_df = process_chat_files(args.input_dir, args.days, args.exclude)
        
        if messages_df.empty:
            print(f"\nNo messages found in the specified time range")
            return
        
        # Save to CSV
        messages_df.to_csv(args.messages_csv, index=False)
        print(f"\nProcessed {len(messages_df)} total messages and saved to {args.messages_csv}")
        print("\nFirst few messages:")
        print(messages_df.head())
    
    # Create daily interactions
    print(f"\nCreating daily interactions summary...")
    daily_df = create_daily_interactions(messages_df, args.daily_csv)
    
    if not daily_df.empty:
        print("\nFirst few daily interactions:")
        print(daily_df.head())
    
    print("\nWhatsApp chat analysis complete! 🎉")

if __name__ == "__main__":
    main() 