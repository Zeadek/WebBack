import html
import mysql.connector
import os

# Константы
MAX_FIO_LENGTH = 150
ALLOWED_LANGUAGES = ["Pascal", "C", "C++", "JavaScript", "PHP", "Python", "Java", "Haskell", "Clojure", "Prolog", "Scala", "Go"]
ALLOWED_GENDERS = ["male", "female", "other"]

DB_HOST = "localhost"
DB_USER = "u68875"
DB_PASSWORD = "1698296"
DB_NAME = "u68875"

def connect_to_db():
    """Устанавливает соединение с базой данных."""
    try:
        db = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return db
    except mysql.connector.Error as err:
        print(f"Ошибка подключения к базе данных: {err}")
        return None

def sanitize_input(data):
    """Очищает ввод."""
    return html.escape(data) if data else None

def validate_data(form):
    """Валидация формы."""
    errors = {}
    fio = form.getvalue("fio", "")
    if not fio:
        errors["fio"] = "ФИО обязательно."
    elif len(fio) > MAX_FIO_LENGTH:
        errors["fio"] = "ФИО слишком длинное."
    elif not all(c.isalpha() or c.isspace() for c in fio):
        errors["fio"] = "ФИО должно содержать только буквы и пробелы."

    phone = form.getvalue("phone", "")
    if phone and not phone.isdigit():
        errors["phone"] = "Телефон должен содержать только цифры."

    email = form.getvalue("email", "")
    if not email or "@" not in email or "." not in email:
        errors["email"] = "Некорректный email."

    gender = form.getvalue("gender", "")
    if gender not in ALLOWED_GENDERS:
        errors["gender"] = "Недопустимый пол."

    languages = form.getlist("languages")
    if not languages or not all(lang in ALLOWED_LANGUAGES for lang in languages):
        errors["languages"] = "Необходимо выбрать языки программирования из списка."

    if form.getvalue("agreement") != "on":
        errors["agreement"] = "Необходимо согласиться."

    bio = form.getvalue("bio", "")
    if len(bio) > 65535:
        errors["bio"] = "Биография слишком длинная."

    return errors

def save_to_db(form):
    """Сохраняет в БД."""
    db = connect_to_db()
    if not db:
        return False, "Ошибка подключения к БД."
    try:
        cursor = db.cursor()
        fio = sanitize_input(form.getvalue("fio"))
        phone = sanitize_input(form.getvalue("phone"))
        email = sanitize_input(form.getvalue("email"))
        birthdate = form.getvalue("birthdate") or None
        gender = form.getvalue("gender")
        bio = sanitize_input(form.getvalue("bio"))
        agreement = 1 if form.getvalue("agreement") == "on" else 0

        insert_user_query = """
        INSERT INTO users (fio, phone, email, birthdate, gender, bio, agreement)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        user_data = (fio, phone, email, birthdate, gender, bio, agreement)
        cursor.execute(insert_user_query, user_data)
        user_id = cursor.lastrowid

        languages = form.getlist("languages")
        insert_language_query = "INSERT INTO user_languages (user_id, language) VALUES (%s, %s)"
        for language in languages:
            cursor.execute(insert_language_query, (user_id, language))

        db.commit()
        cursor.close()
        db.close()
        return True, "Данные успешно сохранены."

    except mysql.connector.Error as err:
        db.rollback()
        return False, f"Ошибка сохранения: {err}"
    finally:
        if db and db.is_connected():
            cursor.close()
            db.close()

def application(environ, start_response):
    """WSGI-приложение."""
    form = cgi.FieldStorage(environ=environ, fp=environ['wsgi.input'])
    errors = validate_data(form)
    result_message = ""

    if environ['REQUEST_METHOD'] == 'POST':
        if errors:
            error_messages = "<br>".join([f"<li>{msg}</li>" for msg in errors.values()])
            result_message = f"<p style='color:red;'>Ошибка:<br><ul>{error_messages}</ul></p>"
        else:
            success, message = save_to_db(form)
            result_message = f"<p style='color:green;'>{message}</p>" if success else f"<p style='color:red;'>{message}</p>"

    with open('index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    html_content = html_content.replace("<div id=\"result\"></div>", f"<div id=\"result\">{result_message}</div>") # Insert the result message
    status = '200 OK'
    headers = [('Content-type', 'text/html; charset=utf-8')]
    start_response(status, headers)
    return [html_content.encode('utf-8')]

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    httpd = make_server('', 8000, application)
    print("Запуск сервера на порту 8000...")
    httpd.serve_forever()
