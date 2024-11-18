window.addEventListener("DOMContentLoaded", ()=>{
    const input_search = document.getElementById("buscar")
    input_search.addEventListener("submit", (e)=>{
        e.preventDefault()
        const search = document.getElementById("search")
        window.location.href = `/buscar?q=${search.value}`
    })
})