# Loona Telegram Chatbot

## Türkçe Açıklama

Bu bot, nyxie Protogen Furry bir Telegram chatbotudur. Groq API ile çalışır ve DeepSeek-R1-Distill-Llama-70B modelini kullanır.

### Özellikler

- **Almanca Konuşma**: Bot her zaman Almanca olarak cevap verir ve türkçe çeviri sağlar
- **Loona Karakteri**: Helluva Boss dizisindeki Loona karakterinin kişiliği ve konuşma tarzını taklit eder
- **Sınırsız Bellek**: FAISS vektör veritabanı kullanarak sohbet geçmişini hatırlar
- **Kişiselleştirilmiş Deneyim**: Her kullanıcı için özel sohbet geçmişi tutar
- **Düşünce Süreçleri**: Bot düşünce süreçlerini `<think></think>` etiketleri içinde gizler

### Gereksinimler

```
python-telegram-bot>=20.0
python-dotenv
groq
faiss-cpu
numpy
```

### Kurulum

1. Repo'yu klonlayın:
   ```
   git clone <repo-url>
   cd hızlı-chatbot
   ```

2. Gerekli paketleri yükleyin:
   ```
   pip install -r requirements.txt
   ```

3. `.env` dosyasını düzenleyin:
   ```
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   GROQ_API_KEY=your_groq_api_key
   ```

4. Botu çalıştırın:
   ```
   python bot.py
   ```

### Kullanım

Telegram'da botu başlatın ve normal bir şekilde mesaj göndermeye başlayın. Bot, Loona karakteri olarak size Almanca yanıt verecek ve her yanıtın altında Türkçe çevirisi yer alacaktır.

### Teknik Ayrıntılar

- Sohbet geçmişi JSON dosyalarında saklanır
- FAISS vektör veritabanı ilgili konuşma geçmişini bulmak için kullanılır
- Groq API, Deepseek-R1-Distill-Llama-70B modeliyle entegre edilmiştir
- Bot, konuşma esnasında konuları takip eder ve tutarlı yanıtlar üretir

### Lisans

Bu proje GNU lisansı altında lisanslanmıştır.
