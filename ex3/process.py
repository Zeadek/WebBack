import cgi
import cgitb
import mysql.connector
import html
import datetime

cgitb.enable()

DB_HOST = "localhost"
DB_USER = "u68875"
DB_PASSWORD = "1698296"
DB_NAME = "u68875"

form = cgi.FieldStorage()

def clean_data(data):
    if data is None:
        return None
    data = data.strip()
    data = html.escape(data)
    return data

errors = []
full_name = form.getfirst("full_name", "")
full_name = clean_data(full_name)
if not full_name:
    errors.append("ФИО обязательно для заполнения.")
elif not full_name.replace(" ", "").isalpha(): # Убираем пробелы и проверяем, что остались только буквы
    errors.append("ФИО может содержать только буквы и пробелы.")

phone = form.getfirst("phone", "")
phone = clean_data(phone)
if phone and not phone.replace("+", "").replace("-", "").replace(" ", "").isdigit():
    errors.append("Некорректный формат телефона.")

email = form.getfirst("email", "")
email = clean_data(email)
if not email:
    errors.append("E-mail обязателен для заполнения.")
elif "@" not in email or "." not in email:
    errors.append("Некорректный формат e-mail.")

birthdate_str = form.getfirst("birthdate", "")
birthdate = None
if birthdate_str:
    birthdate_str = clean_data(birthdate_str)
    try:
        birthdate = datetime.datetime.strptime(birthdate_str, "%Y-%m-%d").date() # Преобразуем строку в дату
    except ValueError:
        errors.append("Некорректный формат даты рождения.")

gender = form.getfirst("gender", "")
gender = clean_data(gender)
allowed_genders = ["male", "female", "other"]
if not gender:
    errors.append("Пол обязателен для выбора.")
elif gender not in allowed_genders:
    errors.append("Недопустимое значение для поля Пол.")

languages = form.getlist("languages")
if not languages:
    errors.append("Необходимо выбрать хотя бы один язык программирования.")
else:
    allowed_languages = ["Pascal", "C", "C++", "JavaScript", "PHP", "Python", "Java", "Haskell", "Clojure", "Prolog", "Scala", "Go"]
    for language in languages:
        language = clean_data(language)
        if language not in allowed_languages:
            errors.append(f"Недопустимый язык программирования: {language}")

bio = form.getfirst("bio", "")
bio = clean_data(bio)

contract = form.getfirst("contract", "")
contract_signed = (contract == "1")

print("Content-Type: text/html; charset=utf-8")
print()
print("<!DOCTYPE html>")
print("<html><head><title>Результат</title></head><body>")

if errors:
    print("<h1>Ошибки:</h1>")
    for error in errors:
        print(f"<p>{error}</p>")
else:
    try:
        mydb = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )

        mycursor = mydb.cursor()

        sql_users = """
            INSERT INTO users (full_name, phone, email, birthdate, gender, bio, contract_signed)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values_users = (full_name, phone, email, birthdate, gender, bio, contract_signed)
        mycursor.execute(sql_users, values_users)
        mydb.commit()
        user_id = mycursor.lastrowid
        sql_languages = "INSERT INTO user_languages (user_id, language) VALUES (%s, %s)"
        for language in languages:
            values_languages = (user_id, language)
            mycursor.execute(sql_languages, values_languages)
            mydb.commit()

        print("<h1>Данные успешно сохранены!</h1>")

    except mysql.connector.Error as err:
        print(f"<h1>Ошибка при записи в базу данных:</h1>