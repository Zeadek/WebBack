package main

import (
	"database/sql"
	"fmt"
	"net/http"
	"net/http/cgi"
	"regexp"
	"strconv"
	"strings"
	"text/template"

	_ "github.com/go-sql-driver/mysql"
)

type FormData struct {
	Fio      string
	Phone    string
	Email    string
	Dob      string
	Gender   string
	Bio      string
	Langs    []string
	Contract bool
}

func validate_data(formData FormData) (bool, string) {
	if formData.Fio == "" {
		return false, "Введите ваше ФИО"
	}
	re := regexp.MustCompile(`^([a-zA-z]+\s){2}[a-zA-z]+$`)
	if !re.MatchString(formData.Fio) || len(formData.Fio) > 150 {
		return false, "Введите ФИО корректно, оно должно содержать только латинские буквы, а длина не должна превышать 150 символов"
	}

	if formData.Email == "" {
		return false, "Введите адрес электронной почты"
	}
	re = regexp.MustCompile(`^[\w\.-_]+@[a-zA-Z]+\.[a-zA-z]+$`)
	if !re.MatchString(formData.Email) {
		return false, "Некоректная запись электронной почты, прим. adress@mail.domen"
	}

	if formData.Phone == "" {
		return false, "Введите ваш номер телефона"
	}
	re = regexp.MustCompile(`^\+\d{11}$`)
	if !re.MatchString(formData.Phone) {
		return false, "Некоректная запись номера телефона, прим. +74957556983"
	}

	if len(formData.Langs) == 0 {
		return false, "Выборите хотя бы 1 язык"
	}

	re = regexp.MustCompile(`^\d{4}(-\d{2}){2}$`)
	if !re.MatchString(formData.Dob) {
		return false, "Введите дату"
	}

	if formData.Bio == "" {
		return false, "Запоните биографию"
	}

	if formData.Contract == false {
		return false, "Подтвердите ознакомление с контрактом"
	}

	return true, fmt.Sprintf("%s, Ваши данные успешно сохранены!", formData.Fio)
}

func addToDataBase(formData FormData, flag int, w http.ResponseWriter) {
	db, err := sql.Open("mysql", "u68875:1698296@/u68875")
	if err != nil {
		fmt.Fprintf(w, "Ошибка подключения: %v", err)
		return
	}
	defer db.Close()

	insert, err := db.Exec(
		"INSERT INTO users (fio, gender, phone, mail, date, bio, contract) VALUES (?, ?, ?, ?, ?, ?, ?)",
		formData.Fio, formData.Gender, formData.Phone, formData.Email, formData.Dob, formData.Bio, flag,
	)
	if err != nil {
		fmt.Fprintf(w, "Ошибка добавления пользователя: %v", err)
		return
	}

	lastInsertID, err := insert.LastInsertId()
	if err != nil {
		fmt.Fprintf(w, "Ошибка получения ID пользователя: %v", err)
		return
	}

	for _, lang_id := range formData.Langs {
		lang, err := strconv.Atoi(lang_id)
		if err != nil {
			fmt.Fprintf(w, "Некорректный id языка: %v", err)
			continue
		}
		_, err = db.Exec("INSERT INTO languages_on_user (user_id, lang_id) VALUES (?, ?)", lastInsertID, lang)
		if err != nil {
			fmt.Fprintf(w, "Ошибка добавления языка: %v", err)
			continue
		}
	}
}

func postHandler(w http.ResponseWriter, r *http.Request) {
	err := r.ParseForm()

	if err != nil {
		fmt.Fprintf(w, "Произошла ошибка: %v", err)
		return
	}

	formData := FormData{
		Fio:      r.FormValue("fio"),
		Phone:    r.FormValue("phone"),
		Email:    r.FormValue("email"),
		Dob:      r.FormValue("date"),
		Gender:   r.FormValue("gender"),
		Bio:      r.FormValue("message"),
		Langs:    r.Form["langs"],
		Contract: r.FormValue("policy") == "on",
	}
	flag := 0
	if formData.Contract {
		flag = 1
	}

	is_valid, val_answer := validate_data(formData)

	funcMap := template.FuncMap{
		"contains": strings.Contains,
	}

	tmpl, err := template.New("index.html").Funcs(funcMap).ParseFiles("index.html")
	if err != nil {
		fmt.Fprintf(w, "Ошибка при работе с шаблоном: %v", err)
		return
	}

	var res []string
	if !is_valid {
		res = append(res, val_answer)
		tmpl.Execute(w, res)
		return
	}

	addToDataBase(formData, flag, w)
	res = append(res, val_answer)
	tmpl.Execute(w, res)
}

func main() {
	cgi.Serve(http.HandlerFunc(postHandler))
}
