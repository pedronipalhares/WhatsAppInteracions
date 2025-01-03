import pandas as pd
import zipfile
import os
from datetime import datetime, timedelta
import re
import shutil

def create_temp_dir(base_directory):
    # Create a temporary directory inside the conversations folder
    temp_dir = os.path.join(base_directory, 'temp_extracted')
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    return temp_dir

def cleanup_temp_dir(temp_dir):
    # Clean up the temporary directory
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

def extract_zip_files(directory):
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
    # New WhatsApp message format: [M/D/YY, H:MM:SS AM/PM] Name: Message
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

def process_chat_files(directory):
    messages = []
    one_month_ago = datetime.now() - timedelta(days=30)
    
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
                            # Only include messages from the last month and not from Guilherme Palhares
                            if parsed['date'] >= one_month_ago and 'Guilherme Palhares' not in parsed['name']:
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
        
        # Save to CSV
        df.to_csv('whatsapp_messages.csv', index=False)
        print(f"\nProcessed {len(messages)} total messages and saved to whatsapp_messages.csv")
        return df
    
    finally:
        # Clean up temporary directory
        cleanup_temp_dir(temp_dir)

if __name__ == "__main__":
    df = process_chat_files('conversations')
    if not df.empty:
        print("\nFirst few messages:")
        print(df.head())
    else:
        print("\nNo messages found in the specified time range") 