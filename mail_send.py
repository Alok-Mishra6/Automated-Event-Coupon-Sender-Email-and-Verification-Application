import pandas as pd
import random
import os

def generate_verification_code():
    """Generate a 6-digit random verification code"""
    return str(random.randint(100000, 999999))

def process_csv_and_generate_codes(csv_file_path):
    """
    Read CSV file, extract Email, Name, Mobile and generate verification codes
    
    Args:
        csv_file_path: Path to the IISER-K_Premiere.csv file
    
    Returns:
        DataFrame with extracted data and verification codes
    """
    try:
        # Read the CSV file
        df = pd.read_csv('/home/alok/codes/ganesh_utsav/coupon_system/Automated-Event-Coupon-Sender-Email-and-Verification-Application/IISER-K_Premiere.csv')
        
        # Extract required columns
        required_columns = ['Email Address', 'Name', 'Mobile']
        
        # Check if all required columns exist
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"Warning: Missing columns: {missing_columns}")
            print(f"Available columns: {df.columns.tolist()}")
            return None
        
        # Extract only required columns
        extracted_df = df[required_columns].copy()
        
        # Generate verification codes for each row
        extracted_df['Verification Code'] = [generate_verification_code() for _ in range(len(extracted_df))]
        
        # Remove any rows with missing data
        extracted_df = extracted_df.dropna()
        
        print(f"Successfully processed {len(extracted_df)} records")
        print("\nSample data:")
        print(extracted_df.head())
        
        return extracted_df
    
    except FileNotFoundError:
        print(f"Error: File not found at {csv_file_path}")
        return None
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return None

def save_processed_data(df, output_file='processed_data_with_codes.csv'):
    """Save the processed data to a new CSV file"""
    try:
        df.to_csv(output_file, index=False)
        print(f"\nData saved to {output_file}")
        return True
    except Exception as e:
        print(f"Error saving file: {str(e)}")
        return False

if __name__ == "__main__":
    # Path to your CSV file
    csv_path = "/home/alok/codes/ganesh_utsav/coupon_system/Automated-Event-Coupon-Sender-Email-and-Verification-Application/IISER-K_Premiere.csv"
    
    # Process the CSV file
    processed_data = process_csv_and_generate_codes(csv_path)
    
    if processed_data is not None:
        # Save the processed data
        save_processed_data(processed_data)
        
        # Display statistics
        print(f"\nTotal records: {len(processed_data)}")
        print(f"Unique emails: {processed_data['Email Address'].nunique()}")
        print(f"Unique mobile numbers: {processed_data['Mobile'].nunique()}")