# 📦 site2zip – Website to ZIP Telegram Bot  
<p align="center">
  <b>Download any website as a ZIP archive directly from Telegram 🚀</b>  
</p>  

---

## ✨ Description  
`site2zip` is a Telegram bot that allows users to **download websites** and receive them as a **compressed ZIP file** right inside Telegram.  
No need for wget or external tools — everything runs on pure Python with `requests` and `beautifulsoup4`.  

---

## 🚀 Features  
- 🔗 Send a URL, get a **ZIP file** of the website  
- 📄 Supports HTML pages, CSS, JS, and images  
- 📦 Automatically zips downloaded content  
- 🛡️ File size and page limits for safe usage  
- 🧹 Auto-deletes files after **3 minutes** for privacy  
- ✅ Simple `/start`, `/help`, and `/status` commands

  
---

## ⚙️ Installation  

1. **Clone the repository**  
   ```bash
   git clone https://github.com/Ahmed-GoCode/site2zip.git
   
   cd site2zip

   
--- 

2. Install dependencies
```bash
pip install -r requirements.txt
``` 

---

3. Set up your Telegram Bot Token

Get your token from ```@BotFather```

Add it to your environment: 
```bash
export BOT_TOKEN="your_telegram_bot_token"
```

---

4. run the bot 
```bash
python main.py
```

---

📖 Usage

```/start``` → Show welcome message

```/help``` → Display help instructions

```/status``` → Check download progress

Send any valid URL → Bot downloads the website, zips it, and sends it back

---

⚡ Limits

Max 20 pages per download

Max 50MB total site size

Max 5MB per file

Auto-deletes downloaded files after 3 minutes

---

📂 Project Structure

```bash 
site2zip/
├── main.py              # Bot code
├── requirements.txt     # Python dependencies
├── README.md            # Project readme
└── LICENSE              # License file
```

--- 

🛠️ Built With

Python 3 🐍

python-telegram-bot 🤖

Requests 🌐

BeautifulSoup4 🍲

---

📜 License

This project is licensed under the MIT License – see the [LICENSE](https://github.com/Ahmed-GoCode/Site2Zip/blob/main/LICENSE)
 file for details.

 ---


 p align="center"> Made with ❤️ by Ahmad </p> ```
