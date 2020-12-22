document.addEventListener("DOMContentLoaded", function(event) { 

    var card__number = document.getElementById("card__number");
    card__number.readOnly = true;

    var clipboard = new ClipboardJS('.copy');
});
function fix_input_width(){
    var card__number = document.getElementById("card__number");
    card__number.style.width = ((card__number.value.length + 1) * 13) + 'px';
}
function set_to_edit(id){
    var element = document.getElementById(id);
    element.readOnly = false;
}
document.getElementById("close_pop").addEventListener("click", function() {
    close_popup();
});
function show_alert(){
    var element = document.getElementById("alert");
    element.style.display = "block";
}
$(".close").click(function() {
    $(this)
      .parent(".alert")
      .fadeOut();
  });

  function gen_password(){
    var blur = document.getElementById("blur");
    var container = document.getElementById("container");
    blur.style.display = "inline";
    blur.style.visibility = "visible";
    container.style.display = "inline";
    container.style.visibility = "visible";
}