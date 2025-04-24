FROM python:3.9

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app

# Add environment variables
ENV STRIPE_PUBLIC_KEY="your_stripe_public_key_here"
ENV STRIPE_SECRET_KEY="your_stripe_secret_key_here"

# Create data directory for persistent storage
RUN mkdir -p /home/data

# Make startup script executable
RUN chmod +x startup.sh

# Expose port
EXPOSE 8000

# Use our startup script
CMD ["./startup.sh"]