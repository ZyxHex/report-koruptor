from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "credit": "@spideyabd",
        "message": "Welcome to Number Info & Report API",
        "endpoints": {
            "/info": "?number=PHONE_NUMBER",
            "/report": "?number=PHONE_NUMBER&message=YOUR_MESSAGE"
        }
    })

@app.route('/info', methods=['GET'])
def number_info():
    phone_number = request.args.get('number')
    if not phone_number:
        return jsonify({"credit": "@spideyabd", "error": "Please provide ?number= parameter"}), 400

    if not phone_number.isdigit() and not (phone_number.startswith('+') and phone_number[1:].isdigit()):
        return jsonify({"credit": "@spideyabd", "error": "Invalid phone number format"}), 400

    try:
        url = "https://calltracer.in"
        headers = {
            "Host": "calltracer.in",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        payload = {
            "country": "IN",
            "q": phone_number
        }

        resp = requests.post(url, headers=headers, data=payload, timeout=10)
        if resp.status_code != 200:
            return jsonify({"credit": "@spideyabd", "error": f"Failed to fetch data. HTTP {resp.status_code}"}), 502

        soup = BeautifulSoup(resp.text, 'html.parser')
        table = soup.find('table', class_='trace-details')
        if not table:
            return jsonify({"credit": "@spideyabd", "error": "No details table found"}), 500

        data = {}
        current_label = None
        rowspan_count = 0

        for row in table.find_all('tr'):
            tds = row.find_all('td')
            if not tds:
                continue

            if tds[0].has_attr('colspan'):
                continue

            if len(tds) == 2:
                label_cell = tds[0]
                value_cell = tds[1]
                label = label_cell.get_text(strip=True).rstrip(':')
                value = value_cell.get_text(separator=' ', strip=True)

                if not value:
                    continue

                if label_cell.has_attr('rowspan'):
                    current_label = label
                    rowspan_count = int(label_cell['rowspan']) - 1
                else:
                    current_label = label
                    rowspan_count = 0

                if label in data:
                    if not isinstance(data[label], list):
                        data[label] = [data[label]]
                    data[label].append(value)
                else:
                    data[label] = value

            elif len(tds) == 1 and current_label:
                value = tds[0].get_text(separator=' ', strip=True)
                if not value:
                    continue
                if current_label in data:
                    if not isinstance(data[current_label], list):
                        data[current_label] = [data[current_label]]
                    data[current_label].append(value)
                else:
                    data[current_label] = value
                rowspan_count -= 1
                if rowspan_count == 0:
                    current_label = None

        data['Number'] = f"+91-{phone_number}" if not phone_number.startswith('+') else phone_number

        clean_data = {}
        for key, value in data.items():
            if isinstance(value, list):
                filtered = [v for v in value if v.strip()]
                if len(filtered) == 1:
                    clean_data[key] = filtered[0]
                else:
                    clean_data[key] = filtered
            elif value and value.strip():
                clean_data[key] = value

        result = {"credit": "@spideyabd"}
        result.update(clean_data)
        return jsonify(result)

    except Exception as e:
        return jsonify({"credit": "@spideyabd", "error": str(e)}), 500

@app.route('/report', methods=['GET'])
def report_number():
    number = request.args.get('number')
    message = request.args.get('message', '')

    if not number:
        return jsonify({"credit": "@spideyabd", "error": "Please provide ?number= parameter"}), 400
    if not message:
        return jsonify({"credit": "@spideyabd", "error": "Please provide ?message= parameter"}), 400

    scam = request.args.get('scam', '0')
    blackmail = request.args.get('blackmail', '0')
    harass = request.args.get('harass', '0')
    marketing = request.args.get('marketing', '0')

    payload = {
        'number': number,
        'country': 'IN',
        'prefix': '91',
        'scam': '1' if scam == '1' else '',
        'blackmail': '1' if blackmail == '1' else '',
        'harass': '1' if harass == '1' else '',
        'marketing': '1' if marketing == '1' else '',
        'message': message,
        'mask': '1',
        'button': 'Submit'
    }

    for key in ['scam', 'blackmail', 'harass', 'marketing']:
        if payload[key] == '':
            del payload[key]

    headers = {
        "Host": "calltracer.in",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": f"https://calltracer.in/in/{number}/"
    }

    try:
        resp = requests.post('https://calltracer.in/', headers=headers, data=payload, timeout=10)
        if resp.status_code == 200:
            return jsonify({
                "credit": "@spideyabd",
                "status": "success",
                "message": f"Report submitted for {number}",
                "details": "Complaint registered."
            })
        else:
            return jsonify({"credit": "@spideyabd", "error": f"Failed to submit report. HTTP {resp.status_code}"}), 502
    except Exception as e:
        return jsonify({"credit": "@spideyabd", "error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
