function next_input(){
    var vault_name = document.getElementById("vault_name");
    var vault_username = document.getElementById("vault_username");
    var vault_password = document.getElementById("vault_password");
    var vault_submit = document.getElementById("vault_submit");
    var vault_next = document.getElementById("vault_next");

    console.log(vault_name.style.display);
    console.log(vault_password.style.display);

    if(vault_name.style.display == "inline" && vault_username.style.display == "none" && vault_password.style.display == "none" && vault_name.value != ""){
        vault_name.style.display = "none";
        vault_username.style.display = "inline";
    }else if(vault_name.style.display == "none" && vault_username.style.display == "inline" && vault_password.style.display == "none" && vault_username.value != ""){
        vault_next.style.display = "none";
        vault_username.style.display = "none";
        vault_password.style.display = "inline";
        vault_submit.style.display = "inline";
    }
}
function is_touch_device1() {
    return 'ontouchstart' in window;
  }
 function copyElementToClipboard(element) {
    window.getSelection().removeAllRanges();
    let range = document.createRange();
    range.selectNode(typeof element === 'string' ? document.getElementById(element) : element);
    window.getSelection().addRange(range);
    document.execCommand('copy');
    window.getSelection().removeAllRanges();
  }
  function copied(){
    document.getElementById("share_button").innerHTML = "Url copied to clipboard!";
}
function settings_show(index){
    var panel_settings = document.getElementById(index+"_settings");
    var panel_info = document.getElementById(index+"_info");

    var rename_select = document.getElementById(index+"_rename_select");
    var rename_submit = document.getElementById(index+"_rename_submit");
    var button_delete = document.getElementById(index+"_delete");
    var input_new_folder_name = document.getElementById(index+"_new_folder_name");

    if(panel_settings.style.visibility == "hidden"){
        panel_info.style.visibility = "hidden";
        panel_settings.style.visibility = "visible";

        rename_select.style.visibility = "visible";
        button_delete.style.visibility = "visible";
    }
    else{
        panel_info.style.visibility = "visible";
        panel_settings.style.visibility = "hidden";

        rename_select.style.visibility = "hidden";
        rename_submit.style.visibility = "hidden";
        button_delete.style.visibility = "hidden";
        input_new_folder_name.style.visibility = "hidden";
    }
}
function rename(index){
    var rename_select = document.getElementById(index+"_rename_select");
    var rename_submit = document.getElementById(index+"_rename_submit");
    var button_delete = document.getElementById(index+"_delete");
    var input_new_folder_name = document.getElementById(index+"_new_folder_name");
    
    rename_select.style.visibility = "hidden";
    rename_submit.style.visibility = "visible";
    button_delete.style.visibility = "hidden";
    input_new_folder_name.style.visibility = "visible";
}
function rename_submit(index, href, type){
    var input_new_folder_name = document.getElementById(index+"_new_folder_name");
    var panel_info = document.getElementById(index+"_info");

    window.location.href='/rename?path='+href+'&new_name='+input_new_folder_name.value+'&type='+type;    
}
$(".close").click(function() {
    $(this)
      .parent(".alert")
      .fadeOut();
  });
  $( document ).on( "vclick", function() {
      $("#share_button").innerHTML = "Url copied to clipboard!";
  });

color_array = ["#2977ac", "#0dc94b", "#df3c06", "#fbac45", "#d946db"];
function changeColor(e){
    folder_color_1 = element.getElementById("folder_1");
    folder_color_1 = element.getElementById("folder_2");

    color_index = getIndex(folder_color_1.style.fill);
    console.log(color_index);
}
function getIndex(color){
    for(var i=0;i<color_array.length;i++){
        if(color === color_array[i]){
            return i
        }
    }
}
function show_add_format(){
    var add_form = document.getElementById("add-format");
    if(add_form.style.display == "none"){
        add_form.style.display = "inline";
        setTimeout(hide_add_form, 2000);
    }else{
        add_form.style.display = "none";
    }
}
window.addEventListener('click', function (e){   
    if (document.getElementById('add-format').contains(e.target)){

    } else if(document.getElementById('add-icon').contains(e.target) == false){
      var add_form = document.getElementById("add-format");
      if(add_form.style.display == "inline"){
          console.log("d");
          add_form.style.display = "none";
      }
    }
  });
  
  document.addEventListener("DOMContentLoaded", function(event) { 
    var clipboard = new ClipboardJS('#share_button');
});
function gen_password(){
    document.getElementById("vault_password").value = Math.random().toString(36).slice(Math.random() * (-5 - -11) + -11);
}