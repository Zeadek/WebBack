const logInForm = document.querySelector('.logIn')
const signInForm = document.querySelector('.signIn')

const regitrationBtn = document.querySelector('.registration-btn')
const loginBtn = document.querySelector('.login-btn')


regitrationBtn.onclick = () => {
    logInForm.classList.add("active")
    signInForm.classList.add("active")
}

loginBtn.onclick = () => {
    logInForm.classList.remove("active")
    signInForm.classList.remove("active")
}