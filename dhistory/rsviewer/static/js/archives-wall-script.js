$(function () {
    var el, barcode = $("#details").data('barcode');
    var $container = $('#wall');
    $container.imagesLoaded( function(){
        $("#loading-message").remove();
        $container.isotope({
            layoutMode: 'fitRows',
            itemSelector : '.element',
        });
    });
    $container.infinitescroll({
        navSelector  : '#page_nav',    // selector for the paged navigation 
        nextSelector : '#page_nav a',  // selector for the NEXT link (to page 2)
        itemSelector : '.element',     // selector for all items you'll retrieve
        loading : {
			selector: '#wall',
			msgText: 'loading more pages...',
			img: 'http://i.imgur.com/qkKy8.gif',
			finishedMsg: 'no more pages...'
		}
        },
        // call Isotope as a callback
        function( newElements ) {
            $(newElements).imagesLoaded( function(){
                $container.isotope( 'appended', $( newElements ) );
           });
        }
      );
    $(".fancybox")
    .fancybox({
        type: 'image',
        beforeLoad: function() {
            var el, id = $(this.element).data('page-id');
            var el, ref = $("#details").data('reference');
            this.title = "NAA: " + ref + ", page " + id + " &mdash; <a href='/archives/naa/items/" + barcode + "/" + id + "/'>View full size</a>";
        }
    });
    $("#go-to").change(function() {
       window.location = "/archives/naa/items/" + barcode + "/" + $("#go-to").val() + "/";
    });
});
