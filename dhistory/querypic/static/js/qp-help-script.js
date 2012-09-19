$(function(){
    var offset = 80;

    $('#side-nav li a').click(function(event) {
        event.preventDefault();
        $($(this).attr('href'))[0].scrollIntoView();
        scrollBy(0, -offset);
    });
});




















