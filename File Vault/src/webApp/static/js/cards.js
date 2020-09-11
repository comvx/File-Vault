document.addEventListener("DOMContentLoaded", function(event) { 

    var card__number = document.getElementById("card__number");
    card__number.readOnly = true;
});
function fix_input_width(){
    var card__number = document.getElementById("card__number");
    card__number.style.width = ((card__number.value.length + 1) * 13) + 'px';
}
function copyToClipboard(id) {
    console.log("d");
    var text = document.getElementById(id).value;
    console.log(text);
    var dummy = document.createElement("textarea");
    document.body.appendChild(dummy);
    dummy.value = text;
    dummy.select();
    document.execCommand("copy");
    document.body.removeChild(dummy);
}
function set_to_edit(id){
    var element = document.getElementById(id);
    element.readOnly = false;
}
document.getElementById("close_pop").addEventListener("click", function() {
    close_popup();
});
function close_popup(){
    var popup = document.getElementById("cd-popup");
    popup.style.visibility = "hidden";
    popup.style.opacity = 0;
}
function show_popup(){
    var popup = document.getElementById("cd-popup");
    popup.style.visibility = "visible";
    popup.style.opacity = 1;
}