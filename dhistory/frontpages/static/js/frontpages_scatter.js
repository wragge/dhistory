$(function () {
    var chart;
    $(document).ready(function() {
        chart = new Highcharts.Chart({
            chart: {
                renderTo: 'container',
                type: 'scatter',
                zoomType: 'xy'
            },
            title: {
                text: 'Front pages'
            },
            legend: {
                enabled: false  
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
                    text: 'Average number of words in front page articles'
                },
                min: -200,
                startOnTick: false
            },
            tooltip: {
                formatter: function() {
                        return newspapers[this.point.options.n] + '<br> ' + this.x +': '+ Highcharts.numberFormat(this.y, 2);
                },
                useHTML: true
            },
            plotOptions: {
                scatter: {
                    marker: {
                        radius: 5,
                        states: {
                            hover: {
                                enabled: true,
                                lineColor: 'rgb(100,100,100)'
                            }
                        }
                    },
                    states: {
                        hover: {
                            marker: {
                                enabled: false
                            }
                        }
                    }
                }
            },
            series: [{
                name: 'Female',
                point: {
                    events: {
                        click: function() {
                            alert(newspapers[this.options.n]);
                        }
                    }
                },
                turboThreshold: 50000,
                color: 'rgba(223, 83, 83, .5)',
                data: data
    
            }]
        });
    });
    
});