# E-Signature Management System (Portfolio Demo)

## Overview

This project is a **simplified demo version** of a full-featured E-Signature Management System that I originally developed as an in-house solution. This version is designed specifically for my portfolio to demonstrate my skills in web application development, database integration, and user authentication.

The application allows users to upload documents, manage employees, assign and collect electronic signatures, and view signed documents—all through a modern web interface.

**Key Features:**
- User authentication (login/logout)
- Role-based dashboards (Boss/Admin and Employee)
- Document upload, viewing, and management
- Electronic signature capture and placement
- One-click signing (auto-placement of default signatures)
- Draw or upload your signature or initials in the Signature Manager
- Employee management (add, view, and manage employees)
- Signature management (upload, assign, and manage signatures)
- Email notifications (for demonstration; see note below)
- Simple, responsive UI

**Signature Features Explained:**

- **One-Click Signing:**
  - For documents where signature positions are pre-defined, users can sign the document instantly with a single click. The system automatically places the user's default signature(s) at the required locations, streamlining the signing process for standard forms and agreements.

- **Manual Signing:**
  - For documents that require custom signature placement, users can manually select where to place their signature(s) on the document. This allows for flexibility when dealing with non-standard documents or when multiple types of signatures (e.g., initials, company stamp) are needed in different locations.

- **Default Signature:**
  - Each user can upload and manage multiple signatures (such as a full signature, initials, or company stamp). Users can set one signature as their default for each type. The default signature is automatically used during one-click signing, ensuring a fast and consistent signing experience.
- **Signature Manager:**
  - In the Signature Manager, you can either draw your signature/initials using your mouse or touchscreen, or upload an image file of your signature/initials.

---

## Cloning the Repository on Windows

To get started on Windows, you need to clone the repository to your computer using the **Command Prompt**:

### Using Command Prompt
1. Make sure Git is installed and added to your PATH (run `git --version` to check).
2. Open **Command Prompt** (Win+R, type `cmd`, press Enter).
3. Run:
   ```cmd
   git clone https://github.com/Ridhwaan-Jogiat/E-sign-System.git
   cd EsignProjectV2
   ```

---

## Quick Start

### 1. Clone the Repository

If you haven't already, follow the steps above to clone the repository to your computer.

### 2. Create and Activate a Virtual Environment

#### On Windows Command Prompt (cmd)
```cmd
python -m venv venv
venv\Scripts\activate
```

#### On Linux/macOS or Git Bash
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

#### On Windows Command Prompt (cmd)
```cmd
pip install -r requirements.txt
```

#### On Linux/macOS or Git Bash
```bash
pip install -r requirements.txt
```

### 4. Initialize the Database

The app uses SQLite for simplicity. On first run, it will automatically create the database (`instance/app.db`) and populate it with default users for demonstration.

### 4. (Optional) Add Your Own Boss Account

If you wish to add your own boss (admin) account, run the following command and follow the prompts **before** you run the application:

```cmd
python -m app.setup_admin
```

This will guide you through creating a boss account with your own credentials.

**Note:** If you create your own boss account using this script, the default boss account (`boss@example.com` / `password`) will **not** be created automatically. Only your custom boss account will exist.

### 5. Run the Application

```bash
python run.py
```

The app will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000).

---

## How to Set Your Default Signature

1. Log in to the app and go to the "Manage Signature" page (usually found in the navigation bar).
2. Upload your signature(s), initials, or company signature as needed.
3. Next to each uploaded signature, click the "Set as Default" button for the type you want to use as your default (Full Signature, Initials, or Company Signature).
4. The default signature for each type will be used for one-click signing and will be pre-selected in manual signing.

---

## Important Note About Email Notifications

This demo project includes a fully functional email notification system (for actions such as user onboarding and document status updates). However, **email notifications will not work out-of-the-box in this public repository** because the required email credentials (such as SMTP username and password) are not included for security reasons.

If you wish to test the email features, you will need to:
1. Create a `.env` file in the project root.
2. Add your own email SMTP credentials, for example:
    ```
    MAIL_SERVER=smtp.gmail.com
    MAIL_PORT=587
    MAIL_USE_TLS=true
    MAIL_USERNAME=your_email@gmail.com
    MAIL_PASSWORD=your_email_password
    ```
3. Ensure "less secure app access" is enabled for your email provider, or use an app password if using Gmail with 2FA.

**For demonstration and review purposes, all other features will work without email configuration.**  
You can log in with the default users and explore the document upload, signature, and management features.

---

## Default Demo Users

- **Boss/Admin**
   - Username: `boss@example.com'`
   - Password: `password`
- **Employee**
   - Username: `employee@example.com`
   - Password: `password`

*If you create your own boss account using the setup script, the above default boss account will NOT be created.*

---

## Notes

- This project is a **watered-down demo** for portfolio purposes only.
- SQLite is used for ease of setup; in production, a more robust database (e.g., PostgreSQL) is recommended.
- Only default users are created automatically for quick testing; no additional demo data is included.
- No sensitive data is stored; feel free to experiment with uploads and signatures.

---

## Screenshots

### Boss Dashboard
![Boss Dashboard](https://i.imgur.com/ogaN6sZ.png)

## License

This project is for portfolio and demonstration use only. 