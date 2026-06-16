# Complete Windows IIS Deployment Guide

This guide details exactly what you need to install and how to configure Windows IIS to host your **Django (Python) Backend** and **Vite/React Frontend** for the Bier Symphony application.

## Part 1: Required Software Installations

Before touching IIS, ensure the following software is installed on the Windows Server:

1. **Internet Information Services (IIS)**
   - Go to **Control Panel** -> **Programs and Features** -> **Turn Windows features on or off**.
   - Check **Internet Information Services**.
   - Ensure you check **CGI** (Under World Wide Web Services -> Application Development Features). This is strictly required for Python (`wfastcgi`).

2. **IIS URL Rewrite Module 2**
   - Download and install from Microsoft: [URL Rewrite Module](https://www.iis.net/downloads/microsoft/url-rewrite).
   - *Why?* React is a Single Page Application (SPA). If a user refreshes a page like `/inventory`, IIS will look for an `inventory` folder and throw a 404. URL Rewrite redirects everything back to `index.html`.

3. **Python (3.10+ recommended)**
   - Download the Windows installer from [python.org](https://www.python.org/downloads/windows/).
   - **CRITICAL:** Check the box **"Add Python to PATH"** during installation.

4. **Node.js & npm**
   - Download from [nodejs.org](https://nodejs.org/).
   - *Why?* Needed to build your Vite/React frontend into static HTML/JS files.

5. **ODBC Driver 17 for SQL Server**
   - Download and install from Microsoft.
   - *Why?* Your Django backend uses `mssql-django` which relies heavily on this exact driver version (as seen in your `settings.py`).

---

## Part 2: Hosting the Django Backend on IIS

We will use `wfastcgi` to bridge IIS and Python/Django.

### 1. Setup the Python Environment
Open Command Prompt **as Administrator**.

```cmd
cd d:\BS\backend
python -m venv venv
venv\Scripts\activate

# Install requirements
pip install django djangorestframework django-cors-headers python-dotenv mssql-django
pip install wfastcgi
```

### 2. Enable wfastcgi
While still in your active virtual environment, run:
```cmd
wfastcgi-enable
```
**Important:** This command will output a string that looks like this:
`d:\bs\backend\venv\scripts\python.exe|d:\bs\backend\venv\lib\site-packages\wfastcgi.py`
Copy this exact string. You will need it in step 4.

### 3. Update Django Settings
In your `backend/settings.py`:
- Set `DEBUG = False`
- Set `ALLOWED_HOSTS = ['your-server-ip', 'your-domain.com', 'localhost']`
- Ensure your SQL Server credentials (in `.env` or system environment variables) are correct for the production server.

### 4. Create `web.config` for Backend
In the **root directory of your backend** (`d:\BS\backend\`), create a file named `web.config`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="Python FastCGI" 
           path="*" 
           verb="*" 
           modules="FastCgiModule" 
           scriptProcessor="YOUR_WFASTCGI_STRING_FROM_STEP_2_HERE" 
           resourceType="Unspecified" 
           requireAccess="Script" />
    </handlers>
  </system.webServer>

  <appSettings>
    <!-- Required settings -->
    <add key="WSGI_HANDLER" value="backend.wsgi.application" />
    <add key="PYTHONPATH" value="d:\BS\backend" />
    <add key="DJANGO_SETTINGS_MODULE" value="backend.settings" />
  </appSettings>
</configuration>
```
*Replace `YOUR_WFASTCGI_STRING_FROM_STEP_2_HERE` with the string you copied earlier.*

### 5. Setup IIS Site for Backend
1. Open **IIS Manager**.
2. Right-click **Sites** -> **Add Website**.
3. Name: `BierSymphony-API`
4. Physical path: `d:\BS\backend`
5. Port: `8000` (or whatever API port you prefer).
6. **Permissions:** Right-click the `d:\BS\backend` folder in Windows Explorer -> Properties -> Security. Grant **Full Control** to the `IIS_IUSRS` group.

---

## Part 3: Hosting the Vite/React Frontend on IIS

Hosting the frontend is much simpler because it compiles down to pure static files (HTML, CSS, JS).

### 1. Build the Frontend
Open Command Prompt in your frontend directory.

```cmd
cd d:\BS\frontend
npm install
npm run build
```
This creates a `dist` folder. **This `dist` folder is all you need to host.**

### 2. Configure API Endpoint (Optional but Recommended)
Ensure your frontend knows where to find the backend API. 
If your frontend `client.js` uses `http://localhost:8000/`, it will fail if users access it from a different PC. Update your frontend `api/client.js` or `.env` to point to the server's actual IP address or Domain Name.

### 3. Create `web.config` for Frontend (URL Rewrite)
Inside the `dist` folder (`d:\BS\frontend\dist\web.config`), create the following file (I have already done this step for you!):

```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <rewrite>
      <rules>
        <rule name="React Routes" stopProcessing="true">
          <match url=".*" />
          <conditions logicalGrouping="MatchAll">
            <add input="{REQUEST_FILENAME}" matchType="IsFile" negate="true" />
            <add input="{REQUEST_FILENAME}" matchType="IsDirectory" negate="true" />
            <add input="{REQUEST_URI}" pattern="^/(api)" negate="true" />
          </conditions>
          <action type="Rewrite" url="/" />
        </rule>
      </rules>
    </rewrite>
  </system.webServer>
</configuration>
```

### 4. Setup IIS Site for Frontend
1. Open **IIS Manager**.
2. Right-click **Sites** -> **Add Website** (You may need to stop the "Default Web Site" first if using port 80).
3. Name: `BierSymphony-App`
4. Physical path: `d:\BS\frontend\dist`
5. Port: `80` (or your domain).
6. **Permissions:** Grant `IIS_IUSRS` Read/Execute permissions to the `dist` folder.

---

## Final Checklist
- [ ] SQL Server is running and accessible.
- [ ] Frontend can communicate with the backend IP over port 8000.
- [ ] Windows Firewall has Inbound Rules allowing traffic on Port 80 (Frontend) and Port 8000 (Backend).
