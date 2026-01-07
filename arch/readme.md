docker build -t docx-render-api .
mkdir -p ./out

docker run --rm -p 8000:8000 \
  -v "$PWD/out:/data/out" \
  docx-render-api

  curl -X POST "http://localhost:8000/render" \
  -F "template=@./template.docx" \
  -F 'payload_json={
    "client":{"name":"Mateusz","surname":"Gladczak"},
    "amount":"123.45",
    "annotations":"zażółć gęślą jaźń",
    "send_email": true,
    "email": {
      "to": "recipient@example.com",
      "subject": "Test notification",
      "body": "Twoje dokumenty zostały wygenerowane."
    }
  }' \
  -F "output_path=invoices/2025-12/invoice-0001"

DOCX musi mieć placeholdery np. {{ client.name }}, {{ amount }}

•	Swagger UI (interaktywne): http://<host>:8000/docs
•	ReDoc: http://<host>:8000/redoc