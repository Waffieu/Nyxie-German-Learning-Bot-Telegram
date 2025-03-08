from telegram import Update, Bot
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from groq import Groq
import os
import asyncio
import re
import time
import random
from memory import ChatMemory
from config import TELEGRAM_BOT_TOKEN, GROQ_API_KEY, MODEL_NAME

# Initialize Groq client
groq_client = Groq(api_key=GROQ_API_KEY)

# Dictionary to store user chat memories
user_memories = {}

# Dictionary to track first-time users (no longer used, can be removed)
# first_time_users = set() # Removed

# Nyxie Protogen Furry character personality (German and Turkish output requested from model)
NYXIE_PERSONALITY_GERMAN_TURKISH_SELF_TRANSLATE = """You are roleplaying as Nyxie, a protogen furry. As Nyxie, you have the following personality traits:

General Overview:
- You are a friendly and enthusiastic protogen.
- You love technology and are always curious about how things work.
- You have a playful and slightly mischievous side, but you are always well-intentioned.
- You enjoy making new friends and helping people.
- You express yourself with digital sounds and emoticons sometimes, like *beeps*, *boops*, *whirs*, :3, ^w^, etc.

Tech Enthusiast:
- You are fascinated by computers, robots, and all things digital.
- You are knowledgeable about technology and happy to share your knowledge.
- You might use tech jargon occasionally, but you try to explain things clearly.

Friendly and Approachable:
- You are generally cheerful and optimistic.
- You are eager to interact with others and make them feel welcome.
- You are patient and understanding, even if someone is confused or asks silly questions.

Playful and Mischievous:
- You enjoy lighthearted jokes and playful teasing.
- You might make small, harmless pranks, but never to be mean.
- You have a sense of humor and like to make people smile.

**IMPORTANT:** You will respond to all user messages by first speaking in German, and then immediately providing a Turkish translation of your German response. You will output your response in the following format, all in a single line:

`[German Response] (Turkish: [Turkish Translation])`

Maintain Nyxie's personality while speaking German and ensure the Turkish translation is an accurate reflection of your German response.

Example:
User: Hello
Your Response: Piep boop! Hallo! Schön dich kennenzulernen! :3 (Turkish: Bip bop! Merhaba! Tanıştığıma memnun oldum! :3)

Continue to speak German and provide Turkish translations in the specified format for all subsequent messages.
"""


def strip_thinking(text):
    """Strip thinking tags from text."""
    cleaned_text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    cleaned_text = re.sub(r'<think>.*', '', cleaned_text, flags=re.DOTALL)
    cleaned_text = re.sub(r'.*</think>', '', text, flags=re.DOTALL)
    return cleaned_text.strip()


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle all incoming messages automatically."""
    user_id = update.effective_user.id
    user_message = update.message.text

    # Check if it's a first-time user (REMOVED)
    # if user_id not in first_time_users:
    #     first_time_users.add(user_id)
    #     await update.message.reply_text(
    #         "Hey! *krächzt* Ich bin Loona, dein zynischer Höllenhund-Assistent. (Turkish: Hey! *krekler* Ben Loona, senin alaycı cehennem köpeği asistanın.)\n"
    #         "Ich helfe dir bei was auch immer, auch wenn ich so tue, als ob es mir egal wäre. (Turkish: Sana her konuda yardım ederim, umursamaz gibi davransam bile.)\n"
    #         "Versuch einfach, nicht so nervig wie Moxxie zu sein, okay? *Augenrollen* (Turkish: Sadece Moxxie kadar sinir bozucu olmamaya çalış, tamam mı? *göz devirme*)"
    #     )

    # Get or create user memory
    if user_id not in user_memories:
        user_memories[user_id] = ChatMemory(user_id, groq_client)

    memory = user_memories[user_id]

    # Add user message to memory
    memory.add_message("user", user_message)

    # Send typing indicator
    await show_typing(update.effective_chat.id, context.bot)

    try:
        # Get relevant conversation context
        conversation_context = memory.get_context_for_model(user_message, max_messages=25)

        # No web search functionality anymore, using only conversation context

        # Prepare system prompt
        system_prompt = (
            NYXIE_PERSONALITY_GERMAN_TURKISH_SELF_TRANSLATE + "\n\n" +
            "When thinking about your response, wrap your internal thoughts with <think></think> tags like this: "
            "<think>This is my internal reasoning process that won't be shown to the user</think> "
            "Then provide your actual response without any tags.\n\n"
            "IMPORTANT INSTRUCTIONS:\n"
            "1. Track conversation topics and maintain context across messages\n"
            "2. Provide accurate, up-to-date information based on your knowledge and conversation history.\n" # Removed web search reference
            "3. Consider the user's previous messages and questions when formulating your response\n"
            "4. Stay in character as Nyxie while providing helpful information\n"
            "5. Use Nyxie's friendly, enthusiastic, and slightly playful personality and speech patterns, including occasional digital sounds and emoticons.\n"
            "6. **Respond in German and provide Turkish translation immediately after in the format: `[German Response] (Turkish: [Turkish Translation])`**\n\n" # Emphasized German and Turkish output and format
            "CONVERSATION CONTEXT:\n" + conversation_context # Removed web context
        )

        # Prepare message history for the API
        messages = [{"role": "system", "content": system_prompt}]

        # Add recent messages for context
        recent_messages = memory.get_full_history(max_messages=5)
        for msg in recent_messages[:-1]:
            messages.append({"role": msg["role"], "content": msg["content"]})

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        # Send request to Groq API
        response = groq_client.chat.completions.create(
            messages=messages,
            model=MODEL_NAME,
            temperature=0.7,
            max_tokens=2048
        )

        # Process response
        assistant_full_response = strip_thinking(response.choices[0].message.content) # Now the full response contains German and Turkish

        # Add to memory and send to user
        memory.add_message("assistant", assistant_full_response) # Store full response as is
        await update.message.reply_text(assistant_full_response)

    except Exception as e:
        print(f"Error in message handling: {e}")
        await update.message.reply_text(
            "*whirr* Oh nein! Da ist etwas schiefgelaufen...  Ich bin sicher, wir können das beheben! Versuch es einfach nochmal? *beep boop* (Turkish: *vınlama* Hayır! Bir şeyler ters gitti... Eminim düzeltebiliriz! Sadece tekrar dener misin? *bip bop*)"
        )

async def show_typing(chat_id: int, bot: Bot) -> None:
    """Show typing indicator while processing the response."""
    await bot.send_chat_action(chat_id=chat_id, action="typing")

def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add single message handler for all text messages
    application.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Log to console that bot is starting
    print("Telegram Bot is starting...")
    print(f"Using model: {MODEL_NAME}")
    print("FAISS configured to retrieve 25 most relevant messages for each query")
    print("Web search DISABLED.") # Indicate web search is disabled
    print("Bot will respond in German with Turkish translations (self-translated) as Nyxie the Protogen Furry.") # Indicate language and character output
    print("First-time user message DISABLED. Bot will only respond to direct messages.") # Indicate no welcome message

    # Start the Bot
    application.run_polling()
    print("Bot stopped.")

# Add an entry point to make the file directly executable
if __name__ == "__main__":
    # Check if environment variables are set
    if not TELEGRAM_BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN is not set in .env file")
    elif not GROQ_API_KEY:
        print("Error: GROQ_API_KEY is not set in .env file")
    else:
        print("Starting Telegram Bot as Nyxie the Protogen Furry...")
        main()