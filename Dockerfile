# Use official Microsoft Playwright Python base image with all Linux browser dependencies included
FROM mcr.microsoft.com/playwright/python:v1.45.0-jammy

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PORT=10000

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Ensure Chromium browser is installed and configured
RUN playwright install chromium

# Copy application files
COPY app.py .
COPY parivesh_api.py .
COPY parivesh_engine.py .
COPY ui_components.py .
COPY captcha_solver.py .
COPY captcha_model.onnx .
COPY captcha_model.onnx.data .
COPY parivesh_activities.json .

# Expose Render default port
EXPOSE 10000

# Start Streamlit application
CMD ["sh", "-c", "streamlit run app.py --server.port=${PORT:-10000} --server.address=0.0.0.0 --server.headless=true --server.enableCORS=false --server.enableXsrfProtection=false"]
