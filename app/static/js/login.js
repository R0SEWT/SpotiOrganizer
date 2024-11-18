const urlParams = new URLSearchParams(window.location.search);
let code = urlParams.get('code');

if(code){
    document.getElementById("loadder").classList.remove("hidden")
    document.getElementById("loginSpotify").classList.add("hidden")
    const codeVerifier = localStorage.getItem("code_verifier");

    fetch("/logining", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            code,
            codeVerifier
        })
    })
    .then(res => res.json())
    .then(data => { 
        console.log(data)
        if(data.status) location.href = "/"
    })
}
window.addEventListener("DOMContentLoaded", async ()=>{
    const btnLogin = document.getElementById("loginSpotify");
    
    let codeVerifier = null
    if(!localStorage.getItem("code_verifier")) {
        codeVerifier  = generateRandomString(64);
        localStorage.setItem('code_verifier', codeVerifier);
    }
    else codeVerifier = localStorage.getItem("code_verifier");

    const hashed = await sha256(codeVerifier)
    const codeChallenge = base64encode(hashed);
    
    const params_adicionales = `redirect_uri=${REDIRECR_URI}&code_challenge_method=S256&code_challenge=${codeChallenge}`

    btnLogin.addEventListener("click", async ()=>{
        const req = await fetch("/login-spotify")
        const res = await req.json()
        location.href = `${res.url}&${params_adicionales}`;
    })
})