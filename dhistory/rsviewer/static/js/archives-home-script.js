$(function () {
    $("#get-barcode").click(function(event) {
        event.preventDefault();
        window.location = "/archives/naa/items/" + $("#barcode").val();
    });
});
