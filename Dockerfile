FROM python:3.9-slim

WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files
COPY main.py .
COPY utils.py .
COPY step1_upload.py .
COPY step2_review.py .
COPY step3_scrape.py .
COPY step4_select.py .
COPY step5_notify.py .

# Copy Streamlit configuration
COPY .streamlit/config.toml /root/.streamlit/config.toml

# Expose the port Streamlit runs on
EXPOSE 8501
ENV STREAMLIT_SERVER_ENABLE_WEBSOCKET_COMPRESSION=false
ENV STREAMLIT_SERVER_ENABLE_WEBSOCKET_CONNECTIONS=false
ENV STREAMLIT_SERVER_BASE_URL_PATH=house-frontend

# Run the app with no WebSocket connections
# Run the app with the base URL path but no WebSocket connections
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.baseUrlPath=house-frontend"]