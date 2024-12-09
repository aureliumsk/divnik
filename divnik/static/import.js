import { base } from "commons";

const formElement = document.getElementById("fileimport");
const fileInput = document.getElementById("file");

formElement.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    const formData = new FormData(formElement);
    const response = await fetch(`${base}/import`, {
        method: "POST",
        body: formData
    })
    const textData = await response.text();
    if (!response.ok) {
        if (!(response.headers.get("Content-Type") === "application/x-www-form-urlencoded")) throw Error("Invalid content type");
        const error = new URLSearchParams(textData);
        if (error.get("code") !== "400") throw Error(`unknown error: "${error.get("desc")}" (${error.get("code")})`);
        fileInput.setCustomValidity(error.get("desc"));
        formElement.reportValidity();
    } else {
        window.location = base;
    }
});