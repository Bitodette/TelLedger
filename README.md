# 💰 Telegram Finance Bot (Ledger/Paisa)

A privacy-focused Telegram bot designed to streamline personal finance tracking. It records expenses and income directly into a local **Ledger** text file (`.ledger` / `.journal`), making it fully compatible with **[Paisa](https://paisa.fyi)**.

## ✨ Features

- **🔒 100% Private & Local:** Data is stored in a plain text file on your own machine. No third-party cloud storage.
- **🚀 Instant Input:** Record transactions via Telegram chat instantly. Supports offline/pending messages (syncs when the bot comes online).
- **🔄 Auto-Sync:** Automatically triggers Paisa to refresh its database (`paisa update`) upon recording a transaction.
- **💸 Dual Payment Mode:**
  - **Cash Mode:** deducts from `Assets:Wallet:Cash`.
  - **Digital Mode:** deducts from `Assets:Bank:Main` (QRIS/Transfer).
- **🛡️ Security:** Restricts access to a specific Telegram User ID.

## 🛠️ Prerequisites

- Python 3.10+
- A Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- **[Paisa](https://paisa.fyi)** installed and added to your system PATH.

## 📦 Installation

### 1. Install Paisa (Visualization Dashboard)

This bot requires `paisa` to be installed to trigger the auto-sync feature.

👉 **[Follow the Official Installation Guide Here](https://paisa.fyi/getting-started/installation/#__tabbed_1_1)**

_Make sure you can run `paisa --version` in your terminal before proceeding._

### 2. Setup the Bot

1.  **Clone the repository**

    ```bash
    git clone [https://github.com/YOUR_USERNAME/finance-bot.git](https://github.com/YOUR_USERNAME/finance-bot.git)
    cd finance-bot
    ```

2.  **Set up Virtual Environment** (Recommended)

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Linux/Mac
    # venv\Scripts\activate   # On Windows
    ```

3.  **Install Python Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Initialize Ledger File**
    Copy the sample ledger to create your real data file:
    ```bash
    cp sample.ledger finance.ledger
    ```

## ⚙️ Configuration

Open `finance_bot.py` and edit the **Configuration Section** at the top:

```python
# Telegram Bot Token (Get from @BotFather)
TOKEN = "YOUR_BOT_TOKEN_HERE"

# Your Telegram User ID (Get from @userinfobot)
# Important: This prevents others from using your bot.
ALLOWED_USER_ID = 123456789

# Path to your Ledger File
LEDGER_FILE = "finance.ledger"

# Path to Paisa Config (Optional, for auto-sync)
PAISA_CONFIG_FILE = "paisa.yaml"
```

## 🚀 Usage

Run the bot:

```bash
python finance_bot.py
```

## 🤖 Bot Commands

### 💵 Cash Expenses (Source: Assets:Wallet:Cash)

    /food [amount] [desc] - Meals, Drinks
    /transport [amount] [desc] - Fuel, Parking
    /shop [amount] [desc] - General Shopping
    /health [amount] [desc] - Medical expenses
    /other [amount] [desc] - Miscellaneous

### 💳 Digital/Bank Expenses (Source: Assets:Bank:Main)

    /qfood [amount] [desc] - Paid via QRIS/Transfer
    /qtransport [amount] [desc] - Ride-hailing apps
    /qshop [amount] [desc] - Online Shopping
    /qbill [amount] [desc] - Utilities, Data Plans
    /qsub [amount] [desc] - Subscriptions

### 💰 Income & Transfers

    /income [amount] [desc] - Salary (to Bank)
    /gift [amount] [desc] - Cash Gift (to Wallet)
    /withdraw [amount] - ATM Withdrawal (Bank -> Cash)

**Example**

    You: /qfood 25000 Burger King
    Bot: ✅ Recorded: EXPENSE (BANK) 📝 Burger King 💰 25000 📂 Expenses:Food

## 📄 License

This project is licensed under the MIT License.
