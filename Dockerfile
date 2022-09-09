FROM python:3.10.4-slim-bullseye

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

ADD . .

CMD [ "python", "./src/run.py", "-p", "order_product", "-d", "bpmn/product_prices.dmn", "bpmn/shipping_costs.dmn", "-b", "bpmn/multiinstance.bpmn", "bpmn/call_activity_multi.bpmn" ]
