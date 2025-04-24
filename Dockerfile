FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN if [ ! -f /home/db.sqlite3 ]; then cp /app/db.sqlite3 /home/db.sqlite3; fi

Add environment variables
ENV STRIPE_PUBLIC_KEY="your_stripe_public_key_here"
ENV STRIPE_SECRET_KEY="your_stripe_secret_key_here"

RUN python manage.py makemigrations
RUN python manage.py migrate

RUN python manage.py collectstatic --noinput

Expose port
EXPOSE 8000

Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "bookstore.wsgi:application"]