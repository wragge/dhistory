$(function(){
    var offset = 50;
    $('#side-nav li a, a[href^="#"]').click(function(event) {
        event.preventDefault();
        $($(this).attr('href'))[0].scrollIntoView();
        scrollBy(0, -offset);
        $('#side-nav li').removeClass('active');
        $(this).parent().addClass('active');
    });

});




















