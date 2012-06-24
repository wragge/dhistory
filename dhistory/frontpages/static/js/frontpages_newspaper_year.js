$(function () {
    var chart;
    alert(year);
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
                            url = "/frontpages/" + newspaper_id + "/" + year + "/" + (this.x + 1) + "/" + total_type + "/";
                            window.location.href = url;
                        }
                    }
                }
            }
        },
        xAxis: {
            categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            title: {
                enabled: true,
                text: month_label + " " + year
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
                return this.x +': '+ Highcharts.numberFormat(this.y, 2);
            },
            useHTML: true
        },
        series: series
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