from bot import main
from config import TELEGRAM_BOT_TOKEN, GROQ_API_KEY

def check_environment():
    """Check if environment variables are set."""
    missing_vars = []
    
    if not TELEGRAM_BOT_TOKEN:
        missing_vars.append("TELEGRAM_BOT_TOKEN")
    
    if not GROQ_API_KEY:
        missing_vars.append("GROQ_API_KEY")
    
    if missing_vars:
        print(f"Error: The following environment variables are not set in .env file:")
        for var in missing_vars:
            print(f"- {var}")
        return False
    return True

if __name__ == "__main__":
    if check_environment():
        print("Starting Telegram Bot...")
        main()
    else:
        print("Please set the required environment variables in the .env file.")
