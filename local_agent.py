from flask import Flask, jsonify, request
import screen_brightness_control as sbc

app = Flask(__name__)


def clamp_brightness(value):
    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        numeric_value = 0
    return max(0, min(100, int(round(numeric_value))))


@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
    return response


@app.route('/health', methods=['GET', 'OPTIONS'])
def health():
    if request.method == 'OPTIONS':
        return ('', 204)
    return jsonify(status='ok')


@app.route('/brightness', methods=['GET', 'POST', 'OPTIONS'])
def brightness():
    if request.method == 'OPTIONS':
        return ('', 204)

    if request.method == 'GET':
        try:
            current_value = sbc.get_brightness()
            if isinstance(current_value, list):
                current_value = current_value[0]
            return jsonify(brightness=clamp_brightness(current_value))
        except Exception as exc:
            return jsonify(error=str(exc)), 500

    data = request.get_json(silent=True) or {}
    brightness_value = clamp_brightness(data.get('brightness', 0))

    try:
        sbc.set_brightness(brightness_value)
        return jsonify(ok=True, brightness=brightness_value)
    except Exception as exc:
        return jsonify(error=str(exc)), 500


if __name__ == '__main__':
    print('Local brightness agent running on http://127.0.0.1:5055')
    app.run(host='127.0.0.1', port=5055, debug=False)