import csv
import sqlite3


def import_csv_to_sql(table_name: str,
                      table_path: str,
                      csv_path: str):
    connection = sqlite3.connect(table_path)
    cursor = connection.cursor()
    with open(csv_path, 'r', encoding='utf-8') as file:

        csv_headers = csv.DictReader(file)
        csv_headers = csv_headers.fieldnames
        sql_headers = ', '.join(csv_headers)
        sql_values = ['?' for i in range(len(csv_headers))]
        sql_values = ', '.join(sql_values)
        insert_records = (f"INSERT INTO {table_name}"
                          f"({sql_headers}) VALUES({sql_values})")

        contents = csv.reader(file)
        try:
            cursor.executemany(insert_records, contents)
        except Exception as e:
            print(e)
        select_all = f"SELECT * FROM {table_name}"
        rows = cursor.execute(select_all).fetchall()
        for r in rows:
            print(r)
        connection.commit()
        connection.close()


if __name__ == '__main__':

    # Users
    import_csv_to_sql(
        table_name='reviews_user',
        table_path='db.sqlite3',
        csv_path='static/data/users.csv',
    )

    # Category
    import_csv_to_sql(
        table_name='reviews_category',
        table_path='db.sqlite3',
        csv_path='static/data/category.csv',
    )

    # Genre
    import_csv_to_sql(
        table_name='reviews_genre',
        table_path='db.sqlite3',
        csv_path='static/data/genre.csv',
    )

    # Title
    import_csv_to_sql(
        table_name='reviews_title',
        table_path='db.sqlite3',
        csv_path='static/data/titles.csv',
    )

    # Review
    import_csv_to_sql(
        table_name='reviews_review',
        table_path='db.sqlite3',
        csv_path='static/data/review.csv',
    )

    # Comment
    import_csv_to_sql(
        table_name='reviews_comment',
        table_path='db.sqlite3',
        csv_path='static/data/comments.csv',
    )

    # ManyToMany - Title + Genre
    import_csv_to_sql(
        table_name='reviews_title_genre',
        table_path='db.sqlite3',
        csv_path='static/data/genre_title.csv',
    )
