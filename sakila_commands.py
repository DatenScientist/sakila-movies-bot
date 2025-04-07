# Module of functions for working with SQL

import os
from dotenv import load_dotenv
import mysql.connector

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


# Connection to write and read the queries
def connect_query_db():
    dbconfig = {
        'host': os.getenv("DB_HOST"),
        'user': os.getenv("DB_USER"),
        'password': os.getenv("DB_PASSWORD"),
        'database': os.getenv("DB_PROJECT")
    }

    return mysql.connector.connect(**dbconfig)


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
    query = """
        INSERT INTO search_queries (category_id, category_name) VALUES (%s, %s);
    """
    
    try:
        connection = connect_query_db()
        cursor = connection.cursor()
        cursor.execute(query, (category_id, category_name))
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Sending the selected year of release of the film to the query base
def insert_year(year):
    query = f"""
    INSERT INTO search_queries (release_year) VALUES ({year});
    """
    
    try:
        connection = connect_query_db()
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


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
    # Ensure category_id is used directly in the SQL query
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
    insert_actor = """
        INSERT INTO Project_Shukrullo.search_queries (actor_id, first_name, last_name) 
        VALUES (%s, %s, %s);
    """
    
    try:
        connection = connect_db()
        cursor = connection.cursor()
        cursor.execute(query, (actor_id,))
        movies = cursor.fetchall()
        # Join the results into a single string with each row on a new line
        result_str = '\n'.join(f"[{row[0]:4}] {row[1]}, {row[2]}" for row in movies)
        # Save the result to a file or process it as needed
        with open('movies_by_actor.txt', 'w') as file:
            file.write(result_str)
        cursor.execute(actor_query, (actor_id,))
        actor = cursor.fetchone()
        actor_id, first_name, last_name = actor
        cursor.execute(insert_actor, (actor_id, first_name, last_name))
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
    return first_name, last_name


# Getting detailed information about a movie by ID number and sending the movie to the query database
def movie_by_id(movie_id: str):
    # Ensure category_id is used directly in the SQL query
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
    insert_movie = """
        INSERT INTO Project_Shukrullo.search_queries 
            (film_id, title, release_year, description, category_id, category_name) 
        VALUES (%s, %s, %s, %s, %s, %s);
    """
    
    try:
        connection = connect_db()
        cursor = connection.cursor()
        cursor.execute(query, (movie_id,))
        movie = cursor.fetchone()
        film_id, title, release_year, description, category_id, category_name, length, rating = movie
        
        # Join the results into a single string with each row on a new line
        result_str = f"""Film ID: [{film_id}]
Title: {title}
Release year: {release_year}
Description: {description}
Category: {category_name}
Length: {length}
Rating: {rating}"""
        
        # Save the result to a file or process it as needed
        with open('movie_details.txt', 'w') as file:
            file.write(result_str)
        
        cursor.execute(insert_movie, (film_id, title, release_year, description, category_id, category_name))
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# Getting the most popular queries by movies
def queries_by_movies():
    query = """
        SELECT 
            film_id, title, release_year, COUNT(title) AS cnt_query,
            ROW_NUMBER() OVER (ORDER BY COUNT(title) DESC) AS row_by_count
        FROM
            search_queries
        WHERE
            title IS NOT NULL
        GROUP BY title
        LIMIT 10;
    """
    try:
        connection = connect_query_db()
        cursor = connection.cursor()
        cursor.execute(query)
        movies = cursor.fetchall()
        # Join the results into a single string with each row on a new line
        #header_str = f' #. [filmID] Title, Year - Queries\n\n'
        result_str = '\n'.join(f"{row[4]:2}. [{row[0]}] {row[1]}, {row[2]} - {row[3]}" for row in movies)
        # Save the result to a file or process it as needed
        with open('queries_by_movies.txt', 'w') as file:
            file.write(result_str)
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# Getting the most popular queries by category
def queries_by_category():
    query = """
        SELECT 
            category_name, COUNT(category_name) AS cnt_query,
            ROW_NUMBER() OVER (ORDER BY COUNT(category_name) DESC) AS row_by_count
        FROM
            search_queries
        WHERE
            category_name IS NOT NULL AND release_year IS NULL
        GROUP BY category_name
        LIMIT 10;
    """
    try:
        connection = connect_query_db()
        cursor = connection.cursor()
        cursor.execute(query)
        genres = cursor.fetchall()
        # Join the results into a single string with each row on a new line
        result_str = '\n'.join(f"{row[2]:2}.  {row[0]} - {row[1]}" for row in genres)
        # Save the result to a file or process it as needed
        with open('queries_by_category.txt', 'w') as file:
            file.write(result_str)
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# Getting the most popular queries by actors
def queries_by_actors():
    query = """
        SELECT 
            first_name, last_name, COUNT(first_name) AS cnt_query,
            ROW_NUMBER() OVER (ORDER BY COUNT(first_name) DESC) AS row_by_count
        FROM
            search_queries
        WHERE
            first_name IS NOT NULL
        GROUP BY first_name, last_name
        LIMIT 10;
    """
    try:
        connection = connect_query_db()
        cursor = connection.cursor()
        cursor.execute(query)
        genres = cursor.fetchall()
        # Join the results into a single string with each row on a new line
        result_str = '\n'.join(f"{row[3]:2}.  {row[0]} {row[1]} - {row[2]}" for row in genres)
        # Save the result to a file or process it as needed
        with open('queries_by_actors.txt', 'w') as file:
            file.write(result_str)
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# Getting the most popular queries by year of release
def queries_by_year():
    query = """
        SELECT 
            release_year, COUNT(release_year) AS cnt_query,
            ROW_NUMBER() OVER (ORDER BY COUNT(release_year) DESC) AS row_by_count
        FROM
            search_queries
        WHERE
            release_year IS NOT NULL AND category_name IS NULL
        GROUP BY release_year
        LIMIT 10;
    """
    try:
        connection = connect_query_db()
        cursor = connection.cursor()
        cursor.execute(query)
        years = cursor.fetchall()
        # Join the results into a single string with each row on a new line
        result_str = '\n'.join(f"{row[2]:2}.  {row[0]} - {row[1]}" for row in years)
        # Save the result to a file or process it as needed
        with open('queries_by_year.txt', 'w') as file:
            file.write(result_str)
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
