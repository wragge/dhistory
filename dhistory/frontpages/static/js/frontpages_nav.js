$(function () {
    var months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
    function load_newspapers() {
        $('form').showLoading();
        url = "/frontpages/autocomplete/";
        $.getJSON(url, function(data) {
            $("#newspaper").empty();
            $("#newspaper").append('<option value="">Newspaper</option>');
            $.each(data, function(index, newspaper) {
                $("#newspaper").append('<option value="' + newspaper[0] + '">' + newspaper[1] + '</option>')
            });
            $('form').hideLoading();
        });
    }
    function clear_years() {
        $("#year").empty();
        $("#year").append('<option value="0">Year</option>'); 
    }
    function clear_months() {
        $("#month").empty();
        $("#month").append('<option value="0">Month</option>'); 
    }
    function clear_days() {
        $("#day").empty();
        $("#day").append('<option value="0">Day</option>');
    }
    $("#show").click(function() {
        newspaper_id = $("#newspaper").val();
        year = $("#year").val();
        month = $("#month").val();
        day = $("#day").val();
        view = $("#view").val();
        url = "/frontpages/" + newspaper_id + "/";
        if (year > 0) { url += year + "/";}
        if (year > 0 && month > 0) { url += month + "/";}
        if (year > 0 && month > 0 && day > 0) { url += day + "/";}
        if (day == 0 && view) { url += view + "/";}
        categories = []
        $('input:checkbox:checked').each(function() {
            categories.push($(this).val());
        })
        if (categories.length > 0) {
            url += "?category=" + categories.join('&category=')
        }
        window.location.href = url;
        return false;
    });
    $("#newspaper").change(function() {
        $('form').showLoading();
        newspaper_id = $("#newspaper").val();
        url = "/frontpages/autocomplete/" + newspaper_id + "/";
        $.getJSON(url, function(data) {
            $("#year").empty();
            $("#year").append('<option value="0">Year</option>');
            $.each(data, function(index, year) {
                $("#year").append('<option value="' + year + '">' + year + '</option>')
            });
            clear_months();
            clear_days();
            $('form').hideLoading();
        });
    });
    $("#year").change(function() {
        $('form').showLoading();
        newspaper_id = $("#newspaper").val();
        year = $("#year").val();
        if (newspaper_id && year) {
            url = "/frontpages/autocomplete/" + newspaper_id + "/" + year + "/";
            $.getJSON(url, function(data) {
                $("#month").empty();
                $("#month").append('<option value="0">Month</option>');
                $.each(data, function(index, month) {
                    $("#month").append('<option value="' + month + '">' + months[month-1] + '</option>')
                });
                clear_days();
                $('form').hideLoading();
            });
        } else {
            $('form').hideLoading();
        }
    });
    $("#month").change(function() {
        $('form').showLoading();
        newspaper_id = $("#newspaper").val();
        year = $("#year").val();
        month = $("#month").val();
        if (newspaper_id && year && month) {
            url = "/frontpages/autocomplete/" + newspaper_id + "/" + year + "/" + month + "/";
            $.getJSON(url, function(data) {
                $("#day").empty();
                $("#day").append('<option value="0">Day</option>');
                $.each(data, function(index, day) {
                    $("#day").append('<option value="' + day + '">' + day + '</option>')
                });
                $('form').hideLoading();
            });
        } else {
            $('form').hideLoading();
        }
    });
    load_newspapers();
});