$(function () {
    function prepare_series(series) {
        var new_series = [];
        $.each(series, function(index, cat) {
           var name = cat['name'];
           var data = [];
           $.each(cat['data'], function(index, values) {
                data.push([Date.UTC(year, month-1, values[0]), values[1]]);
           })
           new_series.push({'name': name, 'data': data});
        });
        return new_series;
    }
    var chart;
    chart = new Highcharts.Chart({
        chart: {
            renderTo: 'container',
            type: 'line',
            zoomType: 'xy'
        },
        title: '',
        legend: {
            enabled: true  
        },
        plotOptions: {
            series: {
                cursor: 'pointer',
                point: {
                    events: {
                        click: function() {
                            url = "/frontpages/" + newspaper_id + "/" + year + "/" + month + "/" + Highcharts.dateFormat("%e", this.x) + "/";
                            window.location.href = url;
                        }
                    }
                }
            }
        },
        xAxis: {
            title: {
                enabled: true,
                text: month_label + " " + year
            },
            type: 'datetime',
            dateTimeLabelFormats: {
                day: '%e %b'   
            }
        },
        yAxis: {
            title: {
                text: y_label
            },
            min: y_min,
            startOnTick: false
        },
        tooltip: {
            formatter: function() {
                return Highcharts.dateFormat("%e %b %Y", this.x) +': '+ Highcharts.numberFormat(this.y, 2);
            },
            useHTML: true
        },
        series: prepare_series(series)
    });
    $("#show").click(function() {
        newspaper_id = $("#newspaper").val();
        url = "/frontpages/" + newspaper_id + "/words/";
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
});