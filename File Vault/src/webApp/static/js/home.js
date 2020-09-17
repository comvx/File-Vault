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
document.addEventListener("DOMContentLoaded", function(event) { 
    var vault_name = document.getElementById("vault_name");
    var vault_username = document.getElementById("vault_username");
    var vault_password = document.getElementById("vault_password");
    var vault_submit = document.getElementById("vault_submit");
    var vault_next = document.getElementById("vault_next");
    try {
        vault_name.style.display = "inline";
        vault_username.style.display = "none";
        vault_password.style.display = "none";
        vault_submit.style.display = "none";
     }
     catch (e) {
     }
     var clipboard = new ClipboardJS('.click_share_url');
});
function settings_show(index){
    var panel_settings = document.getElementById(index+"_settings");
    var panel_info = document.getElementById(index+"_info");

    if(panel_settings.style.visibility == "hidden"){
        panel_info.style.visibility = "hidden";
        panel_settings.style.visibility = "visible";
    }
    else{
        panel_info.style.visibility = "visible";
        panel_settings.style.visibility = "hidden";
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
function copied(){
    document.getElementById("share_button").innerHTML = "Url copied to clipboard!";
}

$(".close").click(function() {
    $(this)
      .parent(".alert")
      .fadeOut();
  });
  $( document ).on( "vclick", function() {
      $("#share_button").innerHTML = "Url copied to clipboard!";
  });