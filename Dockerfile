FROM python:3.9

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Add environment variables
ENV STRIPE_PUBLIC_KEY="your_stripe_public_key_here"
ENV STRIPE_SECRET_KEY="your_stripe_secret_key_here"

# Create database migrations and apply them
RUN python manage.py makemigrations
RUN python manage.py migrate

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "bookstore.wsgi:application"] 