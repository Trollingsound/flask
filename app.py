from flask import Flask, render_template , request, jsonify
import requests

app = Flask(__name__)

@app.route("/", methods=["POST", "GET"])
def start():
    if request.method == "POST":
        r = requests.get('https://whoer.net/en/main/api/ip') 
        return jsonify({"ip":r.json() , "request_body": request.json})
    else:
        return "<h1> sab sahi hai :) </h1>"

@app.route('/api', methods=['GET'])
def api():
    start_time = time.time()

    cards = request.args.get("lista", "")
    mode = request.args.get("mode", "cvv")
    amount = int(request.args.get("amount", 1))
    currency = request.args.get("currency", "usd")

    if not cards:
        return "Please enter card details"

    card_list = cards.split(",")
    results = []

    pk = 'pk_live_51HfBwmD4mk8ECiEaK52fL9vngrRWrLNtA0N2LEC9OGWMd15vtAyz2fFeKMXXWT61L5JlAZs5tePyOefl6YrXvXtc00WGdR32ky'
    sk = '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'

    for card in card_list:
        split = card.split("|")
        cc = split[0] if len(split) > 0 else ''
        mes = split[1] if len(split) > 1 else ''
        ano = split[2] if len(split) > 2 else ''
        cvv = split[3] if len(split) > 3 else ''

        if not cc or not mes or not ano or not cvv:
            results.append(f"Invalid card details for {card}")
            continue

        token_data = {
            'card[number]': cc,
            'card[exp_month]': mes,
            'card[exp_year]': ano,
            'card[cvc]': cvv
        }

        response = requests.post(
            'https://api.stripe.com/v1/tokens',
            data=token_data,
            headers={
                'Authorization': f'Bearer {pk}',
                'Content-Type': 'application/x-www-form-urlencoded',
            }
        )

        if response.status_code != 200:
            results.append(f"Error: {response.json().get('error', {}).get('message', 'Unknown error')} for {card}")
            continue

        token_data = response.json()
        token_id = token_data.get('id', '')

        if not token_id:
            results.append(f"Token creation failed for {card}")
            continue

        charge_data = {
            'amount': amount * 100,
            'currency': currency,
            'source': token_id,
            'description': 'Charge for product/service'
        }

        response = requests.post(
            'https://api.stripe.com/v1/charges',
            data=charge_data,
            headers={
                'Authorization': f'Bearer {sk}',
                'Content-Type': 'application/x-www-form-urlencoded',
            }
        )

        chares = response.json()
        end_time = time.time()
        elapsed_time = round(end_time - start_time, 2)

        if response.status_code == 200 and chares.get('status') == "succeeded":
            status = "CHARGED"
            resp = "Charged successfully ✅"
        elif "Your card's security code is incorrect." in json.dumps(chares):
            status = "LIVE"
            resp = "CCN LIVE✅"
        elif 'insufficient funds' in json.dumps(chares) or 'Insufficient Funds' in json.dumps(chares):
            status = "LIVE"
            resp = "insufficient funds✅"
        else:
            status = "Declined ❌️"
            resp = chares.get('error', {}).get('decline_code', chares.get('error', {}).get('message', 'Unknown error'))

        results.append(f"{status}-->{card}-->[{resp}]")

    return "<br>".join(results)

@app.route("/mbsa")
def mbsa():
    return render_template('index.html')
