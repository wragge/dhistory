$(function () {
    function load_newspapers() {
        url = "/frontpages/autocomplete/";
        $.getJSON(url, function(data) {
            $("#newspaper").empty();
            $("#newspaper").append('<option value="">Choose a newspaper</option>');
            $.each(data, function(index, newspaper) {
                $("#newspaper").append('<option value="' + newspaper[0] + '">' + newspaper[1] + '</option>')
            });
        });
    }
    $("#show").click(function() {
        newspaper_id = $("#newspaper").val();
        url = "/frontpages/" + newspaper_id + "/words/";
        window.location.href = url;
        return false;
    });
    $("#show_scatter").click(function() {
        category = $("#category").val();
        url = "/frontpages/all/" + category + "/words/";
        window.location.href = url;
        return false;
    });
    load_newspapers();
});