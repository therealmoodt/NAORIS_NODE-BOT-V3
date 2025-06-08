import asyncio
import json
import os
import pytz
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from colorama import init, Fore, Style
from curl_cffi import requests
from fake_useragent import FakeUserAgent

# Initialize colorama
init(autoreset=True)
wib = pytz.timezone('Asia/Jakarta')

# Definisikan warna utama
C_SUCCESS = Fore.LIGHTGREEN_EX
C_INFO = Fore.LIGHTYELLOW_EX
C_WARNING = Fore.LIGHTYELLOW_EX
C_ERROR = Fore.LIGHTRED_EX 
C_DEBUG = Fore.LIGHTYELLOW_EX
C_INPUT = Fore.LIGHTYELLOW_EX
C_BANNER = Fore.LIGHTGREEN_EX
C_TEXT = Fore.LIGHTYELLOW_EX
C_SEPARATOR = Fore.LIGHTYELLOW_EX


class NaorisProtocolAutomation:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "chrome-extension://cpikalnagknmlfhnilhfelifgbollmmp",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "none",
            "User-Agent": FakeUserAgent().random
        }
        self.base_api_url = "https://naorisprotocol.network"
        self.ping_api_url = "https://beat.naorisprotocol.network"

        self.proxies: List[str] = []
        self.proxy_index: int = 0
        self.account_proxies: Dict[str, Optional[str]] = {}
        self.access_tokens: Dict[str, str] = {}
        self.refresh_tokens: Dict[str, str] = {}
        self.wallet_balances: Dict[str, float] = {}

        self.accounts_file = "accounts.json"
        self.proxy_file = "proxies.txt"

    def display_banner(self):
        banner_lines = [
            "+------------------------------------------------------------+",
            "|                                                            |",
            "|            NAORIS PROTOCOL AUTOMATION BOT v2.0             |",
            "|                      Upgrade by moodt                      |",
            "|                                                            |",
            "+------------------------------------------------------------+"
        ]
        for line in banner_lines:
            print(C_BANNER + Style.BRIGHT + line + Style.RESET_ALL)
        print()

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message: str, level: str = "INFO", account_context: Optional[str] = None):
        timestamp = datetime.now(wib).strftime('%Y-%m-%d %H:%M:%S %Z')
        
        level_color_map = {
            "SUCCESS": C_SUCCESS, "INFO": C_INFO, "WARNING": C_WARNING,
            "ERROR": C_ERROR, "DEBUG": C_DEBUG, "INPUT": C_INPUT
        }
        log_color = level_color_map.get(level.upper(), C_INFO)
        
        level_str = level.upper().ljust(5)

        print(f"{C_TEXT}[{timestamp}]{Style.RESET_ALL} {log_color}[{level_str}]{Style.RESET_ALL} {log_color}{message}{Style.RESET_ALL}", flush=True)

    def log_account_specific(self, masked_address: str, message: str, level: str = "INFO", proxy_info: Optional[str] = None, status_msg: Optional[str] = None):
        timestamp = datetime.now(wib).strftime('%Y-%m-%d %H:%M:%S %Z')
        level_color_map = {
            "SUCCESS": C_SUCCESS, "INFO": C_INFO, "WARNING": C_WARNING,
            "ERROR": C_ERROR, "DEBUG": C_DEBUG
        }
        log_color = level_color_map.get(level.upper(), C_INFO)
        level_str = level.upper().ljust(5)

        base_message = f"{message} for [ACCOUNT] {masked_address}" if message else f"[ACCOUNT] {masked_address}"
        if proxy_info and status_msg:
            full_message = f"{base_message} | Proxy: {proxy_info} | Status: {status_msg}"
        elif status_msg:
            full_message = f"{base_message} | Status: {status_msg}"
        else:
            full_message = base_message

        print(f"{C_TEXT}[{timestamp}]{Style.RESET_ALL} {log_color}[{level_str}]{Style.RESET_ALL} {log_color}{full_message}{Style.RESET_ALL}", flush=True)


    def generate_device_hash(self) -> str:
        return str(int(uuid.uuid4().hex.replace("-", "")[:10], 16))

    def load_accounts_from_file(self) -> List[Dict[str, Any]]:
        try:
            if not os.path.exists(self.accounts_file):
                self.log(f"Accounts file '{self.accounts_file}' not found.", level="ERROR")
                return []
            with open(self.accounts_file, 'r') as file:
                accounts_data = json.load(file)
            if not isinstance(accounts_data, list):
                self.log(f"Data format in '{self.accounts_file}' is invalid. Expected a list.", level="ERROR")
                return []
            
            valid_accounts = []
            for acc_idx, acc in enumerate(accounts_data):
                if isinstance(acc, dict) and "Address" in acc and "deviceHash" in acc:
                    try:
                        acc["deviceHash"] = int(str(acc["deviceHash"]))
                        valid_accounts.append(acc)
                        if "token" in acc:
                            print(f"Token for {self._mask_address(acc['Address'])}: {acc['token']}")
                    except ValueError:
                        self.log(f"Account #{acc_idx+1} has an invalid deviceHash (must be integer): {C_WARNING}{acc.get('deviceHash')}{C_ERROR}", level="ERROR")
                else:
                    self.log(f"Account #{acc_idx+1} in '{self.accounts_file}' does not have the correct format (requires 'Address' and 'deviceHash').", level="WARNING")
            
            if valid_accounts:
                self.log(f"Loaded {len(valid_accounts)} valid accounts from '{self.accounts_file}'.", level="INFO")
            return valid_accounts
        except json.JSONDecodeError:
            self.log(f"Failed to decode JSON from '{self.accounts_file}'. Ensure the format is correct.", level="ERROR")
            return []
        except Exception as e:
            self.log(f"Error while loading accounts: {e}", level="ERROR")
            return []

    async def load_proxies_from_local_file(self):
        try:
            if not os.path.exists(self.proxy_file):
                self.log(f"Proxy file '{self.proxy_file}' not found.", level="ERROR")
                self.proxies = []
                return
            with open(self.proxy_file, 'r') as f:
                self.proxies = [line.strip() for line in f if line.strip()]

            if not self.proxies:
                self.log(f"No proxies loaded from '{self.proxy_file}'.", level="WARNING")
            else:
                 self.log(f"Total proxies loaded from '{self.proxy_file}': {len(self.proxies)}", level="SUCCESS")
        except Exception as e:
            self.log(f"Failed to load proxies from '{self.proxy_file}': {e}", level="ERROR")
            self.proxies = []

    def _get_proxy_url(self, proxy_str: str) -> Optional[str]:
        if not proxy_str:
            return None
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxy_str.startswith(scheme) for scheme in schemes):
            return proxy_str
        return f"http://{proxy_str}"

    def get_next_proxy_for_account(self, account_address: str) -> Optional[str]:
        if not self.proxies:
            return None
        current_proxy_str = self.proxies[self.proxy_index]
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        assigned_proxy = self._get_proxy_url(current_proxy_str)
        self.account_proxies[account_address] = assigned_proxy
        return assigned_proxy

    def _mask_address(self, address: str) -> str:
        if len(address) > 12:
            return f"{address[:6]}...{address[-4:]}"
        return address

    def ask_use_proxy(self) -> bool:
        timestamp = datetime.now(wib).strftime('%Y-%m-%d %H:%M:%S %Z')
        while True:
            print(f"{C_TEXT}[{timestamp}]{Style.RESET_ALL} {C_INPUT}[INPUT]{Style.RESET_ALL} {C_INPUT}Do you want to use proxies from '{self.proxy_file}'? (y/n): {Style.RESET_ALL}", end="")
            choice = input().strip().lower()
            if choice == 'y':
                self.log("Using proxy.", level="INFO")
                return True
            elif choice == 'n':
                self.log("Not using proxy.", level="INFO")
                return False
            else:
                self.log("Invalid input. Please enter 'y' for Yes or 'n' for No.", level="WARNING")

    async def _request(self, method: str, url: str, headers: Optional[Dict] = None, data: Optional[Dict] = None, 
                       json_payload: Optional[Dict] = None, proxy: Optional[str] = None, impersonate: str = "chrome110", timeout: int = 60) -> Optional[Any]:
        effective_headers = {**self.headers, **(headers or {})}
        if data:
             effective_headers["Content-Length"] = str(len(data))
             if "Content-Type" not in effective_headers:
                 effective_headers["Content-Type"] = "application/json"
        elif json_payload is not None:
            if "Content-Type" not in effective_headers:
                 effective_headers["Content-Type"] = "application/json"
        
        try:
            if method.upper() == "POST":
                response = await asyncio.to_thread(
                    requests.post, url, headers=effective_headers, data=data, json=json_payload, 
                    proxies={"http": proxy, "https": proxy} if proxy else None, 
                    timeout=timeout, impersonate=impersonate
                )
            elif method.upper() == "GET":
                response = await asyncio.to_thread(
                    requests.get, url, headers=effective_headers, 
                    proxies={"http": proxy, "https": proxy} if proxy else None, 
                    timeout=timeout, impersonate=impersonate
                )
            else:
                return {"error": True, "status_code": "N/A", "message": f"Unsupported HTTP method: {method}"}
            response.raise_for_status()
            try:
                return response.json()
            except json.JSONDecodeError:
                return response.text
        except requests.RequestsError as e:
            status_code = e.response.status_code if e.response is not None else "N/A"
            response_text = e.response.text if e.response is not None else None
            error_message = str(e)
            return {"error": True, "status_code": status_code, "message": error_message, "response_text": response_text}
        except Exception as e:
            return {"error": True, "status_code": "N/A", "message": str(e)}

    async def generate_token(self, masked_address: str, original_address: str, proxy: Optional[str], retries: int = 3) -> Optional[Dict]:
        url = f"{self.base_api_url}/sec-api/auth/gt-event"
        payload_dict = {"wallet_address": original_address}
        payload_str = json.dumps(payload_dict)
        
        for attempt in range(retries):
            response = await self._request("POST", url, data=payload_str, proxy=proxy)
            if isinstance(response, dict) and not response.get("error"):
                return response
            elif isinstance(response, dict) and response.get("status_code") == 404:
                 self.log_account_specific(masked_address, "", level="ERROR", status_msg=f"Generate Token Failed (404): Ensure the account is registered and tasks are completed.")
                 return None
            
            error_msg = response.get("message", "Unknown error") if isinstance(response, dict) else "Non-dict/No response"
            # Warning untuk retry, Error untuk final
            log_level_retry = "WARNING" if attempt < retries - 1 else "ERROR"
            self.log_account_specific(masked_address, "", level=log_level_retry, status_msg=f"Generate Token Failed (attempt {attempt+1}/{retries}): {error_msg}{'. Retrying...' if attempt < retries -1 else '. Final failure.'}")
            if attempt < retries - 1:
                await asyncio.sleep(5)
            else: # Failed after all retries
                return None
        return None # Should not be reached if the loop executes

    async def refresh_token_api(self, masked_address: str, original_address: str, current_refresh_token: str, proxy: Optional[str], use_proxy_flag: bool, retries: int = 3) -> Optional[Dict]:
        url = f"{self.base_api_url}/sec-api/auth/refresh"
        payload_dict = {"refreshToken": current_refresh_token}
        payload_str = json.dumps(payload_dict)

        for attempt in range(retries):
            response = await self._request("POST", url, data=payload_str, proxy=proxy)
            if isinstance(response, dict) and not response.get("error"):
                return response
            elif isinstance(response, dict) and response.get("status_code") == 401:
                self.log_account_specific(masked_address, "", level="WARNING", status_msg="Refresh Token Failed (401). Trying to generate a new token...")
                new_tokens = await self.process_generate_new_token(masked_address, original_address, use_proxy_flag, proxy_to_use=proxy)
                if new_tokens:
                    return new_tokens  # This is the successful dict from process_generate_new_token
                else:  # Failed to generate a new token
                    self.log_account_specific(masked_address, "", level="ERROR", status_msg="Failed to generate new token after refresh failed (401).")
                    return None  # Error final untuk refresh ini
            
            error_msg = response.get("message", "Unknown error") if isinstance(response, dict) else "Non-dict/No response"
            log_level_retry = "WARNING" if attempt < retries - 1 else "ERROR"
            self.log_account_specific(masked_address, "", level=log_level_retry, status_msg=f"Refresh Token Failed (attempt {attempt+1}/{retries}): {error_msg}{'. Retrying...' if attempt < retries -1 else '. Final failure.'}")
            if attempt < retries - 1:
                await asyncio.sleep(5)
            else:
                return None
        return None

    async def get_wallet_details(self, masked_address: str, original_address: str, access_token: str, proxy: Optional[str], retries: int = 3) -> Optional[Dict]:
        url = f"{self.base_api_url}/sec-api/api/wallet-details"
        headers = {"Authorization": f"Bearer {access_token}"}
        for attempt in range(retries):
            response = await self._request("GET", url, headers=headers, proxy=proxy)
            if isinstance(response, dict) and not response.get("error"):
                return response
            error_msg = response.get("message", "Unknown error") if isinstance(response, dict) else "Non-dict/No response"
            log_level_retry = "WARNING" if attempt < retries - 1 else "ERROR"
            self.log_account_specific(masked_address, "", level=log_level_retry, status_msg=f"Get Wallet Details Failed (attempt {attempt+1}/{retries}): {error_msg}{'. Retrying...' if attempt < retries -1 else '. Final failure.'}")
            if attempt < retries - 1:
                await asyncio.sleep(5)
            else:
                 return None
        return None

    async def add_to_whitelist(self, masked_address: str, original_address: str, access_token: str, proxy: Optional[str], retries: int = 3) -> bool:
        url = f"{self.base_api_url}/sec-api/api/addWhitelist"
        payload_dict = {"walletAddress": original_address, "url": "naorisprotocol.network"}
        payload_str = json.dumps(payload_dict)
        headers = {"Authorization": f"Bearer {access_token}"}
        proxy_info_str = proxy if proxy else "Not Used"

        for attempt in range(retries):
            response = await self._request("POST", url, headers=headers, data=payload_str, proxy=proxy)
            if isinstance(response, dict) and not response.get("error"):
                if response.get("message") == "url saved successfully":
                    return True # Sukses
            elif isinstance(response, dict) and response.get("status_code") == 409:
                self.log_account_specific(masked_address, "", level="INFO", proxy_info=proxy_info_str, status_msg="URL already in whitelist.")
                return True # Dianggap sukses jika sudah ada

            error_msg = response.get("message", "Unknown error") if isinstance(response, dict) else "Non-dict/No response"
            log_level_retry = "WARNING" if attempt < retries - 1 else "ERROR"
            self.log_account_specific(masked_address, "", level=log_level_retry, status_msg=f"Add Whitelist Failed (attempt {attempt+1}/{retries}): {error_msg}{'. Retrying...' if attempt < retries -1 else '. Final failure.'}")
            if attempt < retries - 1:
                await asyncio.sleep(5)
            else: # Failed after all retries
                 return False
        return False # Default if the loop completes without success
        
    async def toggle_device_activation(self, masked_address: str, original_address: str, device_hash: int, access_token: str, state: str, proxy: Optional[str], retries: int = 3) -> Optional[str]:
        url = f"{self.base_api_url}/sec-api/api/switch"
        payload_dict = {"walletAddress": original_address, "state": state.upper(), "deviceHash": device_hash}
        payload_str = json.dumps(payload_dict)
        headers = {"Authorization": f"Bearer {access_token}"}

        for attempt in range(retries):
            response = await self._request("POST", url, headers=headers, data=payload_str, proxy=proxy)
            
            if isinstance(response, str): # Success when response is a string
                return response.strip()
            # If not a string, something went wrong or response was unexpected
            elif isinstance(response, dict) and response.get("error"):
                error_msg = response.get("message", "Unknown error")
            elif isinstance(response,dict): # Dict tapi bukan error dari _request (misal, API mengembalikan JSON saat kita harapkan string)
                error_msg = f"Unexpected dict response: {response}"
            else: # None atau tipe lain
                error_msg = "No response or unknown response type"

            log_level_retry = "WARNING" if attempt < retries - 1 else "ERROR"
            self.log_account_specific(masked_address, "", level=log_level_retry, status_msg=f"Toggle Activation ({state}) Failed (attempt {attempt+1}/{retries}): {error_msg}{'. Retrying...' if attempt < retries -1 else '. Final failure.'}")
            if attempt < retries - 1:
                await asyncio.sleep(5)
            else: # Failed after all retries
                return None
        return None

    async def initiate_message_production(self, masked_address: str, original_address: str, device_hash: int, access_token: str, proxy: Optional[str], retries: int = 3) -> bool:
        url = f"{self.ping_api_url}/sec-api/api/htb-event"
        payload_dict = {"inputData": {"walletAddress": original_address, "deviceHash": device_hash}}
        payload_str = json.dumps(payload_dict)
        headers = {"Authorization": f"Bearer {access_token}"}

        for attempt in range(retries):
            response = await self._request("POST", url, headers=headers, data=payload_str, proxy=proxy)
            if isinstance(response, dict) and not response.get("error") and response.get("message") == "Message production initiated":
                return True
            
            error_msg = response.get("message", "Unknown error") if isinstance(response, dict) else "Non-dict/No response"
            log_level_retry = "WARNING" if attempt < retries - 1 else "ERROR"
            self.log_account_specific(masked_address, "", level=log_level_retry, status_msg=f"Initiate Message Prod. Failed (attempt {attempt+1}/{retries}): {error_msg}{'. Retrying...' if attempt < retries -1 else '. Final failure.'}")
            if attempt < retries - 1:
                await asyncio.sleep(5)
            else:
                return False
        return False

    async def perform_ping(self, masked_address: str, original_address: str, access_token: str, proxy: Optional[str], retries: int = 3) -> bool:
        url = f"{self.ping_api_url}/api/ping"
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

        for attempt in range(retries):
            response = await self._request("POST", url, headers=headers, json_payload={}, proxy=proxy)
            
            if isinstance(response, str) and response.strip() == "Ping Success!!": # Success if this exact string
                return True
            # Handle case where status 410 is also a success (as in sc2)
            elif isinstance(response, dict) and response.get("status_code") == 410 and \
                 isinstance(response.get("response_text"), str) and \
                 response.get("response_text","").strip() == "Ping Success!!":
                return True
            # If not the success string or 410 case, treat as error or unknown response
            elif isinstance(response, dict) and response.get("error"):
                error_msg = response.get("message", "Unknown error")
                status_code = response.get("status_code")
            elif isinstance(response,dict): # Dict but not an error from _request
                 error_msg = f"Unexpected dict response: {response}"
                 status_code = "N/A"
            else: # None or other types
                error_msg = "No response or unknown response type"
                status_code = "N/A"


            status_code_info = f"(status: {status_code})" if status_code != "N/A" else ""
            log_level_retry = "WARNING" if attempt < retries - 1 else "ERROR"
            self.log_account_specific(masked_address, "", level=log_level_retry, status_msg=f"Perform Ping Failed (attempt {attempt+1}/{retries}){status_code_info}: {error_msg}{'. Retrying...' if attempt < retries -1 else '. Final failure.'}")
            if attempt < retries - 1:
                await asyncio.sleep(5)
            else: # Failed after all retries
                return False
        return False

    async def process_generate_new_token(self, masked_address: str, original_address: str, use_proxy_flag: bool, proxy_to_use: Optional[str] = None) -> Optional[Dict[str,str]]:
        if proxy_to_use is None and use_proxy_flag:
            proxy = self.get_next_proxy_for_account(original_address) if use_proxy_flag else None
        else:
            proxy = proxy_to_use if use_proxy_flag else None
        
        proxy_info_str = proxy if proxy else "Not Used"

        token_data = await self.generate_token(masked_address, original_address, proxy)
        if token_data and "token" in token_data and "refreshToken" in token_data:
            self.access_tokens[original_address] = token_data["token"]
            self.refresh_tokens[original_address] = token_data["refreshToken"]
            # Success message is printed by generate_token if it succeeds,
            # or we can log it here as well. Following the example, "Generate Token Succeeded" is used.
            self.log_account_specific(masked_address, "", level="SUCCESS", proxy_info=proxy_info_str, status_msg=f"Generate Token Succeeded. Token: {token_data['token']}")
            return {"token": token_data["token"], "refreshToken": token_data["refreshToken"]}
        else:
            # Pesan error sudah dicetak oleh generate_token
            if original_address in self.access_tokens: del self.access_tokens[original_address]
            if original_address in self.refresh_tokens: del self.refresh_tokens[original_address]
            return None

    async def periodic_refresh_token_task(self, masked_address: str, original_address: str, use_proxy_flag: bool, initial_delay_minutes: int = 25):
        await asyncio.sleep(initial_delay_minutes * 60)
        while True:
            if original_address not in self.refresh_tokens:
                self.log_account_specific(masked_address, "No refresh token found, trying to generate a new one.", level="WARNING")
                await self.process_generate_new_token(masked_address, original_address, use_proxy_flag)
                if original_address not in self.refresh_tokens: # Jika masih gagal setelah coba generate
                    self.log_account_specific(masked_address, "Failed to obtain refresh token, skipping periodic refresh for this cycle.", level="ERROR")
                    await asyncio.sleep(5 * 60) # Wait before trying again from the start
                    continue # Continue the while True loop
            
            proxy = self.get_next_proxy_for_account(original_address) if use_proxy_flag else None
            proxy_info_str = proxy if proxy else "Not Used"
            
            self.log_account_specific(masked_address, "Attempting to refresh token...", level="DEBUG")
            refreshed_token_data = await self.refresh_token_api(masked_address, original_address, self.refresh_tokens[original_address], proxy, use_proxy_flag)
            
            if refreshed_token_data and "token" in refreshed_token_data and "refreshToken" in refreshed_token_data:
                self.access_tokens[original_address] = refreshed_token_data["token"]
                self.refresh_tokens[original_address] = refreshed_token_data["refreshToken"]
                self.log_account_specific(masked_address, "", level="SUCCESS", proxy_info=proxy_info_str, status_msg=f"Refresh Token Succeeded. New Token: {refreshed_token_data['token']}")
            else:
                # Pesan error/warning sudah dari refresh_token_api atau process_generate_new_token di dalamnya
                # Pastikan token dihapus jika refresh gagal total agar siklus berikutnya coba generate dari awal
                if original_address in self.access_tokens: del self.access_tokens[original_address]
                if original_address in self.refresh_tokens: del self.refresh_tokens[original_address]
                self.log_account_specific(masked_address, "Refresh token failed and old token removed. Will attempt to generate a new one next cycle.", level="WARNING")


            await asyncio.sleep(30 * 60) # Interval refresh

    async def periodic_wallet_details_task(self, masked_address: str, original_address: str, use_proxy_flag: bool, initial_delay_minutes: int = 1):
        await asyncio.sleep(initial_delay_minutes * 60)
        while True:
            if original_address not in self.access_tokens:
                self.log_account_specific(masked_address, "No access token, skipping get wallet details.", level="WARNING")
                await asyncio.sleep(5 * 60)
                continue

            proxy = self.get_next_proxy_for_account(original_address) if use_proxy_flag else None
            proxy_info_str = proxy if proxy else "Not Used"
            self.log_account_specific(masked_address, "Fetching wallet details...", level="DEBUG")
            details = await self.get_wallet_details(masked_address, original_address, self.access_tokens[original_address], proxy)
            
            if isinstance(details, dict) and not details.get("error") and "message" in details :
                total_earnings = details["message"].get("totalEarnings", "N/A")
                try:
                    self.wallet_balances[original_address] = float(total_earnings)
                except (TypeError, ValueError):
                    pass
                total_node = sum(self.wallet_balances.values())
                self.log(f"[TOTAL SOLDE NODE] {total_node} PTS", level="INFO")
                token_value = self.access_tokens.get(original_address, "N/A")
                self.log_account_specific(masked_address, "", level="INFO", proxy_info=proxy_info_str, status_msg=f"Token: {token_value}")
                self.log_account_specific(masked_address, "", level="INFO", proxy_info=proxy_info_str, status_msg=f"Total Earnings: {total_earnings} PTS")
            elif isinstance(details, dict) and details.get("error"):
                response_text = details.get("response_text", "")
                status_code = details.get("status_code")
                if status_code == 401 or (response_text and "Invalid token" in response_text):
                    self.log_account_specific(masked_address, "", level="WARNING", proxy_info=proxy_info_str, status_msg="Token invalid when fetching wallet details.")
                    if original_address in self.access_tokens: del self.access_tokens[original_address] # Hapus token agar di-generate ulang
                else: # Error lain
                    self.log_account_specific(masked_address, "", level="ERROR", proxy_info=proxy_info_str, status_msg=f"Failed to fetch wallet details: {details.get('message')}")
            else: # Respons tidak dikenal
                self.log_account_specific(masked_address, "", level="WARNING", proxy_info=proxy_info_str, status_msg="Failed to fetch wallet details (unknown response).")
            
            await asyncio.sleep(15 * 60) # Interval cek detail

    async def main_account_operations_task(self, original_address: str, device_hash: int, use_proxy_flag: bool):
        masked_address = self._mask_address(original_address)
        
        print(C_SEPARATOR + Style.BRIGHT + "-" * 60 + Style.RESET_ALL)
        # Account header now uses self.log so the timestamp and level format are consistent
        self.log(f"{C_INFO}[ACCOUNT]{Style.RESET_ALL} {C_INFO}{masked_address}{Style.RESET_ALL}", level="INFO")
        print(C_SEPARATOR + Style.BRIGHT + "-" * 60 + Style.RESET_ALL)

        if original_address not in self.access_tokens or original_address not in self.refresh_tokens:
            self.log_account_specific(masked_address, "Token not found. Starting token generation...", level="INFO")
            if not await self.process_generate_new_token(masked_address, original_address, use_proxy_flag):
                self.log_account_specific(masked_address, "Completely failed to create initial token. Cannot continue.", level="ERROR")
                return # Hentikan task ini untuk akun ini

        # Whitelist (setelah token dipastikan ada)
        if original_address in self.access_tokens: # Pastikan token ada sebelum whitelist
            proxy_for_whitelist = self.get_next_proxy_for_account(original_address) if use_proxy_flag else None
            proxy_info_str_whitelist = proxy_for_whitelist if proxy_for_whitelist else "Not Used"
            self.log_account_specific(masked_address, "Adding to whitelist...", level="DEBUG")
            
            if await self.add_to_whitelist(masked_address, original_address, self.access_tokens[original_address], proxy_for_whitelist):
                self.log_account_specific(masked_address, "", level="SUCCESS", proxy_info=proxy_info_str_whitelist, status_msg="Successfully added/already in whitelist.")
            # else: # Pesan error/warning sudah dari add_to_whitelist
        else:
            self.log_account_specific(masked_address, "Token not available, cannot add to whitelist.", level="WARNING")


        ping_interval_seconds = 60
        initiate_msg_interval_seconds = 10 * 60
        activation_check_interval_seconds = 5 * 60 

        last_ping_time = 0
        last_initiate_msg_time = 0
        last_activation_check_time = 0
        
        while True: # Loop utama operasi akun
            if original_address not in self.access_tokens: # Jika token hilang di tengah jalan
                self.log_account_specific(masked_address, "Access token missing, trying to regenerate...", level="WARNING")
                if not await self.process_generate_new_token(masked_address, original_address, use_proxy_flag):
                    self.log_account_specific(masked_address, "Failed to regenerate token. Skipping this cycle.", level="ERROR")
                    await asyncio.sleep(60) # Wait before trying again
                    continue # Return to the start of the while True loop
            
            current_time = asyncio.get_event_loop().time()
            # Dapatkan proxy untuk siklus operasi ini
            current_op_proxy = self.get_next_proxy_for_account(original_address) if use_proxy_flag else None
            current_op_proxy_info = current_op_proxy if current_op_proxy else "Not Used"
            
            perform_actions_after_activation = False # Flag indicating whether core actions (ping/initiate) may run

            # --- Activation Check and Process ---
            if current_time - last_activation_check_time > activation_check_interval_seconds:
                self.log_account_specific(masked_address, "Checking activation status...", level="DEBUG")
                # Always try deactivating first to ensure a clean state unless the API disallows it or errors
                deactivate_response = await self.toggle_device_activation(masked_address, original_address, device_hash, self.access_tokens[original_address], "OFF", current_op_proxy)
                
                if deactivate_response is not None and deactivate_response in ["Session ended and daily usage updated", "No action needed", "Session not found to end"]:
                    self.log_account_specific(masked_address, "", level="INFO", proxy_info=current_op_proxy_info, status_msg=f"Deactivation Status: {deactivate_response}. Attempting to activate ON...")
                    
                    activate_response = await self.toggle_device_activation(masked_address, original_address, device_hash, self.access_tokens[original_address], "ON", current_op_proxy)
                    if activate_response is not None and activate_response == "Session started":
                        self.log_account_specific(masked_address, "", level="SUCCESS", proxy_info=current_op_proxy_info, status_msg="Device Activation (ON) Succeeded.")
                        perform_actions_after_activation = True
                    elif activate_response is not None and activate_response == "Session already active for this device":
                         self.log_account_specific(masked_address, "", level="INFO", proxy_info=current_op_proxy_info, status_msg="Device Activation (ON): Already Active.")
                         perform_actions_after_activation = True # If already active, still perform actions
                    elif activate_response is not None: # Response received but not success
                        self.log_account_specific(masked_address, "", level="ERROR", proxy_info=current_op_proxy_info, status_msg=f"Device Activation (ON) Failed. Response: {activate_response}")
                    else: # activate_response is None (severe error)
                         self.log_account_specific(masked_address, "", level="ERROR", proxy_info=current_op_proxy_info, status_msg="Device Activation (ON) Failed (no response).")

                elif deactivate_response is not None: # Failed to deactivate but response received
                    self.log_account_specific(masked_address, "", level="ERROR", proxy_info=current_op_proxy_info, status_msg=f"Deactivation (OFF) Failed: {deactivate_response}. Activation ON not continued.")
                else: # Failed to deactivate and no response
                    self.log_account_specific(masked_address, "", level="ERROR", proxy_info=current_op_proxy_info, status_msg="Deactivation (OFF) Failed (no response). Activation ON not continued.")
                last_activation_check_time = current_time
            else: # Not time to check activation yet, assume previous state still valid
                 if original_address in self.access_tokens : # At minimum token exists
                    perform_actions_after_activation = True


            # --- Core Actions (Ping & Initiate Message) ---
            if perform_actions_after_activation:
                # Initiate Message Production
                if current_time - last_initiate_msg_time > initiate_msg_interval_seconds :
                    self.log_account_specific(masked_address, "Sending initiate message production...", level="DEBUG")
                    if await self.initiate_message_production(masked_address, original_address, device_hash, self.access_tokens[original_address], current_op_proxy):
                        self.log_account_specific(masked_address, "", level="SUCCESS", proxy_info=current_op_proxy_info, status_msg="Initiate Message Production Succeeded.")
                    # else: # Pesan error sudah dari fungsi initiate_message_production
                    last_initiate_msg_time = current_time
                
                # Perform Ping
                if current_time - last_ping_time > ping_interval_seconds:
                    self.log_account_specific(masked_address, "Performing ping...", level="DEBUG")
                    if await self.perform_ping(masked_address, original_address, self.access_tokens[original_address], current_op_proxy):
                        self.log_account_specific(masked_address, "", level="SUCCESS", proxy_info=current_op_proxy_info, status_msg="Ping Succeeded.")
                    # else: # Pesan error sudah dari fungsi perform_ping
                    last_ping_time = current_time

            await asyncio.sleep(30) # Main pause between cycles in the main loop

    async def run_bot(self):
        self.clear_terminal()
        self.display_banner()

        accounts = self.load_accounts_from_file()
        if not accounts:
            self.log("No accounts loaded. Bot stopping.", level="ERROR")
            return

        use_proxy_flag = self.ask_use_proxy()

        if use_proxy_flag:
            await self.load_proxies_from_local_file()
            if not self.proxies:
                self.log("No proxies available in 'proxies.txt'. Continuing without proxy.", level="WARNING")
                use_proxy_flag = False # Set ulang flag jika tidak ada proxy

        self.log(f"Starting process for {len(accounts)} accounts...", level="INFO")

        tasks = []
        for account_data in accounts:
            original_address = account_data["Address"].lower()
            try:
                device_hash = int(str(account_data["deviceHash"]))
            except ValueError:
                self.log(f"Account with address {C_WARNING}{self._mask_address(original_address)}{C_ERROR} has an invalid deviceHash: {C_WARNING}{account_data['deviceHash']}{C_ERROR}. Skipping this account.", level="ERROR")
                continue
            
            masked_address = self._mask_address(original_address)

            # Membuat tasks untuk setiap akun
            tasks.append(asyncio.create_task(self.main_account_operations_task(original_address, device_hash, use_proxy_flag)))
            tasks.append(asyncio.create_task(self.periodic_refresh_token_task(masked_address, original_address, use_proxy_flag)))
            tasks.append(asyncio.create_task(self.periodic_wallet_details_task(masked_address, original_address, use_proxy_flag)))
            
            await asyncio.sleep(1) # Short delay between starting tasks to avoid flooding the API

        if tasks:
            await asyncio.gather(*tasks)
        else:
            self.log("No valid tasks were created for accounts.", level="WARNING")

if __name__ == "__main__":
    bot = NaorisProtocolAutomation()
    try:
        asyncio.run(bot.run_bot())
    except KeyboardInterrupt:
        bot.log("Bot stopped by user (KeyboardInterrupt).", level="INFO")
    except Exception as e:
        bot.log(f"Unexpected error at top level: {e}", level="ERROR")
        import traceback
        traceback.print_exc()  # Print traceback to debug unexpected errors
    finally:
        bot.log("Bot Finished.", level="INFO")
