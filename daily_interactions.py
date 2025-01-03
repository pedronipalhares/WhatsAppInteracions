import pandas as pd
from datetime import datetime
import unittest

def create_daily_interactions(input_csv='whatsapp_messages.csv', output_csv='daily_interactions.csv'):
    # Read the messages CSV
    df = pd.read_csv(input_csv)
    
    # Convert Date column to datetime
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Extract just the date part (without time)
    df['Date'] = df['Date'].dt.date
    
    # Group by Name and Date, keeping only one interaction per day
    daily_df = df.groupby(['Name', 'Date']).size().reset_index()
    
    # Drop the count column
    daily_df = daily_df[['Name', 'Date']]
    
    # Sort by name and then date
    daily_df = daily_df.sort_values(['Name', 'Date'])
    
    # Save to CSV
    daily_df.to_csv(output_csv, index=False)
    print(f"\nCreated daily interactions file with {len(daily_df)} records")
    return daily_df

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
        # Process the test data
        result_df = create_daily_interactions('test_messages.csv', 'test_daily.csv')
        
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
        import os
        if os.path.exists('test_messages.csv'):
            os.remove('test_messages.csv')
        if os.path.exists('test_daily.csv'):
            os.remove('test_daily.csv')

if __name__ == "__main__":
    # First run the tests
    print("Running tests...")
    unittest.main(argv=['dummy'], exit=False)
    
    print("\nCreating daily interactions file...")
    daily_df = create_daily_interactions()
    print("\nFirst few daily interactions:")
    print(daily_df.head()) 