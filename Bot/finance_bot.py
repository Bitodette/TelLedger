import logging
import subprocess
import os
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# ==========================================
# CONFIGURATION
# ==========================================

# Telegram Bot Token (Replace with your own)
TOKEN = "YOUR_BOT_TOKEN_HERE"

# Telegram User ID (Replace with your own ID)
# This restricts access to the bot to a single user.
ALLOWED_USER_ID = 123456789

# Path to the Ledger file
# Ensure this path is absolute or relative to the script execution.
LEDGER_FILE = "finance.ledger"

# Path to Paisa configuration file (Optional, for auto-sync)
PAISA_CONFIG_FILE = "paisa.yaml"

# Default Account Names
ACC_CASH = "Assets:Wallet:Cash"
ACC_BANK = "Assets:Bank:Main"

# ==========================================
# LOGGING SETUP
# ==========================================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ==========================================
# CORE FUNCTIONS
# ==========================================

def write_to_ledger(description, amount, target_account, source_account):
    """
    Appends a transaction to the ledger file with proper formatting.
    Also triggers Paisa update command if applicable.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Format entry with 44-column alignment
    entry = f"{today} * {description}\n"
    entry += f"    {target_account:<39} IDR {amount}\n" 
    entry += f"    {source_account}\n"

    try:
        # Append to file
        with open(LEDGER_FILE, "a+") as f:
            f.seek(0, 2) # Move cursor to end of file
            size = f.tell()
            
            if size > 0:
                f.seek(size - 2) 
                last_chars = f.read(2)
                
                # Ensure one empty line between transactions
                if last_chars.endswith("\n\n"): 
                    pass 
                elif last_chars.endswith("\n"): 
                    f.write("\n") 
                else: 
                    f.write("\n\n")
            
            f.write(entry)

        # Trigger Paisa database update (Auto-sync)
        # This allows the dashboard to update immediately without manual refresh.
        try:
            if os.path.exists(PAISA_CONFIG_FILE):
                cmd = ["paisa", "update", "--config", PAISA_CONFIG_FILE]
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            logging.warning(f"Paisa sync failed (ignoring): {e}")
        
        return True
        
    except Exception as e:
        logging.error(f"File I/O Error: {e}")
        return False

async def handle_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE, category_account: str, type: str):
    """
    Main logic handler for processing transaction commands.
    Determines source and destination accounts based on transaction type.
    """
    # Security checks
    if not update.effective_user or not update.message: return
    if update.effective_user.id != ALLOWED_USER_ID: return

    # Validate input arguments
    if not context.args:
        await update.message.reply_text(
            "Missing amount.\nUsage: `/command [amount] [description]`", 
            parse_mode='Markdown'
        )
        return

    try:
        # Parse amount
        amount = context.args[0].replace(".", "").replace(",", "")
        if not amount.isdigit():
            await update.message.reply_text("Amount must be a valid number.")
            return

        # Parse description
        description = " ".join(context.args[1:])
        
        target_acc = ""
        source_acc = ""
        display_type = ""
        display_folder = ""

        # --- Logic Handling ---
        
        # 1. Cash Expense
        if type == "expense_cash":
            target_acc = category_account
            source_acc = ACC_CASH
            display_type = "EXPENSE (CASH)"
            display_folder = category_account
            if not description: description = "Expense Cash"

        # 2. Bank/Digital Expense
        elif type == "expense_bank":
            target_acc = category_account
            source_acc = ACC_BANK
            display_type = "EXPENSE (BANK)"
            display_folder = category_account
            if not description: description = "Expense Digital"

        # 3. Cash Income
        elif type == "income_cash":
            target_acc = ACC_CASH
            source_acc = category_account
            display_type = "INCOME (CASH)"
            display_folder = category_account
            if not description: description = "Income Cash"

        # 4. Bank Income
        elif type == "income_bank":
            target_acc = ACC_BANK
            source_acc = category_account
            display_type = "INCOME (BANK)"
            display_folder = category_account
            if not description: description = "Income Bank"
            
        # 5. Withdrawal
        elif type == "withdraw":
            target_acc = ACC_CASH
            source_acc = ACC_BANK
            display_type = "WITHDRAW (ATM)"
            display_folder = "Transfer: Bank -> Cash"
            if not description: description = "ATM Withdraw"

        # Execute
        success = write_to_ledger(description, amount, target_acc, source_acc)

        if success:
            await update.message.reply_text(
                f"✅ **Recorded: {display_type}**\n"
                f"📝 {description}\n"
                f"💰 {amount}\n"
                f"📂 `{display_folder}`", 
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("Failed to write to ledger file. Please check server logs.")

    except Exception as e:
        logging.error(f"System Error: {e}")
        await update.message.reply_text("An internal system error occurred.")

# ==========================================
# BOT COMMAND HANDLERS
# ==========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    await update.message.reply_text(
        "**Finance Bot Ready**\n\n"
        "**CASH Transactions:**\n"
        "`/food`, `/transport`, `/shop`\n"
        "`/health`, `/other`\n\n"
        "**BANK / DIGITAL Transactions:**\n"
        "`/qfood`, `/qtransport`, `/qshop`\n"
        "`/qbill`, `/qsub`\n\n"
        "**INCOME & TRANSFERS:**\n"
        "`/income` (Bank), `/gift` (Cash)\n"
        "`/withdraw` (ATM)",
        parse_mode='Markdown'
    )

# --- Cash Expenses ---
async def food(u, c): await handle_transaction(u, c, "Expenses:Food", "expense_cash")
async def transport(u, c): await handle_transaction(u, c, "Expenses:Transport", "expense_cash")
async def shop(u, c): await handle_transaction(u, c, "Expenses:Shopping", "expense_cash")
async def health(u, c): await handle_transaction(u, c, "Expenses:Health", "expense_cash")
async def other(u, c): await handle_transaction(u, c, "Expenses:Misc", "expense_cash")

# --- Bank/Digital Expenses (Prefix 'q') ---
async def qfood(u, c): await handle_transaction(u, c, "Expenses:Food", "expense_bank")
async def qtransport(u, c): await handle_transaction(u, c, "Expenses:Transport", "expense_bank")
async def qshop(u, c): await handle_transaction(u, c, "Expenses:Shopping", "expense_bank")
async def qbill(u, c): await handle_transaction(u, c, "Expenses:Utilities", "expense_bank")
async def qsub(u, c): await handle_transaction(u, c, "Expenses:Subscription", "expense_bank")

# --- Income & Transfers ---
async def income(u, c): await handle_transaction(u, c, "Income:Salary", "income_bank")
async def gift(u, c): await handle_transaction(u, c, "Income:Allowance", "income_cash")
async def withdraw(u, c): await handle_transaction(u, c, "ATM Withdraw", "withdraw")

# ==========================================
# MAIN ENTRY POINT
# ==========================================
if __name__ == '__main__':
    print("Bot is running...")
    application = ApplicationBuilder().token(TOKEN).build()
    
    # General
    application.add_handler(CommandHandler('start', start))
    
    # Expense Handlers (Cash)
    application.add_handler(CommandHandler('food', food))
    application.add_handler(CommandHandler('transport', transport))
    application.add_handler(CommandHandler('shop', shop))
    application.add_handler(CommandHandler('health', health))
    application.add_handler(CommandHandler('other', other))
    
    # Expense Handlers (Bank/Digital)
    application.add_handler(CommandHandler('qfood', qfood))
    application.add_handler(CommandHandler('qtransport', qtransport))
    application.add_handler(CommandHandler('qshop', qshop))
    application.add_handler(CommandHandler('qbill', qbill))
    application.add_handler(CommandHandler('qsub', qsub))
    
    # Income & Transfer Handlers
    application.add_handler(CommandHandler('income', income))
    application.add_handler(CommandHandler('gift', gift))
    application.add_handler(CommandHandler('withdraw', withdraw))
    
    application.run_polling()