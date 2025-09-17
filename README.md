# Automated Coupon System

This is a web-based application designed to automate the process of generating, distributing, and verifying event coupons. The system allows an event organizer to upload a list of attendees, send them unique QR code coupons via email, and then verify those coupons in real-time at the event using a web-based scanner.

The application is built with Flask and uses Google OAuth for secure authentication, allowing the organizer to send emails directly from their own Gmail account.

## Features

- **Secure User Authentication**: Users log in securely with their Google account using OAuth 2.0.
- **Bulk Email Distribution**: Upload a CSV file of recipient emails and send customized coupon emails to everyone in a single batch.
- **Unique QR Code Generation**: For each recipient, a unique, encrypted QR code is generated.
- **Real-time Coupon Verification**: A web-based scanner interface allows staff to verify coupons instantly using a smartphone or any device with a camera.
- **Status Tracking**: The system tracks the status of each coupon (generated, sent, used).
- **Thank You Emails**: Automatically sends a "Thank You" email to an attendee upon successful verification.
- **Error Logging**: Automatically logs any emails that fail to send for later review.
- **Easy Deployment with Ngrok**: Includes helper scripts to easily expose the local server to the internet for testing and live use.

## How It Works

1.  **Login**: The event organizer logs into the system using their Google account.
2.  **Upload Recipients**: The organizer uploads a CSV file containing the email addresses of all event attendees.
3.  **Send Coupons**: The organizer initiates the email campaign. The system generates a unique coupon and QR code for each recipient and sends it to them using the organizer's authenticated Gmail account.
4.  **Event Day Verification**: At the event, staff can access the `/scanner` URL from their mobile devices.
5.  **Scan & Verify**: When an attendee presents their QR code, the staff member scans it. The system validates the coupon in real-time and marks it as "used" to prevent re-use.
6.  **Post-Verification**: Upon successful verification, the system automatically sends a thank-you email to the attendee.

## Getting Started

### Prerequisites

- Python 3.8+
- `pip` for installing dependencies
- `ngrok` for exposing the local server (for Google OAuth and mobile testing)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd automated_coupon_system
    ```

2.  **Create a virtual environment and activate it:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Configuration

1.  **Set up Google OAuth Credentials:**
    - Go to the [Google Cloud Console](https://console.cloud.google.com/).
    - Create a new project.
    - Navigate to "APIs & Services" > "Credentials".
    - Create an "OAuth client ID" for a "Web application".
    - Add `http://localhost:5000` to the "Authorized JavaScript origins".
    - Add `http://localhost:5000/auth/callback` to the "Authorized redirect URIs". You will update this later with your `ngrok` URL.
    - Download the client secret JSON file.

2.  **Create the `.env` file:**
    Create a file named `.env` in the root of the project. This file will hold all your secret keys and environment-specific settings.

    Below is the structure of the `.env` file. Fill in the values based on your setup.

    ```env
    # Flask Settings
    # ----------------
    # Set to True for development to enable debug mode, or False for production.
    FLASK_DEBUG=True
    # A long, random string used to secure sessions.
    SECRET_KEY=a-very-secret-key-that-you-should-change

    # Google OAuth Credentials
    # ------------------------
    # Get these from the Google Cloud Console after creating your OAuth client ID.
    GOOGLE_CLIENT_ID="YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com"
    GOOGLE_CLIENT_SECRET="YOUR_GOOGLE_CLIENT_SECRET"
    # The initial redirect URI. The start_with_ngrok.sh script will update this automatically.
    GOOGLE_REDIRECT_URI="http://localhost:5000/auth/callback"

    # Encryption Key for Coupons
    # --------------------------
    # A 32-byte (64 hex characters) key for encrypting coupon data.
    # Generate a secure key and keep it safe.
    ENCRYPTION_KEY=your-32-byte-encryption-key-keep-safe
    ```

    **How to Generate Secure Keys:**

    -   **`SECRET_KEY`**: You can generate a suitable key in your terminal with:
        ```bash
        python -c 'import secrets; print(secrets.token_hex(24))'
        ```
    -   **`ENCRYPTION_KEY`**: This key **must** be 32 bytes long. Generate it with:
        ```bash
        python -c 'import secrets; print(secrets.token_hex(32))'
        ```


### Running the Application

1.  **Start `ngrok`:**
    To allow Google to redirect back to your local machine and to test on mobile, you need a public URL. This project is set up to work with `ngrok`.

    The included script simplifies this process. Run:
    ```bash
    ./start_with_ngrok.sh
    ```
    This will start an `ngrok` tunnel and display a public HTTPS URL (e.g., `https://<random-string>.ngrok.io`).

2.  **Update Google Cloud Console:**
    - Go back to your Google Cloud project credentials.
    - Add the `ngrok` URL to your "Authorized redirect URIs". It should look like this: `https://<random-string>.ngrok.io/auth/callback`.

3.  **Start the Flask Application:**
    In a new terminal (while `ngrok` is still running), make sure your virtual environment is activated and run:
    ```bash
    python app.py
    ```

4.  **Access the Application:**
    Open your browser and navigate to the `ngrok` URL provided. You can now log in and start using the application.

## Project Structure

\`\`\`
/
├── app.py # Main Flask application
├── coupon_manager.py # Handles coupon generation and validation
├── csv_manager.py # Manages data storage in CSV files
├── google_auth_service.py # Handles Google OAuth and Gmail API
├── encryption_service.py # Encrypts and decrypts coupon data
├── requirements.txt # Python dependencies
├── start_with_ngrok.sh # Script to start ngrok tunnel
├── templates/
│ ├── login.html
│ ├── sender.html # Main dashboard for sending coupons
│ └── scanner.html # QR code scanner interface
└── static/ # CSS and JavaScript files
\`\`\`
