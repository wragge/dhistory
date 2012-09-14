/* Author: 

*/
var dataSources = {
	'sources': [],
	'listSeries': function(type) {
			var series = [];
			$.each(this.sources, function(index, source) {
				series.push({'name': source.name, 'data': source.makeSeries(type)});
			});
			return series;
		}
}
function graphData() {
	this.label = '';
	this.query = '';
        this.api_query = '';
	this.data = {};
        this.interval = '';
	this.getYears = function() {
		var years = [];
		$.each(this.data, function(year, value) {
			years.push(year);
		});
		years.sort();
		return years;
	}
	this.makeSeries = function(type) {
		//years = this.getYears();
		var series = [];
		//var self = this;
                if (this.interval == "year") {
                    $.each(this.data, function(year, values) {
                        series.push([Date.UTC(parseInt(year, 10), 0, 1), values[type]]);
                    });
                } else if (this.interval == "month") {
                    $.each(this.data, function(year, values) {
                        $.each(values, function(month, totals) {
                            series.push([Date.UTC(parseInt(year, 10), parseInt(month, 10)-1, 1), totals[type]]);
                        });       
                    });
                }
		//$.each(years, function(index, year) {
		//	series.push([parseInt(year), self.data[year][type]]);
		//});
		return series;
	}
	this.getTotal = function(year, month) {
	    if (month > 0) {
		return this.data[year.toString()][month.toString()]['total'];
            } else {
                return this.data[year.toString()]['total'];
            }
	}
        this.getRatio = function(year, month) {
	    if (month > 0) {
		return this.data[year.toString()][month.toString()]['ratio'];
            } else {
                return this.data[year.toString()]['ratio'];
            }
	}
}
$(function(){
    var api_key = "i5j6aunr9ld4edo"
    var api_url = "http://api.trove.nla.gov.au/result?key=" + api_key
    var start_year = 1900;
    var end_year = 1950;
    var query = "";
    var query_type = 'total';
    function api_request(query) {
        $.jsonp({
            "url": api_url + query + "&n=1&zone=newspaper&encoding=json&callback=?",
            "success": function(results) {
                process_results(results);
            },
            "error": function(d,msg) {
                alert("Error: " + msg);
            }
        });
    
   }
   function process_results(results) {    
        var total = parseInt(results.response.zone.records.total, 10);
        if (query_type == "total") {
            $("#results").html("<p>" + current_year + ": " + total + "</p>");
            current_series.data[current_year] = {};
            current_series.data[current_year]['total'] = total;
            if (total > 0) {
                query_type = "ratio";
                var t_query = "&q=date:[" + current_year + "+TO+" + current_year + "]";
                api_request(t_query);
            } else {
                current_series.data[current_year]['ratio'] = 0;
                current_year++;
                get_year();
            }
        } else if (query_type == "ratio") {
            var ratio = current_series.data[current_year]['total'] / total;
            current_series.data[current_year]['ratio'] = ratio;
            $("#results").append("<p>Ratio: " + ratio + " (" + total + ")</p>");
            query_type = "total";
            current_year++;
            get_year();
        }
        
   }
   function get_year() {
        
        if (current_year <= end_year) {
            var y_query = query + "&l-year=" + current_year;
            setTimeout(api_request(y_query), 200);
        } else {
            dataSources.sources.push(current_series);
            makeChart('ratio');
        }
   }
   function do_query() {
        current_year = start_year;
        keywords = $("#query").val();
        query = "&q=" + encodeURI(keywords);
        current_series = new graphData();
        current_series.name = keywords;
        current_series.api_query = query;
        current_series.interval = "year";
        get_year();
   }
   function serialise_data() {
        series_name = "series" + series_data.length;
        $("#series_data").append("var" + series_name + " = new graphData();");
        $("#series_data").append(series_name + ".name = '" + current_series.name + "';");
        $("#series_data").append("series_data.push(" + series_name + ");");
   }
    var chart;

    function makeChart(type) {
        if (dataSources.sources[0].interval == "month") {
            x_date = "%b %Y";
            xLabel = "Month";
        } else {
            x_date = "%Y";
            xLabel = "Year";
        }
        if (type == "total") {
            yLabel = "Number of articles matching query";
        } else if (type == "ratio") {
            yLabel = "% of articles matching query"
        }
        chart = new Highcharts.Chart({
          chart: {
             renderTo: 'graph',
             type: 'spline',
             zoomType: 'x'
          },
          title: {
              text: 'Australian newspaper articles by date'
           },
           xAxis: {
                    title: {
                            text: xLabel
                    },
                    type: 'datetime',
                    labels: {
                        formatter: function() {
                            return Highcharts.dateFormat(x_date, this.value);
                        }
                    }
           },
           yAxis: {
              title: {
                    text: yLabel
                },
                labels: {
                    formatter: function() {
                        if (type == "ratio") {
                            return Highcharts.numberFormat(this.value * 100, 2, '.', '');
                        } else if (type == 'total') {
                            return this.value;
                        }
                    }
                },
              min: 0
           },
           tooltip: {
              formatter: function() {
                    year = new Date(this.x).getFullYear();
                    if (dataSources.sources[this.series.index].interval == "month") {
                        var interval = "month";
                        month = new Date(this.x).getMonth() + 1;
                        month_name = Highcharts.dateFormat("%b %Y", this.x);
                    } else {
                        var interval = "year;"
                        month = 0;
                    }
                    if (type == "total") {
                        displayValue = this.y + " articles (" + (dataSources.sources[this.series.index].getRatio(year, month) * 100).toPrecision(2) + "% )";
                    } else if (type == "ratio") {
                        displayValue = (this.y * 100).toPrecision(2) + "% (" + dataSources.sources[this.series.index].getTotal(year, month) + " articles)";
                    }
                    if (interval == "month") {
                        return '<b>'+ this.series.name +'</b><br/>'+ month_name + ': ' + displayValue;
                    } else {
                        return '<b>'+ this.series.name + '</b><br/>' + year +': ' + displayValue;
    
                    }
             }
           },
          series: dataSources.listSeries(type),
          plotOptions: {
               series: {
                  cursor: 'pointer',
                  point: {
                     events: {
                        click: function() {
                            date = new Date(this.x);
                            query_date = date.getFullYear();
                            if (dataSources.sources[this.series.index].interval == "month") {
                                month = date.getMonth() + 1;
                                if (month < 10) {
                                    query_date = query_date + "/0" + month;
                                } else {
                                    query_date = query_date + "/" + month;
                                }
                            }
                            showArticles(query_date, this.series);
                        }
                     }
                  }
               }
            }
        });
    }
    function showArticles(query_date, series) {
            $('#articles').empty().height('50px');           
            $('#articles').showLoading();
            $.ajax({
                    dataType: 'jsonp',
                    url: 'http://wraggelabs.appspot.com/api/newspapers/articles/' + query_date + '/?' + encodeURI(dataSources.sources[series.index].api_query),
                    success: function(results) {
                            $('#articles').height('');
                            $('#articles').append('<h3>Articles from Trove</h3>');
                            if (results.results.length > 0) {
                                    var articles = $('<ul id="articles"></ul>');
                                    $.each(results.results, function(key, article) {
                                            articles.append('<li><a class="article" href="'+ article.url + '">&lsquo;' + article.title + '&rsquo;,<br><em>' + article.newspaper_title + '</em>, ' + article.issue_date + '</a></li>');
                                    });
                                    $('#articles').append(articles);
                            } else if (results.error == "An error occurred: ApplicationError: 5 ") {
                                    $('#articles').append('<p>Sorry, Trove took too long to respond. Use the link below to query Trove directly.<p>');
                            }
                            $('#articles').append('<div class="more"><p><a href="' + results.query + '">&gt; View more in Trove</a></p></div>')
                            $('#articles').hideLoading();
                    }
            });
    }
    $('#graph_type').change(function() {
       makeChart($('#graph_type').val()); 
    });
    $("#do_query").button().click(function(){ do_query(); });
});






















