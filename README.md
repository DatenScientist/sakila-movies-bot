# 🎬 Sakila Movies Bot

This Telegram bot allows users to interact with the **Sakila Database** — a sample database used for educational purposes — by searching for movies and actors through a convenient chat interface.

---

## 🤖 Bot Features

### ⚙️ Key Capabilities

- **Asynchronous Telegram bot** with inline buttons
- **Smooth navigation** by movie categories, release years, and actor selection
- **Automatic logging** of all user actions into MongoDB

### 🔍 Movie Search

- **Search by movie title** — just type part of a movie name.
- **Filter movies by category** — e.g., Action, Comedy, Drama, etc.
- **Filter movies by release year** — from **1990 to 2025**.
- **View movie details** — enter the movie's index number from the search results to get:
  - **Film ID**
  - **Title**
  - **Release year**
  - **Description**
  - **Category**
  - **Length**
  - **Rating**

> 🎥 The movie details do **not include a list of actors**.

### 🎭 Actor Search

- **Search by actor's name** — partial names are accepted.
- **Select actor by ID number** from the list to view all movies they starred in.

### 📊 Query Statistics

- The bot tracks how often each movie, actor, category, and release year is queried.
- You can request the most frequently searched movies, actors, categories, or years.

---

## 🗄️ Database Info

- The bot connects to a **MySQL database** containing the Sakila schema.
- It also tracks search queries using **MongoDB**.
- The Sakila dataset is purely fictional and used only for demo and learning purposes.

---

## 🛠 Technologies Used

- **Python**
- **python-telegram-bot**
- **MySQL** (via `mysql-connector-python`)
- **MongoDB** (via `pymongo`)
- **Render.com** for deployment
- **dotenv** for managing environment variables

---

## 📁 Project Structure

```
sakila-movies-bot/
├── main.py                  # Bot entry point
├── sakila_commands.py      # Bot logic and DB queries
├── requirements.txt        # Dependencies
├── .env                    # Environment variables (not tracked by Git)
└── README.md               # Project description
```

---

## 🚀 Deployment

This bot is deployed using **Render** (Free Web Service Plan).

> ⚠️ Note: Render's free tier may cause the bot to go idle after a few minutes of inactivity. When idle, the first interaction may take a few seconds to wake the service back up.

To keep the bot running continuously, consider upgrading the Render plan or pinging the bot periodically using an uptime monitoring service.

---

## 📦 Installation (Local Testing)

1. Clone the repo:

```bash
git clone https://github.com/shukrullo-olimov/sakila-movies-bot.git
cd sakila-movies-bot
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up your `.env` file:

```
TOKEN=your_telegram_bot_token
DB_HOST=your_mysql_host
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_SAKILA=sakila
MONGO_URI=your_mongodb_uri
MONGO_DB=sakila_queries
```

4. Run the bot:

```bash
python main.py
```

---

## 🙌 Author

**Shukrullo Olimov** — created this project while halfway through his studies in the *Data Analyst* program at **IT Career Hub GmbH**. This bot served as the **final project** for the **Python Fundamentals** module.

---

## ⭐️ Support

If you found this project helpful, consider giving it a ⭐ on GitHub!

Feel free to fork, customize, or contribute!

---

> Made with ❤️ using Python, MySQL, MongoDB, and Sakila for educational & demo purposes.

