$(function () {
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
                            url = "/frontpages/" + newspaper_id + "/" + this.x + "/" + total_type + "/";
                            window.location.href = url;
                        }
                    }
                }
            }
        },
        xAxis: {
            title: {
                enabled: true,
                text: 'Year'
            },
            labels: {
                formatter: function() {
                    return Highcharts.numberFormat(this.value, 0, '', '');
                }
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
});