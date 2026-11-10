FROM python:3.10-slim

WORKDIR /app

# Install packages first, so changing the code does not reinstall them
COPY pyproject.toml .
RUN pip install --no-cache-dir .

COPY src ./src
COPY model ./model

EXPOSE 8000
CMD ["uvicorn", "serve:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8000"]
