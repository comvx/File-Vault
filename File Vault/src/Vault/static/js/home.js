function next_input(){
    var vault_name = document.getElementById("vault_name");
    var vault_username = document.getElementById("vault_username");
    var vault_password = document.getElementById("vault_password");
    var vault_submit = document.getElementById("vault_submit");
    var vault_next = document.getElementById("vault_next");

    console.log(vault_name.style.display);
    console.log(vault_password.style.display);

    if(vault_name.style.display == "inline" && vault_username.style.display == "none" && vault_password.style.display == "none"){
        vault_name.style.display = "none";
        vault_username.style.display = "inline";
    }else if(vault_name.style.display == "none" && vault_username.style.display == "inline" && vault_password.style.display == "none"){
        vault_next.style.display = "none";
        vault_username.style.display = "none";
        vault_password.style.display = "inline";
        vault_submit.style.display = "inline";
    }
}
function change_bg(vault_name){
    
}

document.addEventListener("DOMContentLoaded", function(event) { 
    var vault_name = document.getElementById("vault_name");
    var vault_username = document.getElementById("vault_username");
    var vault_password = document.getElementById("vault_password");
    var vault_submit = document.getElementById("vault_submit");
    var vault_next = document.getElementById("vault_next");

    vault_name.style.display = "inline";
    vault_username.style.display = "none";
    vault_password.style.display = "none";
    vault_submit.style.display = "none";
});