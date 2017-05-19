'use strict'

$(function(){
  //当滚动条的位置处于距顶部100像素以下时，跳转链接出现，否则消失
  $(window).scroll(function(){
    if ($(window).scrollTop()>100){
      $("#go_top").fadeIn(120);
    } else {
      $("#go_top").fadeOut(120);
    }
  });
  $("#go_top").click(function(){
    $('body,html').animate({ scrollTop: 0 }, 140);
    return false;
  });
})
