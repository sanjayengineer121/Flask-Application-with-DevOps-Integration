FROM python:3.9-slim

ENV FLASK_APP=your_flask_app.py
ENV FLASK_RUN_HOST=0.0.0.0

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["flask", "run"]
