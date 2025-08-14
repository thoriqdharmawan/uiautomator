import subprocess
import time

import requests
from flask import Flask, jsonify, request
from uiautomator import Device

app = Flask(__name__)
d = Device()


# @app.route("/trigger_n8n", methods=["POST"])
# def trigger_n8n():
#     n8n_webhook_url = "https://n8n.aturuang.xyz/webhook-test/open_shopee"
#     payload = {"action": "open_shopee"}
#     try:
#         print(f"Sending request to: {n8n_webhook_url}")
#         print(f"Payload: {payload}")
#         r = requests.post(n8n_webhook_url, json=payload, timeout=10)
#         print(f"Response status: {r.status_code}")
#         print(f"Response text: {r.text}")
#         return jsonify(
#             {
#                 "status": "n8n webhook hit",
#                 "response_code": r.status_code,
#                 "response_text": r.text,
#                 "url": n8n_webhook_url,
#             }
#         )
#     except Exception as e:
#         return jsonify({"status": "failed", "error": str(e)})


# @app.route("/open_shopee_v2", methods=["POST"])
# def open_shopee_v2():
#     d.screen.on()
#     d.press.home()
#     time.sleep(1)

#     d(text="Shopee").click()
#     time.sleep(5)

#     return jsonify({"status": "Shopee app opened"})


@app.route("/open_shopee", methods=["GET"])
def open_shopee():
    try:
        subprocess.run(
            ["am", "start", "-n", "com.shopee.id/com.shopee.app.ui.home.HomeActivity_"],
            check=True,
        )

        return jsonify({"status": "success", "message": "Shopee dibuka"})
    except subprocess.CalledProcessError as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/open_atur_uang", methods=["POST"])
def open_atur_uang():
    """Only opens the Atur Uang app"""
    try:
        subprocess.run(
            ["am", "start", "-n", "com.aturuang/.MainActivity"],
            check=True,
        )
        time.sleep(5)
        return jsonify({"status": "success", "message": "Atur Uang app opened"})
    except subprocess.CalledProcessError as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/wait_for_login", methods=["POST"])
def wait_for_login():
    """Waits for user to complete login in Atur Uang app"""
    try:
        while not d(text="Masuk").exists:
            time.sleep(1)

        login_attempts = 0
        max_wait_time = 300

        while d(text="Masuk").exists and login_attempts < max_wait_time:
            time.sleep(1)
            login_attempts += 1

        if login_attempts >= max_wait_time:
            return jsonify(
                {
                    "status": "timeout",
                    "message": "Login timeout - user took too long to login",
                }
            )

        time.sleep(3)
        return jsonify({"status": "success", "message": "User successfully logged in"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/click_ai_chatbot", methods=["POST"])
def click_ai_chatbot():
    """Finds and clicks the AI Chatbot button"""
    try:
        chatbot_wait_attempts = 0
        max_chatbot_wait = 60

        while (
            not d(text="AI Chatbot").exists and chatbot_wait_attempts < max_chatbot_wait
        ):
            time.sleep(1)
            chatbot_wait_attempts += 1

        if d(text="AI Chatbot").exists:
            d(text="AI Chatbot").click()
            return jsonify(
                {"status": "success", "message": "AI Chatbot clicked successfully"}
            )
        else:
            return jsonify(
                {
                    "status": "timeout",
                    "message": "AI Chatbot button not found after waiting",
                }
            )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/full_atur_uang_flow", methods=["POST"])
def full_atur_uang_flow():
    """Complete flow: opens app, waits for login, and clicks AI Chatbot"""
    try:
        subprocess.run(
            ["am", "start", "-n", "com.aturuang/.MainActivity"],
            check=True,
        )
        time.sleep(5)

        while not d(text="Masuk").exists:
            time.sleep(1)

        login_attempts = 0
        max_wait_time = 300

        while d(text="Masuk").exists and login_attempts < max_wait_time:
            time.sleep(1)
            login_attempts += 1

        if login_attempts >= max_wait_time:
            return jsonify(
                {
                    "status": "timeout",
                    "message": "Login timeout - user took too long to login",
                }
            )

        time.sleep(3)

        chatbot_wait_attempts = 0
        max_chatbot_wait = 60

        while (
            not d(text="AI Chatbot").exists and chatbot_wait_attempts < max_chatbot_wait
        ):
            time.sleep(1)
            chatbot_wait_attempts += 1

        if d(text="AI Chatbot").exists:
            d(text="AI Chatbot").click()
            return jsonify(
                {
                    "status": "success",
                    "message": "Complete flow: Atur Uang opened, user logged in, and AI Chatbot clicked",
                }
            )
        else:
            return jsonify(
                {
                    "status": "timeout",
                    "message": "AI Chatbot not found after waiting for user login",
                }
            )
    except subprocess.CalledProcessError as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok - v1"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
