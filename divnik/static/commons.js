export const base = `http://${document.location.host}`;
export async function parseError(response) {
    if (!(response.headers.get("Content-Type") !== "application/x-www-urlencoded")) throw Error("Invalid content type");
    const text = await response.text();
    const error = new URLSearchParams(text); 
    return {code: error.get("code"), desc: error.get("desc")}
};
export function parseForm(form) {
    const inputs = form.elements;
    const result = new URLSearchParams();
    for (let i = 0; i < inputs.length; ++i) {
        result.append(inputs[i].name, inputs[i].value);
    }
    return result;
}