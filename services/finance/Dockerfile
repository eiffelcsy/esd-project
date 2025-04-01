FROM python:3-slim
WORKDIR /finance/finance_service
COPY finance-requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "finance_app.py"] 