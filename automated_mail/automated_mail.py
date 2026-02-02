# import pandas as pd
# import qrcode
# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# from email.mime.image import MIMEImage
# from email.mime.base import MIMEBase
# from email import encoders
# import os
# from io import BytesIO

# def generate_qr_code(json_string, filename):
#     """
#     Generate QR code from JSON string
    
#     Args:
#         json_string: JSON string to encode
#         filename: Path to save QR code image
    
#     Returns:
#         Path to saved QR code image
#     """
#     qr = qrcode.QRCode(
#         version=1,
#         error_correction=qrcode.constants.ERROR_CORRECT_L,
#         box_size=10,
#         border=4,
#     )
#     qr.add_data(json_string)
#     qr.make(fit=True)
    
#     img = qr.make_image(fill_color="black", back_color="white")
#     img.save(filename)
#     return filename

# def create_email_body(name, verification_code):
#     """
#     Create HTML email body with dynamic content
    
#     Args:
#         name: Recipient's name
#         verification_code: Verification code
    
#     Returns:
#         HTML email body
#     """
#     html = f"""
#     <html>
#         <body style="font-family: Arial, sans-serif; padding: 20px;">
#             <h2 style="color: #333;">Dear {name}!</h2>

#             <p>Please find the QR code attached for refreshments for the IPL Finals scheduled on Sunday.</p>
#             <p>The serving of refreshments will start from 11:30 PM onwards.</p>
#             <p>Your verification code is: <strong style="font-size: 18px; color: #0066cc;">{verification_code}</strong></p>
            
#             <p>Please find your QR code attached to this email. You will need to present this QR code at the event entrance.</p>
            
#             </ul>
            
#             <p>We look forward to seeing you at the event!</p>
            
#             <p style="margin-top: 30px;">
#                 Best regards,<br>
#                 <strong>Cricket Association</strong><br>
#                 IISER Kolkata
#             </p>
#         </body>
#     </html>
#     """
#     return html

# def send_email_with_qr(recipient_email, recipient_name, verification_code, json_string, 
#                        sender_email, sender_password, smtp_server='smtp.gmail.com', smtp_port=587):
#     """
#     Send email with QR code attachment
    
#     Args:
#         recipient_email: Recipient's email address
#         recipient_name: Recipient's name
#         verification_code: Verification code
#         json_string: JSON string for QR code
#         sender_email: Sender's email address
#         sender_password: Sender's email password/app password
#         smtp_server: SMTP server address
#         smtp_port: SMTP port number
    
#     Returns:
#         True if email sent successfully, False otherwise
#     """
#     try:
#         # Generate QR code
#         qr_filename = f"qr_codes/qr_{verification_code}.png"
#         os.makedirs("qr_codes", exist_ok=True)
#         generate_qr_code(json_string, qr_filename)
        
#         # Create message
#         msg = MIMEMultipart('alternative')
#         msg['From'] = sender_email
#         msg['To'] = recipient_email
#         msg['Subject'] = f"QR Code for Refreshments – IPL Finals for {recipient_name}"
        
#         # Create email body
#         html_body = create_email_body(recipient_name, verification_code)
#         msg.attach(MIMEText(html_body, 'html'))
        
#         # Attach QR code image
#         with open(qr_filename, 'rb') as f:
#             img_data = f.read()
#             image = MIMEImage(img_data, name=f"QRCode_{recipient_name}.png")
#             msg.attach(image)
        
#         # Connect to SMTP server and send email
#         server = smtplib.SMTP(smtp_server, smtp_port)
#         server.starttls()
#         server.login(sender_email, sender_password)
#         server.send_message(msg)
#         server.quit()
        
#         print(f"✓ Email sent successfully to {recipient_name} ({recipient_email})")
#         return True
        
#     except Exception as e:
#         print(f"✗ Failed to send email to {recipient_name} ({recipient_email}): {str(e)}")
#         return False

# def process_and_send_emails(csv_file, sender_email, sender_password):
#     """
#     Process CSV file and send emails to all recipients
    
#     Args:
#         csv_file: Path to CSV file with recipient data
#         sender_email: Sender's email address
#         sender_password: Sender's email password/app password
#     """
#     # Read CSV file
#     df = pd.read_csv(csv_file)
    
#     print(f"Processing {len(df)} recipients...")
#     print("-" * 60)
    
#     successful = 0
#     failed = 0
    
#     # Iterate through each row and send email
#     for index, row in df.iterrows():
#         email = row['Email Address']
#         name = row['Name']
#         verification_code = str(int(row['Verification Code']))
#         json_string = row['json_string']
        
#         # Send email
#         if send_email_with_qr(email, name, verification_code, json_string, 
#                              sender_email, sender_password):
#             successful += 1
#         else:
#             failed += 1
        
#         # Optional: Add delay to avoid rate limiting
#         # import time
#         # time.sleep(1)
    
#     print("-" * 60)
#     print(f"\nEmail sending completed!")
#     print(f"Successful: {successful}")
#     print(f"Failed: {failed}")
#     print(f"Total: {len(df)}")

# if __name__ == "__main__":
#     # Configuration
#     CSV_FILE = "test.csv"
#     SENDER_EMAIL = "cricket.activity@iiserkol.ac.in"  # Replace with your email
#     SENDER_PASSWORD = "yvnbjraisytfuzhj"   # Replace with your app password

#     # For Gmail, you need to use App Password instead of regular password
#     # Generate App Password: https://myaccount.google.com/apppasswords
    
#     print("=" * 60)
#     print("Ganesh Utsav - Automated Email Sender with QR Codes")
#     print("=" * 60)
    
#     # Process and send emails
#     process_and_send_emails(CSV_FILE, SENDER_EMAIL, SENDER_PASSWORD)

import pandas as pd
import qrcode
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os
from io import BytesIO
from datetime import datetime

def generate_qr_code_bytes(json_string):
    """
    Generate QR code and return as bytes
    
    Args:
        json_string: JSON string to encode
    
    Returns:
        QR code image as bytes
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(json_string)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="#0047AB", back_color="white")
    
    # Convert to bytes
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return buffered.getvalue()

def create_email_body(name, verification_code):
    """
    Create professional HTML email body with cricket theme
    
    Args:
        name: Recipient's name
        verification_code: Verification code
    
    Returns:
        HTML email body with enhanced cricket theme
    """
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
            }}
            .email-wrapper {{
                max-width: 650px;
                margin: 0 auto;
                background: #ffffff;
                border-radius: 20px;
                overflow: hidden;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            }}
            .header {{
                background: linear-gradient(135deg, #0047AB 0%, #002d72 100%);
                padding: 0;
                position: relative;
                overflow: hidden;
            }}
            .header-pattern {{
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background-image: 
                    repeating-linear-gradient(45deg, transparent, transparent 35px, rgba(255,255,255,.05) 35px, rgba(255,255,255,.05) 70px);
            }}
            .header-content {{
                position: relative;
                z-index: 1;
                padding: 40px 30px;
                text-align: center;
            }}
            .trophy-icon {{
                font-size: 60px;
                margin-bottom: 15px;
                animation: bounce 2s infinite;
            }}
            @keyframes bounce {{
                0%, 100% {{ transform: translateY(0); }}
                50% {{ transform: translateY(-10px); }}
            }}
            .header h1 {{
                color: #FFD700;
                font-size: 32px;
                font-weight: 800;
                text-transform: uppercase;
                letter-spacing: 2px;
                margin-bottom: 10px;
                text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.5);
            }}
            .header-subtitle {{
                color: #ffffff;
                font-size: 18px;
                font-weight: 500;
                letter-spacing: 1px;
            }}
            .content {{
                padding: 50px 40px;
                background: #ffffff;
            }}
            .greeting {{
                font-size: 28px;
                color: #0047AB;
                margin-bottom: 25px;
                font-weight: 700;
            }}
            .intro-text {{
                font-size: 17px;
                line-height: 1.8;
                color: #333;
                margin-bottom: 30px;
                text-align: center;
            }}
            .event-card {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 15px;
                margin: 30px 0;
                box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
            }}
            .event-card h3 {{
                font-size: 22px;
                margin-bottom: 20px;
                text-align: center;
                font-weight: 700;
                letter-spacing: 1px;
            }}
            .event-info {{
                display: flex;
                flex-direction: column;
                gap: 15px;
            }}
            .event-row {{
                display: flex;
                align-items: center;
                gap: 15px;
                background: rgba(255, 255, 255, 0.1);
                padding: 15px;
                border-radius: 10px;
                backdrop-filter: blur(10px);
            }}
            .event-icon {{
                font-size: 28px;
                min-width: 40px;
            }}
            .event-text {{
                flex: 1;
            }}
            .event-label {{
                font-size: 13px;
                opacity: 0.9;
                margin-bottom: 5px;
            }}
            .event-value {{
                font-size: 18px;
                font-weight: 700;
            }}
            .verification-section {{
                background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
                padding: 30px;
                border-radius: 15px;
                text-align: center;
                margin: 30px 0;
                box-shadow: 0 10px 30px rgba(255, 215, 0, 0.3);
            }}
            .verification-label {{
                color: #0047AB;
                font-size: 16px;
                font-weight: 600;
                margin-bottom: 15px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            .verification-code {{
                font-size: 42px;
                font-weight: 900;
                color: #0047AB;
                letter-spacing: 8px;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
                font-family: 'Courier New', monospace;
            }}
            .qr-section {{
                text-align: center;
                margin: 40px 0;
                padding: 40px;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                border-radius: 20px;
                position: relative;
            }}
            .qr-section::before {{
                content: '';
                position: absolute;
                top: -2px;
                left: -2px;
                right: -2px;
                bottom: -2px;
                background: linear-gradient(45deg, #0047AB, #FFD700, #0047AB);
                border-radius: 20px;
                z-index: -1;
            }}
            .qr-title {{
                font-size: 24px;
                color: #0047AB;
                font-weight: 700;
                margin-bottom: 10px;
                text-transform: uppercase;
                letter-spacing: 2px;
            }}
            .qr-subtitle {{
                color: #666;
                margin-bottom: 25px;
                font-size: 15px;
            }}
            .qr-code {{
                max-width: 300px;
                height: auto;
                border: 8px solid white;
                border-radius: 15px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
                background: white;
                padding: 15px;
            }}
            .qr-instruction {{
                margin-top: 20px;
                font-size: 16px;
                color: #0047AB;
                font-weight: 600;
            }}
            .instructions-box {{
                background: #f8f9fa;
                border-left: 6px solid #0047AB;
                padding: 30px;
                margin: 30px 0;
                border-radius: 10px;
            }}
            .instructions-box h3 {{
                color: #0047AB;
                font-size: 20px;
                margin-bottom: 20px;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            .instructions-box ul {{
                list-style: none;
                padding: 0;
            }}
            .instructions-box li {{
                padding: 12px 0;
                color: #555;
                font-size: 15px;
                line-height: 1.6;
                position: relative;
                padding-left: 30px;
            }}
            .instructions-box li::before {{
                content: '✓';
                position: absolute;
                left: 0;
                color: #0047AB;
                font-weight: bold;
                font-size: 18px;
            }}
            .highlight-banner {{
                background: linear-gradient(135deg, #0047AB 0%, #002d72 100%);
                color: white;
                padding: 25px;
                text-align: center;
                border-radius: 10px;
                margin: 30px 0;
                font-size: 20px;
                font-weight: 600;
                letter-spacing: 1px;
            }}
            .footer {{
                background: linear-gradient(135deg, #0047AB 0%, #002d72 100%);
                padding: 40px;
                text-align: center;
                color: white;
            }}
            .footer-icons {{
                font-size: 30px;
                margin-bottom: 20px;
            }}
            .footer-org {{
                font-size: 20px;
                font-weight: 700;
                color: #FFD700;
                margin-bottom: 10px;
            }}
            .footer-text {{
                font-size: 14px;
                opacity: 0.9;
                line-height: 1.6;
            }}
            .divider {{
                height: 2px;
                background: linear-gradient(to right, transparent, #0047AB, transparent);
                margin: 30px 0;
            }}
            @media only screen and (max-width: 600px) {{
                .content {{
                    padding: 30px 20px;
                }}
                .header h1 {{
                    font-size: 24px;
                }}
                .verification-code {{
                    font-size: 32px;
                    letter-spacing: 4px;
                }}
                .qr-code {{
                    max-width: 250px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="email-wrapper">
            <!-- Header -->
            <div class="header">
                <div class="header-pattern"></div>
                <div class="header-content">
                    <div class="trophy-icon">🏆</div>
                    <h1>IPL FINALS 2026</h1>
                    <div class="header-subtitle">EXCLUSIVE REFRESHMENT COUPON</div>
                </div>
            </div>
            
            <!-- Content -->
            <div class="content">
                <div class="greeting">Hello {name}! 🎉</div>
                
                <p class="intro-text">
                    You're all set for the biggest cricket showdown of the year! Get ready to witness history in the making.
                </p>
                
                <!-- Event Details Card -->
                <div class="event-card">
                    <h3>📅 EVENT INFORMATION</h3>
                    <div class="event-info">
                        <div class="event-row">
                            <div class="event-icon">🏏</div>
                            <div class="event-text">
                                <div class="event-label">Event</div>
                                <div class="event-value">IPL Finals 2026</div>
                            </div>
                        </div>
                        <div class="event-row">
                            <div class="event-icon">📆</div>
                            <div class="event-text">
                                <div class="event-label">Date</div>
                                <div class="event-value">Sunday, February 2, 2026</div>
                            </div>
                        </div>
                        <div class="event-row">
                            <div class="event-icon">⏰</div>
                            <div class="event-text">
                                <div class="event-label">Refreshments Start</div>
                                <div class="event-value">11:30 AM Onwards</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="divider"></div>
                
                <!-- Verification Code -->
                <div class="verification-section">
                    <div class="verification-label">🎫 Your Verification Code</div>
                    <div class="verification-code">{verification_code}</div>
                </div>
                
                <!-- QR Code Section -->
                <div class="qr-section">
                    <div class="qr-title">🎫 Your Digital Pass</div>
                    <div class="qr-subtitle">Present this QR code at the refreshment counter</div>
                    <img src="cid:qr_code_image" alt="QR Code" class="qr-code">
                    <div class="qr-instruction">Scan to redeem your refreshments</div>
                </div>
                
                <div class="divider"></div>

            </div>
            
            <!-- Footer -->
            <div class="footer">
                <div class="footer-icons">🏏 🏆 🎉</div>
                <div class="footer-org">CRICKET CLUB</div>
                <div class="footer-text">
                    IISER Kolkata<br>
                    Mohanpur, Nadia - 741246<br><br>
                    For queries, contact: cricket.activity@iiserkol.ac.in
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return html

def send_email_with_qr(recipient_email, recipient_name, verification_code, json_string, 
                       sender_email, sender_password, smtp_server='smtp.gmail.com', smtp_port=587):
    """
    Send email with embedded QR code using CID (Content-ID)
    
    Args:
        recipient_email: Recipient's email address
        recipient_name: Recipient's name
        verification_code: Verification code
        json_string: JSON string for QR code
        sender_email: Sender's email address
        sender_password: Sender's email password/app password
        smtp_server: SMTP server address
        smtp_port: SMTP port number
    
    Returns:
        Tuple: (success: bool, error_message: str or None)
    """
    try:
        # Generate QR code as bytes
        qr_bytes = generate_qr_code_bytes(json_string)
        
        # Create message with related content
        msg = MIMEMultipart('related')
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = f"🏏 IPL Finals 2026 - Your Refreshment Coupon | {recipient_name}"
        
        # Create alternative part for HTML
        msg_alternative = MIMEMultipart('alternative')
        msg.attach(msg_alternative)
        
        # Create email body
        html_body = create_email_body(recipient_name, verification_code)
        msg_alternative.attach(MIMEText(html_body, 'html'))
        
        # Attach QR code image with Content-ID
        qr_image = MIMEImage(qr_bytes)
        qr_image.add_header('Content-ID', '<qr_code_image>')
        qr_image.add_header('Content-Disposition', 'inline', filename=f'QRCode_{recipient_name}.png')
        msg.attach(qr_image)
        
        # Connect to SMTP server and send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        
        print(f"✓ Email sent successfully to {recipient_name} ({recipient_email})")
        return True, None
        
    except Exception as e:
        error_msg = str(e)
        print(f"✗ Failed to send email to {recipient_name} ({recipient_email}): {error_msg}")
        return False, error_msg

def process_and_send_emails(csv_file, sender_email, sender_password):
    """
    Process CSV file and send emails to all recipients
    
    Args:
        csv_file: Path to CSV file with recipient data
        sender_email: Sender's email address
        sender_password: Sender's email password/app password
    """
    # Read CSV file
    df = pd.read_csv(csv_file)
    
    print(f"Processing {len(df)} recipients...")
    print("-" * 60)
    
    successful = 0
    failed = 0
    failed_records = []
    
    # Iterate through each row and send email
    for index, row in df.iterrows():
        email = row['Email Address']
        name = row['Name']
        verification_code = str(int(row['Verification Code']))
        json_string = row['json_string']
        
        # Send email
        success, error_message = send_email_with_qr(email, name, verification_code, json_string, 
                                                    sender_email, sender_password)
        
        if success:
            successful += 1
        else:
            failed += 1
            # Store failed record
            failed_records.append({
                'Email Address': email,
                'Name': name,
                'Mobile': row.get('Mobile', 'N/A'),
                'Verification Code': verification_code,
                'json_string': json_string,
                'Error': error_message,
                'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        
        # Add delay to avoid rate limiting
        import time
        time.sleep(1)
    
    print("-" * 60)
    print(f"\n📊 Email Sending Summary")
    print("=" * 60)
    print(f"✓ Successful: {successful}")
    print(f"✗ Failed: {failed}")
    print(f"📧 Total: {len(df)}")
    print("=" * 60)
    
    # Save failed records to CSV if any
    if failed_records:
        failed_df = pd.DataFrame(failed_records)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        failed_csv_filename = f"failed_emails_{timestamp}.csv"
        failed_df.to_csv(failed_csv_filename, index=False)
        print(f"\n⚠️  Failed records saved to: {failed_csv_filename}")
        print(f"    Total failed records: {len(failed_records)}")
    else:
        print(f"\n🎉 All emails sent successfully!")

if __name__ == "__main__":
    # Configuration
    CSV_FILE = "merged_csv.csv"
    SENDER_EMAIL = "cricket.activity@iiserkol.ac.in"
    SENDER_PASSWORD = "yvnbjraisytfuzhj"
    
    print("=" * 60)
    print("🏏 IPL Finals 2026 - Automated Email Sender 🏏")
    print("=" * 60)
    print()
    
    # Process and send emails
    process_and_send_emails(CSV_FILE, SENDER_EMAIL, SENDER_PASSWORD)