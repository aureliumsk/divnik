import { base } from "commons";

const container = document.getElementById("wrapper");
container.addEventListener("click", (ev) => {
    const button = ev.target;
    if (button.className !== "append") return;
    const article = button.parentNode;
    button.hidden = true;
    const element = document.createElement("article");
    element.className = "homework";
    const inputDate = document.createElement("input");
    const inputDesc = document.createElement("input");
    inputDate.type = "date";
    const today = new Date();
    inputDate.min = `${today.getFullYear()}-${today.getMonth() + 1}-${today.getDate()}`;
    inputDesc.addEventListener("keyup", async (e) => {
        if (e.key !== "Enter") return;
        const date = inputDate.value;
        const desc = inputDesc.value;
        if (date === "" || desc === "") return;
        const form = new URLSearchParams({ date, desc, lesson_id: article.dataset.lessonId });
        const res = await fetch(`${base}/create`, {
            method: "POST",
            body: form
        });
        if (!res.ok) console.error("Bad response from server.");
        else {
            const html = await res.text();
            article.outerHTML = html;
        }
    });
    element.append(inputDate, inputDesc);
    article.append(element);
});

container.addEventListener("click", async (ev) => {
    const button = ev.target;
    if (button.className !== "delete") return;
    const homework = button.parentNode.parentNode;
    const article = homework.parentNode;
    const homeworkId = homework.dataset.homeworkId;
    const res = await fetch(`${base}/delete/${homeworkId}`, {
        method: "POST"
    });
    if (!res.ok) console.error("Bad response from server.");
    else {
        const html = await res.text();
        article.outerHTML = html;
    }
});

container.addEventListener("click", (ev) => {
    let button = ev.target;
    if (button.className !== "edit") {
        // a bit hacky, but it's better than checking every single child
        if (button.tagName === "IMG") button = button.parentNode;
        else return;
    }
    const homework = button.parentNode.parentNode;
    const article = homework.parentNode;
    const homeworkId = homework.dataset.homeworkId;
    let date = "";
    let desc = "";
    while (homework.firstChild) {
        const child = homework.lastChild
        if (child.tagName === "P") {
            desc = child.textContent;
        } else if (child.tagName === "H2") {
            date = child.dataset.isoformat;
        }
        homework.removeChild(child);
    }; 
    const inputDate = document.createElement("input");
    const today = new Date();
    inputDate.type = "date";
    inputDate.value = date;
    inputDate.min = `${today.getFullYear()}-${today.getMonth() + 1}-${today.getDate()}`;
    const inputDesc = document.createElement("input");
    inputDesc.value = desc;
    inputDesc.addEventListener("keyup", async (e) => {
        if (e.key !== "Enter") return;
        const date = inputDate.value;
        const desc = inputDesc.value;
        if (date === "" || desc === "") return;
        const form = new URLSearchParams({ date, desc })
        const res = await fetch(`${base}/update/${homeworkId}`, {
            method: "POST",
            body: form
        });
        if (!res.ok) console.error("Bad response from server.");
        else {
            const html = await res.text();
            article.outerHTML = html;
        }
    });
    homework.append(inputDate, inputDesc);
})