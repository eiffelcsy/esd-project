FROM python:3-slim
WORKDIR /finance
COPY finance-requirements.txt .
RUN pip install --no-cache-dir -r finance-requirements.txt
COPY . .
CMD ["python", "finance.py"] 