FROM python:3.10-slim

# Hugging Face Spaces runs the app as user 1000, so we do the same everywhere.
# Then CI tests the image exactly the way the Space will run it
RUN useradd -m -u 1000 user

WORKDIR /app

# Install packages first, so changing the code does not reinstall them
COPY pyproject.toml .
RUN pip install --no-cache-dir .

COPY --chown=user src ./src
COPY --chown=user model ./model

USER user
ENV HOME=/home/user

EXPOSE 8000
CMD ["uvicorn", "serve:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8000"]
