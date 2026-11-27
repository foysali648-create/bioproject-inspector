FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY bioproject_inspector ./bioproject_inspector
RUN pip install --no-cache-dir ".[web]"
EXPOSE 7860
CMD ["uvicorn", "bioproject_inspector.web:app", "--host", "0.0.0.0", "--port", "7860"]
