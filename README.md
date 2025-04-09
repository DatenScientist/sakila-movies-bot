# 🎬 Telegram Bot for Movie Search (Sakila DB)

This bot allows you to search for movies, actors, categories and release years using the Sakila database. All queries are also logged in MongoDB.

## 🔧 Possibilities

- 🔍 Search movies by title
- 🎭 Search actors and watch their movies
- 📅 Search by year of release
- 📂 Filter by categories
- 📊 Collect query statistics in MongoDB Atlas

## 🛠 Technology stack

- Python 🐍
- MySQL (Sakila DB)
- MongoDB Atlas ☁️
- python-telegram-bot
- dotenv

## 🚀 How to launch

1. Clone the repository:

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file with the following variables:

```env
TOKEN=your_telegram_token
DB_HOST=your_host_for_sakila
DB_USER=your_user
DB_PASSWORD=your_password
DB_SAKILA=sakila
MONGO_URI=your_mongo_uri
MONGO_DB=sakila_queries
```

4. Launch the bot:

```bash
python bot.py
```

## 📁 Project structure

```
├── main.py
├── sakila_commands.py
├── .env
├── requirements.txt
└── README.md
```

## 🤝 Author

The bot is written with a love of programming ❤️  
Author: @DatenScientist