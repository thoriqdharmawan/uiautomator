import subprocess
import time

import requests
from flask import Flask, jsonify, request
from uiautomator import Device

app = Flask(__name__)
d = Device()


def check_premium_membership():
    """Check if user is a premium member by looking for 'Keanggotaan Premium' text"""
    if d(text="Keanggotaan Premium").exists:
        return {
            "is_premium_member": False,
            "message": "User is not a premium member - Keanggotaan Premium text found",
        }
    else:
        return {
            "is_premium_member": True,
            "message": "User is a premium member - Keanggotaan Premium text not found",
        }


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
        time.sleep(1)

        if d(text="Login").exists:
            return jsonify(
                {
                    "status": "success",
                    "logged_in": False,
                    "message": "User is not logged in - Login text found",
                }
            )
        else:
            return jsonify(
                {
                    "status": "success",
                    "logged_in": True,
                    "message": "User is already logged in - No Login text found",
                }
            )
    except subprocess.CalledProcessError as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/wait_for_login", methods=["POST"])
def wait_for_login():
    """Waits for user to complete login in Atur Uang app"""
    try:
        while not d(text="Login").exists:
            time.sleep(1)

        login_attempts = 0
        max_wait_time = 300

        while d(text="Login").exists and login_attempts < max_wait_time:
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
            time.sleep(1)

            wait_attempts = 0
            max_wait = 30

            while d(text="AI Chatbot").exists and wait_attempts < max_wait:
                time.sleep(1)
                wait_attempts += 1

            if wait_attempts >= max_wait:
                return jsonify(
                    {
                        "status": "timeout",
                        "message": "AI Chatbot text still visible after clicking - page may not have loaded",
                    }
                )

            time.sleep(2)

            premium_status = check_premium_membership()

            return jsonify({"status": "success", **premium_status})
        else:
            return jsonify(
                {
                    "status": "timeout",
                    "message": "AI Chatbot button not found after waiting",
                }
            )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/click_mulai_berlangganan", methods=["POST"])
def click_mulai_berlangganan():
    """Clicks the 'Mulai Berlangganan' button and then the 'Langganan' button"""
    try:
        if d(text="Mulai Berlangganan").exists:
            d(text="Mulai Berlangganan").click()
            time.sleep(4)

            if d(text="Langganan").exists:
                d(text="Langganan").click()
                time.sleep(2)

                return jsonify(
                    {
                        "status": "success",
                        "message": "Successfully clicked 'Mulai Berlangganan' and 'Langganan' buttons",
                    }
                )
            else:
                return jsonify(
                    {
                        "status": "not_found",
                        "message": "'Langganan' button not found after clicking 'Mulai Berlangganan'",
                    }
                )
        else:
            return jsonify(
                {
                    "status": "not_found",
                    "message": "'Mulai Berlangganan' button not found",
                }
            )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/check_premium_status", methods=["GET"])
def check_premium_status():
    """Check if user is a premium member"""
    try:
        premium_status = check_premium_membership()
        return jsonify({"status": "success", **premium_status})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/confirm_subscription", methods=["POST"])
def confirm_subscription():
    """Confirms subscription by waiting for 'Langganan' text to disappear"""
    try:
        wait_attempts = 0
        max_wait = 30

        while d(text="Langganan").exists and wait_attempts < max_wait:
            time.sleep(1)
            wait_attempts += 1

        if not d(text="Langganan").exists:
            time.sleep(2)

            screen_info = d.info
            screen_width = screen_info["displayWidth"]
            tap_x = screen_width // 2
            tap_y = 200

            d.click(tap_x, tap_y)
            time.sleep(1)

            return jsonify(
                {
                    "status": "success",
                    "message": "Successfully subscribed and closed success drawer - 'Langganan' text disappeared",
                }
            )
        else:
            return jsonify(
                {
                    "status": "timeout",
                    "message": "Timeout waiting for 'Langganan' text to disappear",
                }
            )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/write_breakfast_expense", methods=["POST"])
def write_breakfast_expense():
    """Write 'Breakfast 10000' in the available text field"""
    try:
        text_field = None

        if d(className="android.widget.EditText").exists:
            text_field = d(className="android.widget.EditText")
        elif d(resourceId="com.aturuang:id/editText").exists:
            text_field = d(resourceId="com.aturuang:id/editText")
        elif d(resourceId="com.aturuang:id/et_expense").exists:
            text_field = d(resourceId="com.aturuang:id/et_expense")
        elif d(resourceId="com.aturuang:id/input").exists:
            text_field = d(resourceId="com.aturuang:id/input")
        elif (
            d(text="").exists
            and d(text="").info.get("className") == "android.widget.EditText"
        ):
            text_field = d(text="")

        if text_field and text_field.exists:
            text_field.clear_text()
            time.sleep(0.5)
            text_field.set_text("Breakfast 10000")
            time.sleep(1)

            return jsonify(
                {
                    "status": "success",
                    "message": "Successfully wrote 'Breakfast 10000' in text field",
                }
            )
        else:
            return jsonify(
                {
                    "status": "not_found",
                    "message": "No text field found on current screen",
                }
            )

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/click_submit_button", methods=["POST"])
def click_submit_button():
    """Click the submit/arrow button next to text field (React Native Pressable icon)"""
    try:
        text_field = None

        if d(className="android.widget.EditText").exists:
            text_field = d(className="android.widget.EditText")
        elif d(resourceId="com.aturuang:id/editText").exists:
            text_field = d(resourceId="com.aturuang:id/editText")
        elif d(resourceId="com.aturuang:id/et_expense").exists:
            text_field = d(resourceId="com.aturuang:id/et_expense")
        elif d(resourceId="com.aturuang:id/input").exists:
            text_field = d(resourceId="com.aturuang:id/input")

        if not text_field or not text_field.exists:
            return jsonify(
                {
                    "status": "not_found",
                    "message": "No text field found for reference positioning",
                }
            )

        submit_button = None

        text_field_bounds = text_field.info.get("bounds", {})
        text_field_right = text_field_bounds.get("right", 0)
        text_field_top = text_field_bounds.get("top", 0)
        text_field_bottom = text_field_bounds.get("bottom", 0)
        text_field_center_y = (text_field_top + text_field_bottom) // 2

        if d(className="android.view.ViewGroup").exists:
            viewgroups = d(className="android.view.ViewGroup")
            for vg in viewgroups:
                vg_bounds = vg.info.get("bounds", {})
                vg_left = vg_bounds.get("left", 0)
                vg_top = vg_bounds.get("top", 0)
                vg_bottom = vg_bounds.get("bottom", 0)
                vg_center_y = (vg_top + vg_bottom) // 2

                if (
                    vg_left >= text_field_right - 50
                    and abs(vg_center_y - text_field_center_y) < 50
                ):
                    submit_button = vg
                    break

        if not submit_button:
            if d(className="android.widget.ImageButton").exists:
                submit_button = d(className="android.widget.ImageButton")
            elif d(className="android.widget.ImageView").exists:
                imageviews = d(className="android.widget.ImageView")
                for iv in imageviews:
                    iv_bounds = iv.info.get("bounds", {})
                    iv_left = iv_bounds.get("left", 0)
                    iv_top = iv_bounds.get("top", 0)
                    iv_bottom = iv_bounds.get("bottom", 0)
                    iv_center_y = (iv_top + iv_bottom) // 2

                    if (
                        iv_left >= text_field_right - 50
                        and abs(iv_center_y - text_field_center_y) < 50
                    ):
                        submit_button = iv
                        break
            elif d(className="android.widget.Button").exists:
                submit_button = d(className="android.widget.Button")

        if submit_button and submit_button.exists:
            submit_button.click()
            time.sleep(1)
            return jsonify(
                {
                    "status": "success",
                    "message": "Successfully clicked submit button",
                }
            )
        else:
            click_x = text_field_right + 30  # 30px to the right
            click_y = text_field_center_y
            d.click(click_x, click_y)
            time.sleep(1)
            d.press.back()
            d.press.back()
            return jsonify(
                {
                    "status": "success",
                    "message": "Successfully clicked estimated submit button position",
                }
            )

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/go_back", methods=["POST"])
def go_back():
    """Navigate back with dynamic number of back presses"""
    try:
        data = request.get_json() or {}
        back_count = data.get("count", 1)

        if not isinstance(back_count, int) or back_count < 1:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Invalid count parameter. Must be a positive integer.",
                    }
                ),
                400,
            )

        if back_count > 10:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Maximum 10 back presses allowed for safety.",
                    }
                ),
                400,
            )

        for i in range(back_count):
            d.press.back()
            time.sleep(0.5)

        return jsonify(
            {
                "status": "success",
                "message": f"Successfully pressed back button {back_count} time(s)",
                "back_count": back_count,
            }
        )

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok - v1"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
