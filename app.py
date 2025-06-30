#npx localtunnel --port 5000

from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

API_KEY = "acdd8e383d155fc787b93fb1"  # Replace with your actual key

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return "✅ Webhook is live! Use POST requests to interact with Dialogflow."

    # Get JSON payload from Dialogflow
    req = request.get_json()
    print("🔧 Received JSON from Dialogflow:")
    print(req)

    try:
        # Extract values from Dialogflow parameters
        source_currency = req['queryResult']['parameters']['unit-currency']['currency']
        amount = req['queryResult']['parameters']['unit-currency']['amount']
        target_currency = req['queryResult']['parameters']['currency-name']

        print(f"Received: {amount} {source_currency} to {target_currency}")

        # Call ExchangeRate API with dynamic source currency
        url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{source_currency.upper()}"
        response = requests.get(url)
        data = response.json()

        # Check for API success
        if data['result'] != 'success':
            return jsonify({"fulfillmentText": "Sorry, I couldn't fetch the exchange rate."})

        # Get conversion rate to target currency
        conversion_rates = data['conversion_rates']
        if target_currency.upper() not in conversion_rates:
            return jsonify({"fulfillmentText": f"Sorry, I can't convert to {target_currency.upper()}."})

        rate = conversion_rates[target_currency.upper()]
        converted_amount = float(amount) * rate

        reply = f"{amount} {source_currency.upper()} is equal to {converted_amount:.2f} {target_currency.upper()}."

        return jsonify({"fulfillmentText": reply})

    except Exception as e:
        print("Error:", e)
        return jsonify({"fulfillmentText": "Sorry, there was an error processing your request."})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
