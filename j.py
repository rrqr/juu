# coding=utf-8
#!/usr/bin/env python3

from sys import exit
from os import _exit
from multiprocessing import Process
from colorama import Fore, Style
from requests import Session, post
import uuid

# Helpers
def print_logo():
    print(Fore.GREEN + r"""
JUNAI """ + Style.RESET_ALL)

def print_success(message):
    print(Fore.GREEN + "[+] " + message + Style.RESET_ALL)

def print_error(message):
    print(Fore.RED + "[-] " + message + Style.RESET_ALL)

def print_status(message):
    print(Fore.YELLOW + "[*] " + message + Style.RESET_ALL)

def ask_question(message):
    return input(Fore.CYAN + "[?] " + message + ": " + Style.RESET_ALL)

def login_to_instagram(username, password):
    """تسجيل الدخول إلى Instagram."""
    session = Session()
    headers = {
        "User-Agent": "Instagram 123.0.0.21.114 Android (30/3.0; 320dpi; 720x1280; Xiaomi; Redmi Note 8; ginkgo; qcom; en_US)",
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive"
    }

    data = {
        "_uuid": str(uuid.uuid4()),
        "username": username,
        "password": password,
        "device_id": str(uuid.uuid4()),
        "login_attempt_count": "0"
    }

    try:
        response = session.post(
            "https://i.instagram.com/api/v1/accounts/login/",
            headers=headers,
            data=data
        )

        if "logged_in_user" in response.text:
            print_success("Login Successful!")
            sessionid = response.cookies.get("sessionid")
            csrftoken = response.cookies.get("csrftoken")
            return sessionid, csrftoken
        elif "challenge_required" in response.text:
            print_error("Challenge Required. Please complete it manually.")
        elif "two_factor_required" in response.text:
            print_error("Two-Factor Authentication Required.")
        else:
            print_error("Login Failed. Check your credentials.")
    except Exception as e:
        print_error(f"Error during login: {e}")

    return None, None

def report_profile_attack(username, sessionid, csrftoken):
    """الإبلاغ عن حساب معين."""
    try:
        # الحصول على user_id عبر طلب GET
        user_info_response = post(
            f"https://www.instagram.com/{username}/?__a=1",
            headers={
                "User-Agent": "Mozilla/5.0",
                "cookie": f"sessionid={sessionid}",
                "X-CSRFToken": csrftoken,
            }
        )

        if user_info_response.status_code == 200:
            user_id = user_info_response.json().get("graphql", {}).get("user", {}).get("id")
            if not user_id:
                print_error("Failed to fetch user ID. Invalid username.")
                return
        else:
            print_error(f"Failed to fetch user info. Status: {user_info_response.status_code}")
            return

        print_status(f"Reporting profile: {username} (ID: {user_id})")

        # إرسال طلب الإبلاغ
        response = post(
            f"https://i.instagram.com/api/v1/users/{user_id}/flag/",
            headers={
                "User-Agent": "Mozilla/5.0",
                "cookie": f"sessionid={sessionid}",
                "X-CSRFToken": csrftoken,
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            },
            data="reason_id=1&source_name="  # سبب البلاغ: Scam/Spam
        )

        print(response.text)  # طباعة الرد للتأكد
        if response.status_code == 200:
            print_success("Report Sent Successfully!")
        elif response.status_code == 404:
            print_error("Failed to send report. The endpoint might be incorrect or the target does not exist.")
        else:
            print_error(f"Failed to send report. Status: {response.status_code}")
    except Exception as e:
        print_error(f"Error during profile report: {e}")

def profile_attack(username, sessionid, csrftoken):
    """تنفيذ الهجوم على ملف شخصي."""
    p = Process(target=report_profile_attack, args=(username, sessionid, csrftoken,))
    p.start()

def main():
    print_logo()
    print_success("Modules loaded!")

    # تسجيل الدخول
    username = ask_question("Enter your Instagram username").strip()
    password = ask_question("Enter your Instagram password").strip()
    sessionid, csrftoken = login_to_instagram(username, password)

    if not sessionid or not csrftoken:
        print_error("Failed to log in. Exiting.")
        return

    print_status("1 - Report Profile")
    print_status("Note: Enter '1' to report a profile.")
    report_choice = ask_question("Please select the complaint method").strip()

    if report_choice == "1":
        target_username = ask_question("Enter the username of the person you want to report").strip()
        if target_username:
            profile_attack(target_username, sessionid, csrftoken)
        else:
            print_error("Invalid username. Exiting.")
    else:
        print_error("Invalid choice. Exiting.")

if __name__ == "__main__":
    try:
        main()
        print(Style.RESET_ALL)
    except KeyboardInterrupt:
        print("\n\n" + Fore.RED + "[*] Program is closing!")
        print(Style.RESET_ALL)
        _exit(0)
