$(document).ready(function() {      
    $('.dc-menu-trigger').click(function(){
       $('nav').toggleClass( "dc-menu-open" );
       $('.menu-overlay').toggleClass( "open" );
       $('header').toggleClass( "shownav" );
    }); 
 });
$(window).on('load', function() {
   $('.toast').toast({delay: (30000)});
   $('.toast').toast('show');
})
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
function show_add_row(){
   document.getElementById("add_row").style.visibility = "visible";
}
var Password = {
 
   _pattern : /[a-zA-Z0-9_\-\+\.\!]/,
   
   
   _getRandomByte : function()
   {
     // http://caniuse.com/#feat=getrandomvalues
     if(window.crypto && window.crypto.getRandomValues) 
     {
       var result = new Uint8Array(1);
       window.crypto.getRandomValues(result);
       return result[0];
     }
     else if(window.msCrypto && window.msCrypto.getRandomValues) 
     {
       var result = new Uint8Array(1);
       window.msCrypto.getRandomValues(result);
       return result[0];
     }
     else
     {
       return Math.floor(Math.random() * 256);
     }
   },
   
   generate : function(length)
   {
     return Array.apply(null, {'length': length})
       .map(function()
       {
         var result;
         while(true) 
         {
           result = String.fromCharCode(this._getRandomByte());
           if(this._pattern.test(result))
           {
             return result;
           }
         }        
       }, this)
       .join('');  
   }    
     
 };