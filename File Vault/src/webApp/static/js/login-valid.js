  $('input[type="text"],input[type="password"]').focus(function(){
    $(this).prev().animate({'opacity':'1'},200)
  });
  $('input[type="text"],input[type="password"]').blur(function(){
    $(this).prev().animate({'opacity':'.5'},200)
  });
  
  $('input[type="text"],input[type="password"]').keyup(function(){
    if(!$(this).val() == ''){
      $(this).next().animate({'opacity':'1','right' : '30'},200)
    } else {
      $(this).next().animate({'opacity':'0','right' : '20'},200)
    }
  });
  
  var open = 0;
  $('.tab').click(function(){
    $(this).fadeOut(200,function(){validation
      $(this).parent().animate({'left':'0'})
    });
  });
  
  