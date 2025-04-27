import os
import requests
import time

#配置
CONTRACT_ADDRESS = "0x8f0528ce5ef7b51152a59745befdd91d97091d2f"
BSCSCAN_API_KEY = os.getenv("BSCSCAN_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

CHECK_INTERVAL = 1  # 检查间隔（秒）
HEARTBEAT_INTERVAL = 600  # 心跳推送间隔（秒）
BSC_SCAN_RATE_LIMIT = 5  # BscScan接口限制，5次/秒

# === 功能函数 ===
def get_total_supply():
    url = f"https://api.bscscan.com/api?module=stats&action=tokensupply&contractaddress={CONTRACT_ADDRESS}&apikey={BSCSCAN_API_KEY}"
    try:
        response = requests.get(url)
        data = response.json()
        if data["status"] == "1":
            supply = int(data["result"])
            return supply
        else:
            print("[错误] 获取Supply失败:", data)
            return None
    except Exception as e:
        print("[异常] 请求出错:", e)
        return None

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("[异常] 发送Telegram消息失败:", e)

# === 主程序 ===
def main():
    print("启动增发监控Bot...")
    old_supply = get_total_supply()
    if old_supply is None:
        print("初次获取Supply失败，退出。")
        return
    print(f"初始Supply: {old_supply}")
    
    last_heartbeat_time = time.time()

    while True:
        time.sleep(1 / BSC_SCAN_RATE_LIMIT)  # 控制访问频率
        
        new_supply = get_total_supply()
        if new_supply is None:
            continue
        
        current_time = time.time()

        if new_supply > old_supply:
            diff = new_supply - old_supply
            message = f"\u26a1\ufe0f警告！检测到 {diff} 单位新增供应！\n合约: {CONTRACT_ADDRESS}"
            print(message)
            send_telegram_message(message)
            old_supply = new_supply
            last_heartbeat_time = current_time
        else:
            if current_time - last_heartbeat_time >= HEARTBEAT_INTERVAL:
                heartbeat_message = f"\u2705 监控正常，无新增供应。\n合约: {CONTRACT_ADDRESS}\n时间: {time.strftime('%Y-%m-%d %H:%M:%S')}"
                print(heartbeat_message)
                send_telegram_message(heartbeat_message)
                last_heartbeat_time = current_time

if __name__ == "__main__":
    main()
