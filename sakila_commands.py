# Module of functions for working with SQL

import os
from dotenv import load_dotenv
import mysql.connector
from pymongo import MongoClient

load_dotenv("sakila.env")

# Connection to read
def connect_db():
    dbconfig = {
        'host': os.getenv("DB_HOST"),
        'user': os.getenv("DB_USER"),
        'password': os.getenv("DB_PASSWORD"),
        'database': os.getenv("DB_SAKILA")
    }

    return mysql.connector.connect(**dbconfig)

# Connecting to MongoDB Atlas to write and read the queries
def connect_mongo():
    mongo_uri = os.getenv("MONGO_URI")
    mongo_db = os.getenv("MONGO_DB")

    client = MongoClient(mongo_uri)
    return client[mongo_db]



# Getting list of movie categories
def category_list():
    connection = connect_db()
    cursor = connection.cursor()
    cursor.execute("SELECT category_id, name FROM sakila.category;")
    
    result = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    # Join the results into a single string with each row on a new line
    result_str = '\n'.join(f"{row[0]:2}. {row[1]}" for row in result)
    # Write the result string to a text file
    with open('categories.txt', 'w') as file:
        file.write(result_str)


# Creating category dictionary from category list
def create_category_map(file_path: str) -> dict:
    category_map = {}
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if line.strip():
                    # Extract category number and name
                    parts = line.split('.')
                    if len(parts) == 2:
                        category_id = parts[0].strip()
                        category_name = parts[1].strip()
                        category_map[category_id] = category_name
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    return category_map


# Sending the selected movie category to the query database
def insert_category(category_id: str, category_name: str):
    db = connect_mongo()
    collection = db["category"]

    existing = collection.find_one({"category_id": category_id})

    if existing:
        collection.update_one(
            {"category_id": category_id},
            {"$inc": {"count": 1}}
        )
    else:
        collection.insert_one({
            "category_id": category_id,
            "category_name": category_name,
            "count": 1
        })






# Sending the selected year of release of the film to the query base
def insert_year(year: int):
    db = connect_mongo()
    collection = db["year"]

    existing = collection.find_one({"release_year": year})

    if existing:
        collection.update_one(
            {"release_year": year},
            {"$inc": {"count": 1}}
        )
    else:
        collection.insert_one({
            "release_year": year,
            "count": 1
        })



def insert_movie(film_id, title, release_year, description, category_id, category_name, length, rating):
    db = connect_mongo()
    collection = db.movie

    existing = collection.find_one({"film_id": film_id})
    if existing:
        collection.update_one({"_id": existing["_id"]}, {"$inc": {"count": 1}})
    else:
        collection.insert_one({
            "film_id": film_id,
            "title": title,
            "release_year": release_year,
            "description": description,
            "category_id": category_id,
            "category_name": category_name,
            "length": length,
            "rating": rating,
            "count": 1
        })




def insert_actor(actor_id: str, first_name: str, last_name: str):
    db = connect_mongo()
    collection = db["actor"]

    existing = collection.find_one({"actor_id": actor_id})

    if existing:
        collection.update_one(
            {"actor_id": actor_id},
            {"$inc": {"count": 1}}
        )
    else:
        collection.insert_one({
            "actor_id": actor_id,
            "first_name": first_name,
            "last_name": last_name,
            "count": 1
        })






# Getting list of movies by category
def movies_by_category(category_id: str):
    # Ensure category_id is used directly in the SQL query
    query = """
        SELECT 
            film.film_id, title, release_year
        FROM
            film
                JOIN
            film_category ON film.film_id = film_category.film_id
        WHERE
            category_id = %s
        ORDER BY release_year
    """

    try:
        connection = connect_db()
        cursor = connection.cursor()
        cursor.execute(query, (category_id,))
        movies = cursor.fetchall()
        # Join the results into a single string with each row on a new line
        result_str = '\n'.join(f"[{row[0]:4}] {row[1]}, {row[2]}" for row in movies)
        result_str += '\n'
        # Save the result to a file or process it as needed
        with open('movies_by_cat.txt', 'w') as file:
            file.write(result_str)
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# Getting list of movies by year of release
def movies_by_year(year):
    query = """
        SELECT 
            film.film_id, title, category.name
        FROM
            film
                JOIN
            film_category ON film.film_id = film_category.film_id
                JOIN
            category ON film_category.category_id = category.category_id
        WHERE
            release_year = %s
        ORDER BY category.name;
    """                    
    connection = connect_db()
    cursor = connection.cursor()
    cursor.execute(query, (str(year), ))
                    
    movies = cursor.fetchall()
    
    cursor.close()
    connection.close()
        
    # Join the results into a single string with each row on a new line
    result_str = '\n'.join(f"[{row[0]:4}] {row[1]}, {row[2]}" for row in movies)
    result_str += '\n'
    # Write the result string to a text file
    with open('movies_by_year.txt', 'w') as file:
        # file.write(f'Films by release year:\n' + result_str)
        file.write(result_str)


# Getting list of actors by name
def actors_by_name(actor_name: str):
    query = f"""
        SELECT 
            actor_id, first_name, last_name
        FROM
            actor
        WHERE
            first_name LIKE '%{actor_name}%' or last_name LIKE '%{actor_name}%';
    """
    try:
        connection = connect_db()
        cursor = connection.cursor()
        cursor.execute(query)
        actors = cursor.fetchall()
        # Join the results into a single string with each row on a new line
        result_str = '\n'.join(f"[{row[0]:3}] {row[1]} {row[2]}" for row in actors)
        # Save the result to a file or process it as needed
        with open('actors_by_name.txt', 'w') as file:
            file.write(result_str)
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# Getting list of movies by title
def movies_by_title(movie_title: str):
    query = f"""
        SELECT 
            film_id, title, release_year
        FROM
            film
        WHERE
            title LIKE '%{movie_title}%';
    """
    try:
        connection = connect_db()
        cursor = connection.cursor()
        cursor.execute(query)
        movies = cursor.fetchall()
        # Join the results into a single string with each row on a new line
        result_str = '\n'.join(f"[{row[0]:4}] {row[1]}, {row[2]}" for row in movies)
        # Save the result to a file or process it as needed
        with open('movies_by_title.txt', 'w') as file:
            file.write(result_str)
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# Getting list of movies by actor and sending the actor to the query database
def movies_by_actor(actor_id: str):
    query = """
        SELECT 
            film.film_id, title, release_year
        FROM
            film
                JOIN
            film_actor ON film.film_id = film_actor.film_id
        WHERE
            actor_id = %s;
    """
    actor_query = """
        SELECT 
            actor_id, first_name, last_name
        FROM
            actor
        WHERE
            actor_id = %s;
    """

    try:
        connection = connect_db()
        cursor = connection.cursor()

        # Получаем фильмы
        cursor.execute(query, (actor_id,))
        movies = cursor.fetchall()

        # Сохраняем в файл
        result_str = '\n'.join(f"[{row[0]:4}] {row[1]}, {row[2]}" for row in movies)
        with open('movies_by_actor.txt', 'w') as file:
            file.write(result_str)

        # Получаем данные об актёре
        cursor.execute(actor_query, (actor_id,))
        actor = cursor.fetchone()
        actor_id, first_name, last_name = actor

        # MongoDB
        insert_actor(actor_id, first_name, last_name)

    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return first_name, last_name






# Getting detailed information about a movie by ID number and sending the movie to the query database
def movie_by_id(movie_id: str):
    query = """
        SELECT 
            film.film_id,
            title,
            release_year,
            description,
            category.category_id,
            name,
            length,
            CASE rating
                WHEN 'G' THEN 'General Audiences'
                WHEN 'PG' THEN 'Parental Guidance Suggested'
                WHEN 'PG-13' THEN 'Parents Strongly Cautioned'
                WHEN 'R' THEN 'Restricted'
                ELSE 'Adults Only'
            END AS rating
        FROM
            film
                JOIN
            film_category ON film.film_id = film_category.film_id
                JOIN
            category ON film_category.category_id = category.category_id
        WHERE
            film.film_id = %s;
    """

    try:
        connection = connect_db()
        cursor = connection.cursor()
        cursor.execute(query, (movie_id,))
        movie = cursor.fetchone()

        film_id, title, release_year, description, category_id, category_name, length, rating = movie

        # Сохраняем в файл
        result_str = f"""Film ID: [{film_id}]
Title: {title}
Release year: {release_year}
Description: {description}
Category: {category_name}
Length: {length}
Rating: {rating}"""
        with open('movie_details.txt', 'w') as file:
            file.write(result_str)

        # MongoDB
        insert_movie(
            film_id=film_id,
            title=title,
            release_year=release_year,
            description=description,
            category_id=category_id,
            category_name=category_name,
            length=length,
            rating=rating
        )

    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()





# Getting the most popular queries by movies
def queries_by_movies():
    db = connect_mongo()
    collection = db["movie"]

    top_movies = collection.find().sort("count", -1).limit(10)

    result_str = '\n'.join(
        f"{i+1:2}. [{doc['film_id']}] {doc['title']}, {doc['release_year']} - {doc['count']}"
        for i, doc in enumerate(top_movies)
    )

    with open('queries_by_movies.txt', 'w') as file:
        file.write(result_str)




# Getting the most popular queries by category
def queries_by_category():
    db = connect_mongo()
    collection = db["category"]

    top_categories = collection.find().sort("count", -1).limit(10)

    result_str = '\n'.join(
        f"{i+1:2}.  {doc['category_name']} - {doc['count']}"
        for i, doc in enumerate(top_categories)
    )

    with open('queries_by_category.txt', 'w') as file:
        file.write(result_str)





# Getting the most popular queries by actors
def queries_by_actors():
    db = connect_mongo()
    collection = db["actor"]

    top_actors = collection.find().sort("count", -1).limit(10)

    result_str = '\n'.join(
        f"{i+1:2}.  {doc['first_name']} {doc['last_name']} - {doc['count']}"
        for i, doc in enumerate(top_actors)
    )

    with open('queries_by_actors.txt', 'w') as file:
        file.write(result_str)





# Getting the most popular queries by year of release
def queries_by_year():
    db = connect_mongo()
    collection = db["year"]

    top_years = collection.find().sort("count", -1).limit(10)

    result_str = '\n'.join(
        f"{i+1:2}.  {doc['release_year']} - {doc['count']}"
        for i, doc in enumerate(top_years)
    )

    with open('queries_by_year.txt', 'w') as file:
        file.write(result_str)


