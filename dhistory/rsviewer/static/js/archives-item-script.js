$(function () {
    var el, barcode = $("#details").data('barcode');
    var el, page = $("#details").data('page');
    $("#go-to").val(page);
    $("#go-to").change(function() {
       window.location = "/archives/naa/items/" + barcode + "/" + $("#go-to").val() + "/";
    });
    $("#print").click(function(event) {
        event.preventDefault();
        window.location = "/archives/naa/items/" + barcode + "/print/?pages=" + $("#print-range").val();
    });
    $("#zoom").click(function(event) {
        event.preventDefault();
        var zoom = $("#zoom").text();
        if (zoom == " Enlarge") {
            $("#page-image").attr("src", "/archives/naa/images/" + barcode + "/" + page + "/large/");
            $("#zoom").html('<i class="icon-zoom-out"></i> Reduce');
        } else if (zoom == " Reduce") {
            $("#page-image").attr("src", "/archives/naa/images/" + barcode + "/" + page + "/");
            $("#zoom").html('<i class="icon-zoom-in"></i> Enlarge');
        }
    });
});
