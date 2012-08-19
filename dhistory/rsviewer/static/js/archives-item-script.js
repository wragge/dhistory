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
});
