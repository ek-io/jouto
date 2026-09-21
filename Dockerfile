# Use the official Microsoft Playwright image (includes all browser dependencies)
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Ensure Chromium is installed for Playwright
RUN playwright install chromium

# Copy the rest of the application
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Command to run the application
CMD ["streamlit", "run", "app/Dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
