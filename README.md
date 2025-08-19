# CryptoUZSBot — Aiogram 3.21

📊 **CryptoUZSBot** — bu Telegram boti barcha kripto valyutalarning narxini **AQSh dollari** va **Oʻzbekiston soʻmida (UZS)** ko‘rsatib beradi. Bot **CoinCap API** va **Binance API** orqali kripto narxlarni, **Markaziy Bank (CBU) API** orqali USD→UZS kursini oladi. Kod **aiogram 3.21** asosida `start_polling` rejimida yozilgan.

## ✨ Asosiy imkoniyatlari
- 🔎 Kripto qidirish: nom yoki symbol orqali (masalan: `btc`, `bitcoin`).
- 📈 `/top N` buyrug‘i orqali eng yirik `N` ta kriptolarni ko‘rsatish.
- 🔄 Har 60 soniyada avtomatik yangilanish.
- 📱 Inline qidiruv (chat ichida @botname so‘zi bilan).
- 📃 Sahifalash (⬅️ ➡️ tugmalar orqali).
- 🇺🇿 Kriptolar narxi AQSh dollarida va so‘mda.
- ⚡ Juda tez va kechikishsiz ishlash uchun optimallashtirilgan.

## 🛠 O‘rnatish va ishga tushirish
### 1. Python o‘rnatish
Python 3.12 yoki undan yuqori versiyasi kerak.

### 2. Kutubxonalar o‘rnatish
```bash
pip install aiogram==3.21.0 aiohttp python-dotenv
```

### 3. Token sozlash
`.env` faylda yoki terminal orqali Telegram bot tokenini belgilang:
```bash
export TOKEN=123456:ABCDEF...
```

### 4. Botni ishga tushirish
```bash
python main.py
```

## 📋 Buyruqlar
- `/start` — Boshlash
- `/menu` — Asosiy menyu
- `/top 20` — TOP 20 kriptolar
- `btc`, `eth` va hokazo — Qidiruv

## 📂 Loyihaning tarkibi
```
├── main.py     # Asosiy kod (bot)
├── .env        # Bot tokeni (TOKEN=...)
└── README.md   # Hujjat
```

## 🔒 Xavfsizlik
- Tokenni hech qachon ommaga chiqarmang.
- Agar serverda ishlatsangiz, `.env` faylni `.gitignore`ga qo‘shing.

## 👨‍💻 Muallif
Yuqori darajada optimallashtirilgan professional kod — barcha joyi xatosiz ishlashga tayyor.
