FROM python:3.11-slim
WORKDIR /app
RUN pip install Flask PyMySQL
COPY . .
CMD ["flask", "run", "--host=0.0.0.0"]
