import requests
import os
from dotenv import load_dotenv

load_dotenv()

def find_chat_id():
    token = os.getenv("TELEGRAM_TOKEN")
    if not token or "your_bot_token" in token:
        print("X .env file has no valid TELEGRAM_TOKEN.")
        return

    print(f"Finding Chat ID for Bot (Token: {token[:10]}...)...")
    
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    try:
        response = requests.get(url)
        data = response.json()
        
        if not data.get("ok"):
            print(f"X API Error: {data.get('description')}")
            return

        results = data.get("result", [])
        if not results:
            print("! No messages found for this bot.")
            print("? Please send any message to your bot in Telegram first!")
            return

        # 가장 최근 메시지에서 chat id 추출
        last_update = results[-1]
        chat_id = None
        user_name = "Unknown"

        if "message" in last_update:
            chat_id = last_update["message"]["chat"]["id"]
            user_name = last_update["message"]["from"].get("first_name", "User")
        elif "my_chat_member" in last_update:
            chat_id = last_update["my_chat_member"]["chat"]["id"]
            
        if chat_id:
            print(f"Chat ID Found!")
            print(f"User: {user_name}")
            print(f"Chat ID: {chat_id}")
            return chat_id
        else:
            print("X Could not find Chat ID in message structure.")
            
    except Exception as e:
        print(f"X Error occurred: {e}")

if __name__ == "__main__":
    chat_id = find_chat_id()
    if chat_id:
        # Update .env file
        env_path = ".env"
        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        with open(env_path, "w", encoding="utf-8") as f:
            for line in lines:
                if line.startswith("TELEGRAM_CHAT_ID="):
                    f.write(f"TELEGRAM_CHAT_ID={chat_id}\n")
                else:
                    f.write(line)
        print(f"TELEGRAM_CHAT_ID in .env updated to {chat_id}!")
