
# Naoris Protocol Automation Bot v2.0


Bot otomatisasi untuk berinteraksi dengan Naoris Protocol, dibuat oleh **@AirdropFamilyIDN**.
Skrip ini dirancang untuk mengotomatiskan berbagai tugas terkait akun Naoris Protocol, seperti menghasilkan token, menambahkan ke whitelist, aktivasi perangkat, melakukan ping, dan memeriksa detail wallet.

## ✨ Fitur Utama

* 🤖 **Otomatisasi Penuh**: Dari pembuatan token hingga ping berkala.
* 👥 **Manajemen Multi-Akun**: Mendukung banyak akun dari file `accounts.json`.
* 🔄 **Dukungan Proxy**: Opsi untuk menggunakan proxy dari `proxies.txt` dengan rotasi sederhana.
* 🔑 **Manajemen Token**: Pembuatan token awal dan refresh token otomatis.
* 📝 **Whitelist Otomatis**: Menambahkan URL jaringan ke whitelist akun.
* 💡 **Aktivasi Perangkat**: Mengelola status aktivasi perangkat (ON/OFF).
* 💓 **Ping & Produksi Pesan**: Mengirim ping dan inisiasi produksi pesan secara berkala.
* 📊 **Detail Wallet**: Memeriksa total pendapatan (poin) secara periodik.
* 🎨 **Logging Berwarna**: Output terminal yang mudah dibaca dengan status (SUCCESS, INFO, WARNING, ERROR).
* 🛡️ **Penanganan Error & Retry**: Upaya coba lagi (retry) untuk operasi API yang gagal.
* ⚙️ **Konfigurasi Mudah**: Pengaturan akun dan proxy melalui file eksternal.

## 📋 Kebutuhan Sistem

* Python 3.10+
* Pip (Python package installer)

## 🛠️ Instalasi Dependensi

Pastikan Anda sudah menginstal Python dan Pip. Kemudian, instal dependensi yang dibutuhkan dengan menjalankan perintah berikut di terminal:

```bash
pip install pytz colorama curl_cffi fake_useragent
```

## ⚙️ Konfigurasi

Sebelum menjalankan bot, Anda perlu menyiapkan dua file konfigurasi di direktori yang sama dengan skrip:

1.  **`accounts.json`**:
    File ini berisi daftar akun Naoris Protocol Anda. Formatnya adalah JSON array dari objek, di mana setiap objek memiliki `Address` (alamat wallet) dan `deviceHash`.

    Contoh `accounts.json`:
    ```json
    [
      {
        "Address": "0xWalletAddressKamu1",
        "deviceHash": 1234567890123
      },
      {
        "Address": "0xWalletAddressKamu2",
        "deviceHash": 9876543210987
      }
    ]
    ```
    * Ganti `0xWalletAddressKamu...` dengan alamat wallet Ethereum Anda.
    * `deviceHash` adalah ID unik perangkat; skrip ini mengasumsikan `deviceHash` adalah integer yang valid dan unik per akun.

2.  **`proxies.txt`** (Opsional):
    Jika Anda ingin menggunakan proxy, buat file ini dan isi dengan daftar proxy, satu proxy per baris.
    Format: `ip:port` atau `user:pass@ip:port` atau `http://user:pass@ip:port`.
    Jika file ini tidak ada atau kosong, dan Anda memilih untuk tidak menggunakan proxy saat bot dijalankan, bot akan berjalan tanpa proxy.

    Contoh `proxies.txt`:
    ```
    192.168.1.1:8080
    user1:pass1@proxy.example.com:3128
    [http://anotheruser:anotherpass@123.123.123.123:8888](http://anotheruser:anotherpass@123.123.123.123:8888)
    ```

## 🚀 Cara Menjalankan Bot

1.  Pastikan semua dependensi sudah terinstal.
2.  Siapkan file `accounts.json` (dan `proxies.txt` jika diperlukan).
3.  Jalankan skrip dari terminal:

    ```bash
    python main.py
    ```
    (Ganti `nama_script_anda.py` dengan nama file skrip Python Anda, misalnya `naoris_bot.py`).

4.  Bot akan menanyakan apakah Anda ingin menggunakan proxy. Jawab `y` (Ya) atau `n` (Tidak).
5.  Bot akan mulai memproses setiap akun secara asinkron.

## 📜 Cara Kerja Umum per Akun

1.  **Inisialisasi**: Memuat data akun dan proxy (jika digunakan).
2.  **Pembuatan/Refresh Token**:
    * Jika token belum ada, bot akan mencoba membuat token baru.
    * Jika token sudah ada, bot akan menjalankan tugas refresh token secara berkala (default setiap 30 menit setelah 25 menit awal).
3.  **Whitelist**: Menambahkan URL jaringan (`naorisprotocol.network`) ke whitelist.
4.  **Aktivasi Perangkat**:
    * Secara periodik, bot akan mencoba menonaktifkan sesi yang ada (jika ada) untuk memastikan state bersih.
    * Kemudian mengaktifkan perangkat (state "ON").
5.  **Operasi Berkala (jika perangkat aktif dan token valid)**:
    * **Initiate Message Production**: Mengirim permintaan inisiasi produksi pesan ke `beat.naorisprotocol.network` (default setiap 10 menit).
    * **Perform Ping**: Melakukan ping ke server `beat.naorisprotocol.network` (default setiap 60 detik).
6.  **Detail Wallet**: Memeriksa detail wallet (total pendapatan) secara berkala (default setiap 15 menit setelah 1 menit awal).
7.  Semua operasi utama (aktivasi, ping, initiate message) dilakukan dalam loop utama dengan jeda antar siklus pengecekan. Task untuk refresh token dan cek detail wallet berjalan secara paralel dengan intervalnya masing-masing.

## ⚠️ Disclaimer

* Bot ini disediakan sebagaimana adanya. **Gunakan dengan risiko Anda sendiri (Do With Your Own Risk - DWYOR)**.
* Penggunaan bot untuk mengotomatisasi interaksi dengan platform apa pun mungkin melanggar Ketentuan Layanan (ToS) platform tersebut. Pastikan Anda memahami dan menerima risikonya.
* Penulis tidak bertanggung jawab atas kerugian atau masalah apa pun yang mungkin timbul dari penggunaan skrip ini, termasuk namun tidak terbatas pada pemblokiran akun atau kehilangan aset.
* Perubahan pada API Naoris Protocol dapat menyebabkan bot ini tidak berfungsi. Selalu uji coba pada akun tes terlebih dahulu jika memungkinkan.


---
```
