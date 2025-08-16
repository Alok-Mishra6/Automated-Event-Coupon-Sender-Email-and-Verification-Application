# 🎫 Automated Coupon System

This is a comprehensive, secure, and user-friendly Flask-based web application designed for creating, distributing, and verifying digital event tickets using QR code technology. The system features robust authentication via Google OAuth, seamless email delivery with the Gmail API, and a sleek, modern dark-themed interface.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-v2.3+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Status](https://img.shields.io/badge/status-production--ready-brightgreen.svg)

## 🌟 Core Features

### 🔐 Authentication & Security
- **Google OAuth 2.0**: Secure and reliable authentication using Google accounts.
- **Gmail API Integration**: Send personalized event tickets directly from your authenticated Gmail account.
- **AES-256 Encryption**: Military-grade encryption for all ticket data, ensuring maximum security.
- **Timestamp Validation**: Tickets automatically expire after 24 hours, preventing misuse.
- **One-Time Usage**: Each ticket is valid for a single use, preventing fraud and unauthorized entry.
- **Rate Limiting**: Built-in protection against spam and abuse.

### 🎫 Ticket Management
- **Automated Generation**: Instantly create unique, encrypted tickets for each attendee.
- **QR Code Integration**: Each ticket includes a secure QR code with embedded attendee information.
- **Batch Processing**: Efficiently handle large attendee lists from a CSV file.
- **Real-Time Status Tracking**: Monitor the status of each ticket (pending, sent, used) in real-time.
- **Smart Attendee Detection**: The system intelligently identifies new and existing ticket holders.

### 📧 Email Distribution
- **Responsive HTML Templates**: Beautiful and modern email templates that look great on any device.
- **Personalized Content**: Customize emails with each attendee's name and event details.
- **Live Progress Tracking**: Monitor the email sending process in real-time with detailed feedback.
- **Automatic Retry Logic**: The system automatically retries sending failed emails.
- **Confirmation Preview**: Review the recipient list before sending out the email campaign.

### 📱 QR Code Verification
- **Instant Scanning**: Verify tickets instantly using a mobile device's camera.
- **HTML5 Camera Access**: Seamless camera integration for mobile-based QR code scanning.
- **Manual Verification Backup**: A fallback option for manual ticket verification if the camera is unavailable.
- **Real-Time Feedback**: Get immediate verification results with detailed information.
- **Mobile-Optimized Interface**: A touch-friendly and intuitive interface for event staff.

### 🎨 Modern User Interface
- **Professional Dark Theme**: A sleek dark mode with stylish purple and blue accents.
- **Fully Responsive Design**: The application is optimized for all screen sizes, from desktops to mobile devices.
- **Smooth Animations & Effects**: Glass-morphism effects and smooth transitions for a premium user experience.
- **Intuitive Navigation**: A user-friendly interface that is easy to use for all skill levels.
- **Live Statistics**: Get real-time updates on your campaign's statistics and progress.

## 🚀 Getting Started

Follow these steps to set up and run the application on your local machine.

### 1. Prerequisites
- Python 3.8+
- `pip` for package management
- A Google account for OAuth and Gmail API access
- `ngrok` for exposing the local server to the internet (for mobile testing)

### 2. Initial Setup

```bash
# Clone the repository to your local machine
git clone https://github.com/your-username/automated-coupon-system.git
cd automated-coupon-system

# Install the required Python packages
pip install -r requirements.txt

# Run the initial setup script
python setup.py
```

### 3. Google Cloud Console Configuration

To enable Google authentication and email sending, you need to configure a project in the Google Cloud Console.

1.  **Navigate to the Google Cloud Console**: [https://console.cloud.google.com/](https://console.cloud.google.com/)
2.  **Create a New Project**:
    *   Click on the project dropdown in the top navigation bar and select "New Project".
    *   Enter a project name (e.g., "Automated Coupon System") and click "Create".
3.  **Enable Necessary APIs**:
    *   In the project dashboard, go to "APIs & Services" > "Enabled APIs & Services".
    *   Click on "+ ENABLE APIS AND SERVICES".
    *   Search for and enable the following APIs:
        *   **Gmail API**
        *   **Google People API**
4.  **Create OAuth 2.0 Credentials**:
    *   Go to "APIs & Services" > "Credentials".
    *   Click on "+ CREATE CREDENTIALS" and select "OAuth 2.0 Client ID".
    *   **Configure the Consent Screen**:
        *   If prompted, configure the consent screen.
        *   Choose "External" for the user type and click "Create".
        *   Fill in the required fields (App name, User support email, Developer contact information).
        *   Click "SAVE AND CONTINUE" through the "Scopes" and "Test users" sections.
    *   **Create the Client ID**:
        *   Select "Web application" as the application type.
        *   Under "Authorized JavaScript origins", add `http://localhost:5000`.
        *   Under "Authorized redirect URIs", add `http://localhost:5000/auth/callback`.
        *   Click "Create".
5.  **Get Your Credentials**:
    *   A dialog box will appear with your "Client ID" and "Client Secret". Copy these values.
6.  **Update the `.env` File**:
    *   Create a `.env` file in the root of the project by copying the `.env.example` file.
    *   Paste your credentials into the `.env` file:

    ```env
    # Google OAuth Configuration
    GOOGLE_CLIENT_ID=your-google-client-id-here
    GOOGLE_CLIENT_SECRET=your-google-client-secret-here
    GOOGLE_REDIRECT_URI=http://localhost:5000/auth/callback

    # Coupon Encryption
    COUPON_SECRET_KEY=your-encryption-secret-key-here
    ```

### 4. Ngrok Setup for Mobile Access

For mobile access and to use the QR scanner on other devices, you need a public URL. `ngrok` is the recommended tool for this.

1.  **Sign up for Ngrok**: Go to [https://ngrok.com/signup](https://ngrok.com/signup) and create a free account.
2.  **Get Your Authtoken**: Find your authtoken on your [ngrok dashboard](https://dashboard.ngrok.com/get-started/your-authtoken).
3.  **Install and Configure Ngrok**:
    ```bash
    # Install ngrok (if you don't have it)
    python setup_ngrok.py

    # Configure your authtoken
    ngrok config add-authtoken <YOUR_AUTHTOKEN>
    ```
4.  **Start the Application with Ngrok**:
    ```bash
    ./start_with_ngrok.sh
    ```
    This script will start `ngrok`, update your `.env` file with the public URL, and start the Flask application.

5.  **Update Google Cloud Console Redirect URI**:
    *   The script will give you a public `ngrok` URL (e.g., `https://<random-string>.ngrok.io`).
    *   Go back to your [Google Cloud Console Credentials](https://console.cloud.google.com/apis/credentials).
    *   Edit your OAuth 2.0 Client ID.
    *   Add the `ngrok` URL to the "Authorized redirect URIs": `https://<random-string>.ngrok.io/auth/callback`

### 5. Add Recipients

Add the email addresses of your event attendees to the `sample_attendees.csv` file. Make sure the file has a header row with the column name `email`.

```csv
email
user1@example.com
user2@example.com
user3@example.com
```

### 6. Run the Application

If you are not using `ngrok`, you can run the app directly:
```bash
python app.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

## 📋 How to Use the System

### For Administrators (Sending Campaigns)

1.  **Sign In with Google**:
    *   Visit [http://localhost:5000](http://localhost:5000) (or your `ngrok` URL).
    *   Click "Continue with Google" and authorize the application to send emails on your behalf.
    *   You will be redirected to the main dashboard.

2.  **Upload Recipients**:
    *   Upload a CSV file containing the email addresses of your attendees.
    *   The system will validate the email formats and provide real-time statistics.

3.  **Send the Campaign**:
    *   Enter a name for your event.
    *   Click "Generate Coupons & Send Emails".
    *   The system will send personalized emails with QR codes from your authenticated Gmail account.
    *   You can monitor the progress and delivery status in real-time.

4.  **View Statistics**:
    *   The dashboard displays the total number of recipients, coupons generated, emails sent, and used tickets.

### For Event Staff (Verifying Coupons)

1.  **Access the QR Scanner**:
    *   Navigate to the scanner interface on a mobile device using the `ngrok` URL.
    *   Click "Start Scanner" to activate the camera.
    *   Point the camera at the QR code on the attendee's ticket.
    *   The system will automatically verify the ticket and mark it as used.

2.  **Manual Verification**:
    *   If the camera is unavailable, you can use the manual entry form.
    *   Enter the recipient's email and the encrypted data from the ticket.
    *   Click "Verify Coupon" to validate the ticket.

### For Recipients

Recipients will receive a professionally designed HTML email with:
- A personalized greeting.
- A unique QR code for easy scanning.
- A coupon ID for reference.
- Clear instructions on how to use the ticket.

## 🏗️ System Architecture

The application can be run in two modes:

*   **Single-Device Mode**: Uses CSV files for data storage. This mode is simple to set up and is suitable for small events.
*   **Multi-Device Mode**: Utilizes a PostgreSQL database and Redis for real-time synchronization between multiple scanning devices. This is ideal for larger events with multiple staff members.

To set up the multi-device architecture, run the interactive setup script:
```bash
python setup_distributed.py
```

## 🔐 Security Features

- **AES-256 Encryption**: All coupon data is encrypted using the Fernet symmetric encryption algorithm.
- **Timestamp Validation**: Coupons are valid for 24 hours from the time of generation.
- **Email Hash Integration**: An additional layer of security to prevent tampering.
- **One-Time Usage**: Each coupon can only be redeemed once.
- **Rate Limiting**: Protects the verification endpoints from abuse.

## 📁 File Structure

```
/
├── app.py                    # Main Flask application with OAuth
├── google_auth_service.py    # Handles Google OAuth and Gmail API integration
├── coupon_manager.py         # Manages coupon generation and validation
├── csv_manager.py            # Handles all CSV file operations
├── email_service.py          # Fallback email sending functionality
├── encryption_service.py     # Provides encryption and decryption services
├── requirements.txt          # Python dependencies
├── setup.py                  # Setup script with OAuth instructions
├── .env.example              # Template for environment variables
├── templates/
│   ├── login.html            # Google OAuth login page
│   ├── sender.html           # Admin interface for sending campaigns
│   ├── scanner.html          # QR scanner interface for ticket verification
│   └── event.html            # HTML email template for the tickets
├── uploads/                  # Directory for uploaded CSV files
├── coupons.csv               # Database of generated coupons
└── sample_attendees.csv      # List of event attendees
```

## 🛠️ API Endpoints

- `POST /send-emails`: Send an email campaign to all recipients.
- `POST /verify-coupon`: Verify a QR coupon and mark it as used.
- `GET /coupon-status/<id>`: Check the status of a specific coupon.
- `POST /upload-csv`: Upload a CSV file with a list of recipients.
- `GET /stats`: Get the latest statistics for the system.

## 🧪 Testing

The system includes a suite of tests for all major components:

```bash
python test_encryption_service.py
python test_email_service.py
python test_csv_manager.py
```

## 🔧 Troubleshooting

### Google OAuth Issues

1.  **"Google OAuth is not configured" error**:
    *   Ensure that `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are correctly set in your `.env` file.
    *   Verify that the credentials are from the correct project in the Google Cloud Console.
    *   Make sure the Gmail API is enabled in your project.

2.  **"Authorization code not received" error**:
    *   Verify that the redirect URI in your Google Cloud Console (`http://localhost:5000/auth/callback` or your `ngrok` URL) matches the one in your `.env` file.
    *   Ensure that the OAuth consent screen is properly configured.
    *   If your Google project is in testing mode, make sure you have added the necessary test users.

3.  **"Failed to connect to Gmail API" error**:
    *   Check your internet connection.
    *   Verify that the Gmail API is enabled in the Google Cloud Console.
    *   Try logging out and back in to refresh the OAuth tokens.

### Common Issues

1.  **QR Scanner not working**:
    *   Ensure you are using a secure HTTPS connection (`ngrok` provides this).
    *   Check your browser's permissions for camera access.
    *   Use the manual verification option as a backup.
    *   Try using a different browser (Chrome is recommended).

2.  **Coupon verification fails**:
    *   Check that the `COUPON_SECRET_KEY` in your `.env` file is consistent.
    *   Verify that the email address matches the one on the ticket.
    *   Ensure that the coupon has not expired (it is valid for 24 hours).
    *   Check that the coupon has not already been used.

3.  **CSV upload fails**:
    *   Ensure that the CSV file has an `email` column header.
    *   Check the file size (the maximum is 16MB).
    *   Verify that the email addresses are properly formatted.
    *   Remove any special characters or extra spaces from the file.

## 📝 License

This project is open-source and is available under the **MIT License**.