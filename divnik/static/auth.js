import { base, parseError, parseForm } from "commons";

let endpoint = `${base}/auth/register`;
let formElement = document.getElementById("registration");
if (formElement === null) { formElement = document.getElementById("loginform"); endpoint = `${base}/auth/login` }

const errorMessage = document.getElementById("error-message");
const errorDisplay = document.getElementById("error");
const closeErrorButton = document.getElementById("error-close");

formElement.addEventListener("submit", handleSubmit)
closeErrorButton.addEventListener("click", closeError)

async function handleSubmit(ev) {    
    ev.preventDefault();    
    const data = parseForm(formElement);
    const response = await fetch(endpoint, {
        method: "POST",
        body: data
    })
    if (!response.ok) {
        const error = await parseError(response);
        errorDisplay.className = "";
        errorMessage.innerText = error.desc;
        return false;
    } else {
        window.location.assign(base);
    }
} 

function closeError(ev) {
    errorDisplay.className = "hidden";
}