FROM python:3.10

WORKDIR /app

COPY requirements.txt .

RUN pip install -f requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "controller.payment_controller:app", "--host", "0.0.0.0"]