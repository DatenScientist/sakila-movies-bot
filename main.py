
import asyncio
from aiohttp import web
import nest_asyncio
import os
from dotenv import load_dotenv
from typing import Final
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters, ContextTypes
import logging
from sakila_commands import category_list, create_category_map, movies_by_category, movies_by_year, actors_by_name, movies_by_title, insert_category, insert_year, movies_by_actor, movie_by_id, queries_by_movies, queries_by_category, queries_by_actors, queries_by_year

load_dotenv("sakila.env")
TOKEN: Final = os.getenv("TOKEN")
BOT_USERNAME: Final = '@sakila_movies_bot'

# Pagination variables
MOVIES_PER_PAGE = 10
YEARS_PER_PAGE = 10

# Generate keyboard for years
def generate_year_keyboard(page: int):
    years = [str(year) for year in range(1990 + page * YEARS_PER_PAGE, 1990 + (page + 1) * YEARS_PER_PAGE)]
    keyboard = [
        [InlineKeyboardButton(year, callback_data=f'year_{year}') for year in years[i:i+5]]
        for i in range(0, len(years), 5)
    ]
    navigation_buttons = []
    if page > 0:
        navigation_buttons.append(InlineKeyboardButton("Previous", callback_data=f'prev_{page}'))
    if page < (2025 - 1990) // YEARS_PER_PAGE:
        navigation_buttons.append(InlineKeyboardButton("Next", callback_data=f'next_{page}'))
    if navigation_buttons:
        keyboard.append(navigation_buttons)
    return InlineKeyboardMarkup(keyboard)


# Generate keyboard for movies by years
def generate_movie_year_keyboard(page: int, total_pages: int, year: str) -> InlineKeyboardMarkup:
    keyboard = []
    navigation_buttons = []
    if page > 0:
        navigation_buttons.append(InlineKeyboardButton("Previous", callback_data=f'year_{year}_prev_{page}'))
    if (page == 0) or (page < total_pages - 1):
        navigation_buttons.append(InlineKeyboardButton("Next", callback_data=f'year_{year}_next_{page}'))
    if navigation_buttons:
        keyboard.append(navigation_buttons)
    return InlineKeyboardMarkup(keyboard)


# Generate keyboard for movies by category
def generate_pagination_keyboard(page: int, total_pages: int, category_id: str) -> InlineKeyboardMarkup:
    keyboard = []
    navigation_buttons = []
    if page > 0:
        navigation_buttons.append(InlineKeyboardButton("Previous", callback_data=f'cat_{category_id}_prev_{page-1}'))
    if (page == 0) or (page < total_pages - 1):
        navigation_buttons.append(InlineKeyboardButton("Next", callback_data=f'cat_{category_id}_next_{page+1}'))
    if navigation_buttons:
        keyboard.append(navigation_buttons)
    return InlineKeyboardMarkup(keyboard)



# Commands

# Start command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""
Hello!

Welcome to the Sakila bot. I will help you search for movies by different parameters.

First, I recommend enabling the movie search mode by title or by movie ID number. To do this, press /keyword and select the <Movie ID or Movie Title> mode
""")


# Help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('''Hello!
/start: Welcomes the user.
/help: Provides help information.
/keyword: Allows the user to choose between searching by movie title or actor name.
/category: Lists movie categories for selection.
/release: Allows the user to search for movies by release year.
/queries - The command displays a list of the most popular queries that were searched''')



# Keyword command
async def keyword_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Movie ID or Movie Title", callback_data="title")],
        [InlineKeyboardButton("Actor ID or Actor Name", callback_data="actor")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Search by keyword\nSelect search by title or by actor:", reply_markup=reply_markup)


# Keyword button
async def button_keyword(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    # Reset states
    context.user_data['searching_actor'] = False
    context.user_data['searching_title'] = False
    context.user_data['expecting_actor_id'] = False
    context.user_data['expecting_movie_id'] = False
    
    if data == "actor":
        context.user_data['searching_actor'] = True
        await query.message.reply_text("<Actor ID or Actor Name> mode is ON.\nEnter the the actor name or actor ID you want to search for:")
    elif data == "title":
        context.user_data['searching_title'] = True
        await query.message.reply_text("<Movie ID or Movie Title> mode is ON.\nEnter the movie title or movie ID you want to search for:")



# Category command
async def category_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    category_list()  # Refresh the categories list
    with open('categories.txt', 'r') as file:
        categories = file.readlines()

    keyboard = []
    for i in range(0, len(categories), 2):
        row = []
        for j in range(2):
            if i + j < len(categories):
                category_id, category_name = categories[i + j].strip().split('. ')
                row.append(InlineKeyboardButton(category_name, callback_data=f'cat_{category_id}_page_0'))
        keyboard.append(row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Select a category:', reply_markup=reply_markup)


# Category button
async def button_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    print(f"button_category working: {data}")
    # Load the category map from the file
    CATEGORY_MAP = create_category_map('categories.txt')
    try:
        # Extract category ID and page number from callback data
        if data.startswith("cat_"):
            parts = data.split('_')
            print(f"Parsed parts: {parts}")  # Debugging: Print the parsed parts
            direction = 'page'
            if len(parts) == 4 and parts[1].isdigit() and parts[3].isdigit():
                category_id = parts[1]
                page = int(parts[3])
                direction = parts[2]
                
                # Fetch movies for the selected category
                movies_by_category(category_id)
                
                with open('movies_by_cat.txt', 'r') as file:
                    movies = file.readlines()
                
                MOVIES_PER_PAGE = 10
                start = page * MOVIES_PER_PAGE
                end = start + MOVIES_PER_PAGE
                movies_page = movies[start:end]

                category_name = CATEGORY_MAP.get(category_id, 'Unknown Category')
                
                total_pages = (len(movies) + MOVIES_PER_PAGE - 1) // MOVIES_PER_PAGE
                reply_markup = generate_pagination_keyboard(page, total_pages, category_id)
                new_text = f'Films by category "{category_name}":\n\n' + ''.join(movies_page) + '\nMovies are sorted by release YEAR'

                if direction == 'page':
                    new_text = f'Films by category "{category_name}":\n\n' + ''.join(movies_page) + '\nMovies are sorted by release YEAR'
                    insert_category(category_id, category_name)
                    await query.message.reply_text(new_text, reply_markup=reply_markup)
                else:
                    await query.message.edit_text(new_text, reply_markup=reply_markup)
                
            else:
                raise ValueError("Invalid callback data format.")
        else:
            raise ValueError("Callback data does not start with 'cat_'.")
    
    except ValueError as e:
        print(f"Error: {e}")
        await query.message.reply_text('Invalid callback data format. Please try again.')
    except FileNotFoundError:
        await query.message.reply_text('Movies data file not found.')
    except Exception as e:
        print(f"Unexpected error: {e}")
        await query.message.reply_text('An unexpected error occurred. Please try again later.')



# Relese years command
async def release_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = generate_year_keyboard(0)
    await update.message.reply_text('Search by movie release date\nSelect years from 1990 to 2025:', reply_markup=reply_markup)


# Relese years button
async def button_release(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    print(f"button_release working: {data}")  # Debugging: Print the received callback data

    try:
        if data.startswith('year_'):
            parts = data.split('_')
            year = parts[1]
            page = 0
            direction = 'next'
            if len(parts) == 4:
                direction = parts[2]
                page = int(parts[3])
                if direction == 'next':
                    page += 1
                elif direction == 'prev':
                    page -= 1

            movies_by_year(year)
            with open('movies_by_year.txt', 'r') as file:
                movies = file.readlines()

            total_pages = (len(movies) + MOVIES_PER_PAGE - 1) // MOVIES_PER_PAGE
            movies_page = movies[page * MOVIES_PER_PAGE: (page + 1) * MOVIES_PER_PAGE]

            reply_markup = generate_movie_year_keyboard(page, total_pages, year)
            new_text = f'Films released in {year}:\n\n' + ''.join(movies_page) + '\nFilms are sorted by CATEGORY'

            if page == 0 and direction == 'next':
                new_text = f'Films released in {year}:\n\n' + ''.join(movies_page) + '\nFilms are sorted by CATEGORY'
                insert_year(year)
                await query.message.reply_text(new_text, reply_markup=reply_markup)
            else:
                await query.message.edit_text(new_text, reply_markup=reply_markup)
        elif data.startswith('next_'):
            page = int(data.split('_')[1]) + 1
            reply_markup = generate_year_keyboard(page)
            await query.message.edit_text('Search by movie release date\nSelect years from 1990 to 2025:', reply_markup=reply_markup)
        elif data.startswith('prev_'):
            page = int(data.split('_')[1]) - 1
            reply_markup = generate_year_keyboard(page)
            await query.message.edit_text('Search by movie release date\nSelect years from 1990 to 2025:', reply_markup=reply_markup)
        else:
            raise ValueError("Invalid callback data format.")
    except ValueError as e:
        print(f"ValueError: {e}")
        await query.message.reply_text('Invalid callback data format. Please try again.')
    except FileNotFoundError:
        await query.message.reply_text('Movies data file not found.')
    except Exception as e:
        print(f"Unexpected error: {e}")
        await query.message.reply_text('An unexpected error occurred. Please try again later.')



# Query command
async def query_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Queries by movies", callback_data="query_movies")],
        [InlineKeyboardButton("Queries by actors", callback_data="query_actors")],
        [InlineKeyboardButton("Queries by category", callback_data="query_category")],
        [InlineKeyboardButton("Queries by year of release", callback_data="query_year")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("The most popular queries that were searched:", reply_markup=reply_markup)


# Query button
async def button_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "query_movies":
        # Handle queries by movies
        queries_by_movies()
        try:
            with open('queries_by_movies.txt', 'r') as file:
                queries = file.read()
            await query.message.reply_text(f"Here are the most popular queries by movies:\n\n{queries}")
        except FileNotFoundError:
            await query.message.reply_text("The file 'queries_by_movies.txt' was not found.")
        except Exception as e:
            await query.message.reply_text(f"An error occurred: {e}")
    elif data == "query_actors":
        # Handle queries by actors
        queries_by_actors()
        try:
            with open('queries_by_actors.txt', 'r') as file:
                queries = file.read()
            await query.message.reply_text(f"Here are the most popular queries by actors:\n\n{queries}")
        except FileNotFoundError:
            await query.message.reply_text("The file 'queries_by_actors.txt' was not found.")
        except Exception as e:
            await query.message.reply_text(f"An error occurred: {e}")
    elif data == "query_category":
        # Handle queries by category
        queries_by_category()
        try:
            with open('queries_by_category.txt', 'r') as file:
                queries = file.read()
            await query.message.reply_text(f"Here are the most popular queries by category:\n\n{queries}")
        except FileNotFoundError:
            await query.message.reply_text("The file 'queries_by_category.txt' was not found.")
        except Exception as e:
            await query.message.reply_text(f"An error occurred: {e}")
    elif data == "query_year":
        # Handle queries by year of release
        queries_by_year()
        try:
            with open('queries_by_year.txt', 'r') as file:
                queries = file.read()
            await query.message.reply_text(f"Here are the most popular queries by year:\n\n{queries}")
        except FileNotFoundError:
            await query.message.reply_text("The file 'queries_by_year.txt' was not found.")
        except Exception as e:
            await query.message.reply_text(f"An error occurred: {e}")



# Handle of text
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    is_searching_actor = context.user_data.get('searching_actor', False)
    is_searching_title = context.user_data.get('searching_title', False)
    is_expecting_actor_id = context.user_data.get('expecting_actor_id', False)
    is_expecting_movie_id = context.user_data.get('expecting_movie_id', False)

    print(f"User input: {user_input}")
    print(f"Current states - is_searching_actor: {is_searching_actor}, is_searching_title: {is_searching_title}, is_expecting_actor_id: {is_expecting_actor_id}, is_expecting_movie_id: {is_expecting_movie_id}")

    if is_searching_actor or is_expecting_actor_id:
        if user_input.isdigit():
            actor_id = user_input
            first_name, last_name = movies_by_actor(actor_id)
            with open('movies_by_actor.txt', 'r') as file:
                movies = file.readlines()
            if movies:
                context.user_data['expecting_actor_id'] = False
                context.user_data['expecting_movie_id'] = True  # Set next state
                await update.message.reply_text(f'Movies with {first_name} {last_name}:\n\n' + ''.join(movies) + '\n\nTo get information about a movie, go to the movie search mode by title or by movie ID number. To do this, press /keyword and select the <Movie ID or Movie Title> mode.')
            else:
                await update.message.reply_text('No movies found for that actor ID.')
        else:
            actors_by_name(user_input)
            with open('actors_by_name.txt', 'r') as file:
                actors = file.readlines()
            if actors:
                context.user_data['searching_actor'] = True  # Keep the search by actor state
                context.user_data['expecting_actor_id'] = True  # Keep expecting actor ID state
                await update.message.reply_text('Actors found:\n\n' + ''.join(actors) + '\n\nEnter the actor ID to see the movies they played in or enter another actor name:')
            else:
                await update.message.reply_text('No actors found with that name.')

    elif is_searching_title or is_expecting_movie_id:
        if user_input.isdigit():
            movie_id = user_input
            movie_by_id(movie_id)
            with open('movie_details.txt', 'r') as file:
                movie_details = file.read()
            if movie_details:
                context.user_data['expecting_movie_id'] = False
                await update.message.reply_text('Movie details:\n\n' + movie_details)
            else:
                await update.message.reply_text('No details found for that movie ID.')
        else:
            movies_by_title(user_input)
            with open('movies_by_title.txt', 'r') as file:
                movies = file.readlines()
            if movies:
                context.user_data['searching_title'] = True  # Keep the search by title state
                context.user_data['expecting_movie_id'] = True  # Keep expecting movie ID state
                await update.message.reply_text('Movies found:\n\n' + ''.join(movies) + '\n\nEnter the movie ID to get more details or enter another movie title:')
            else:
                await update.message.reply_text('No movies found with that title.')

    else:
        await update.message.reply_text("I'm sorry, I didn't understand that command. Please choose an option from the menu or type /help for assistance.")



# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
# Reducing the log level for httpx
logging.getLogger("httpx").setLevel(logging.WARNING)

async def handle_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")
    # logger.error(f"Update {update} caused error {context.error}")



async def keep_alive():
    app = web.Application()
    app.router.add_get('/', lambda request: web.Response(text="Bot is running"))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()
    print("Keep-alive server is running on port 8080")
    
# The main part
async def main():
    app = (Application.builder().token(TOKEN).build())
    
    # Handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("keyword", keyword_command))
    app.add_handler(CommandHandler("category", category_command))
    app.add_handler(CommandHandler("release", release_command))
    app.add_handler(CommandHandler("queries", query_command))
    
    app.add_handler(CallbackQueryHandler(button_keyword, pattern="^(title|actor)$"))
    app.add_handler(CallbackQueryHandler(button_category, pattern=r"^cat_\d+"))
    app.add_handler(CallbackQueryHandler(button_release, pattern=r'^(year_|next_|prev_)'))
    app.add_handler(CallbackQueryHandler(button_query, pattern=r"^query_(movies|actors|category|year)$"))
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Log all errors
    app.add_error_handler(handle_error)
    
    # Launching the bot
    logging.info("Bot is running...")
    await asyncio.gather(
        keep_alive(),  # Keep-alive сервер
        app.initialize(),
        app.start(),
        app.updater.start_polling(),
    )

    # Waiting for the stop (Ctrl+C)
    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Stopping the bot...")

    # Finish it carefully
    await app.updater.stop()
    await app.stop()
    await app.shutdown()
    logging.info("Bot has been stopped.")

# Launch
if __name__ == '__main__':
    import nest_asyncio
    nest_asyncio.apply()

    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\nBot stopped gracefully. Goodbye 👋")

