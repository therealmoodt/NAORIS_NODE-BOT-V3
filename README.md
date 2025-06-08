
# Naoris Protocol Automation Bot v3.0


Automation bot for interacting with Naoris Protocol.
This script is designed to automate various account-related tasks such as generating tokens, adding to the whitelist, activating devices, sending pings and checking wallet details.

## ✨ Key Features

* 🤖 **Full Automation**: From token generation to periodic pings.
* 👥 **Multi-Account Management**: Supports multiple accounts from `accounts.json`.
* 🔄 **Proxy Support**: Optionally use proxies from `proxies.txt` with simple rotation.
* 🔑 **Token Management**: Initial token creation and automatic refresh.
* 📝 **Automatic Whitelisting**: Adds the network URL to the account whitelist.
* 💡 **Device Activation**: Manages device activation status (ON/OFF).
* 💓 **Ping & Message Production**: Sends pings and initiates message production periodically.
* 📊 **Wallet Details**: Checks total earnings (points) periodically and prints each account's token with an aggregated node total. [NEW]
* 🎨 **Colored Logging**: Easy‑to‑read terminal output with status (SUCCESS, INFO, WARNING, ERROR).
* 🛡️ **Error Handling & Retry**: Retries failed API operations.
* ⚙️ **Simple Configuration**: Configure accounts and proxies via external files.

## 📋 System Requirements

* Python 3.10+
* Pip (Python package installer)

## 🛠️ Installing Dependencies

Ensure you have Python and Pip installed. Then install the required dependencies by running the following command in your terminal:

```bash
pip install pytz colorama curl_cffi fake_useragent
```

## ⚙️ Configuration

Before running the bot you need to prepare two configuration files in the same directory as the script:

1.  **`accounts.json`**:
    This file contains a list of your Naoris Protocol accounts. The format is a JSON array of objects, each containing `Address` (wallet address) and `deviceHash`.

    Example `accounts.json`:
    ```json
    [
      {
        "Address": "0xWalletAddressKamu1",
        "deviceHash": "1234567890123"
      },
      {
        "Address": "0xWalletAddressKamu2",
        "deviceHash": "9876543210987"
      }
    ]
    ```
    * Replace `0xWalletAddressKamu...` with your Ethereum wallet address.
    * `deviceHash` is a unique device ID; the script assumes `deviceHash` is a valid integer unique to each account.

2.  **`proxies.txt`** (Optional):
    If you want to use proxies, create this file and fill it with a list of proxies, one per line.
    Format: `ip:port` or `user:pass@ip:port` or `http://user:pass@ip:port`.
    If this file does not exist or is empty and you choose not to use a proxy when the bot runs, it will run without proxies.

    Example `proxies.txt`:
    ```
    192.168.1.1:8080
    user1:pass1@proxy.example.com:3128
    [http://anotheruser:anotherpass@123.123.123.123:8888](http://anotheruser:anotherpass@123.123.123.123:8888)
    ```

## 🚀 Running the Bot

1.  Ensure all dependencies are installed.
2.  Prepare the `accounts.json` file (and `proxies.txt` if needed).
3.  Run the script from your terminal:

    ```bash
    python main.py
    ```

4.  The bot will ask whether you want to use proxies. Answer `y` (Yes) or `n` (No).
5.  The bot will then begin processing each account asynchronously.

## 📜 General Workflow per Account

1.  **Initialization**: Loads account data and proxies (if used).
2.  **Token Generation/Refresh**:
    * If no token exists, the bot tries to generate a new one.
    * If a token is already present, it refreshes the token periodically (default every 30 minutes after an initial 25-minute delay).
3.  **Whitelist**: Adds the network URL (`naorisprotocol.network`) to the whitelist.
4.  **Device Activation**:
    * Periodically attempts to disable any existing session to ensure a clean state.
    * Then activates the device (state "ON").
5.  **Periodic Operations (if the device is active and token valid)**:
    * **Initiate Message Production**: Sends a request to `beat.naorisprotocol.network` (default every 10 minutes).
    * **Perform Ping**: Pings the `beat.naorisprotocol.network` server (default every 60 seconds).
6.  **Wallet Details**: Checks wallet details (total earnings) periodically (default every 15 minutes after an initial 1-minute delay).
7.  All main operations (activation, ping, initiate message) run in a main loop with delays between cycles. Tasks for refreshing the token and checking wallet details run in parallel with their own intervals.

## 📈 Improvement Log

* 🔎 **Token Logging**: Displays each account's token when loaded and whenever wallet details are fetched. [NEW]
* 💰 **Total Wallet Balance**: After retrieving wallet details for all accounts, prints the combined balance across nodes. [NEW]

## ⚠️ Disclaimer

* This bot is provided as is. **Use at your own risk (Do With Your Own Risk - DWYOR).**
* Automating interactions with any platform may violate its Terms of Service. Make sure you understand and accept the risk.
* The author is not responsible for any loss or issues that may arise from using this script, including but not limited to account bans or asset loss.
* Changes to the Naoris Protocol API can cause this bot to stop working. Always test on a demo account first if possible.


---
