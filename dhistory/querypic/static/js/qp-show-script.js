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
};
function graphData() {
	this.name = '';
	this.query = '';
        this.api_query = '';
        this.web_query = '';
	this.data = {};
        this.interval = '';
        this.country = '';
        this.accuracy = '';
	this.getYears = function() {
		var years = [];
		$.each(this.data, function(year, value) {
			years.push(year);
		});
		years.sort();
		return years;
	};
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
	};
	this.getTotal = function(year, month) {
        if (month > 0) {
		return this.data[year.toString()][month.toString()]['total'];
            } else {
                return this.data[year.toString()]['total'];
            }
	};
    this.getRatio = function(year, month) {
        if (month > 0) {
            return this.data[year.toString()][month.toString()]['ratio'];
        } else {
            return this.data[year.toString()]['ratio'];
        }
	};
}

$(function(){
    var digitalnz_api_key = "9yXNTynMDb3TUQws7QuD";
    var digitalnz_api_url = "http://api.digitalnz.org/records/v2.json?";
    var digitalnz_html_url = "http://digitalnz.org.nz/records?i[display_collection]=Papers+Past";
    var trove_api_key = "6pi5hht0d2umqcro";
    var trove_api_url = "http://api.trove.nla.gov.au/result?zone=newspaper";
    var trove_html_url = "http://trove.nla.gov.au/newspaper/result?q=";
    var twitter_url ="http://platform.twitter.com/widgets/tweet_button.html";
    var query_type = 'ratio';

   function make_link() {
        var params = [];
        $.each(dataSources.sources, function(key, source) {
            params.push(source.query + "|" + source.country + "|" + source.accuracy);
        });
        var link = "http://wraggelabs.com/shed/querypic/?q=" + params.join("&q=");
        return link;
   }
    var chart;

    function makeChart(type) {
        $("#graph").show();
        $("#status").empty();
        $("#intro-hints").hide();
        $("#graph-notes").show();
        $("#intro-notes").hide();
        $("#graph-hints").show();
        $("#trove-results").show();
        $("#type_selector").show();
        $('#graph_type').val(type);
        $("#query").val("");
        //var link = make_link();
        //$("#link").html("Share this: <a href='" + link + "'>" + link + "</a>");
        //$("#twitter-frame").attr('src', twitter_url + "?url=" + encodeURIComponent(link) + "&text=" + encodeURIComponent("Made with QueryPic") + "&hashtags=querypic");
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
            yLabel = "% of articles matching query";
        }
        chart = new Highcharts.Chart({
          chart: {
             renderTo: 'graph',
             type: 'spline',
             zoomType: 'x'
          },
          title: {
              text: 'Newspaper articles by date'
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
                    var interval;
                    if (dataSources.sources[this.series.index].interval == "month") {
                        interval = "month";
                        month = new Date(this.x).getMonth() + 1;
                        month_name = Highcharts.dateFormat("%b %Y", this.x);
                    } else {
                        interval = "year";
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
            var this_query = dataSources.sources[series.index].api_query;
            var callback;
            if (dataSources.sources[series.index].country == "aus") {
                this_query = this_query + "&l-year=" + query_date;
                callback = "callback";
            } else if (dataSources.sources[series.index].country == "nz") {
                this_query = this_query + "+year:" + query_date;
                callback = "jsonp";
            }
            $.ajax({
                    "dataType": "jsonp",
                    "jsonp": callback,
                    "url": this_query,
                    "success": function(results) {
                            $('#articles').height('');
                            $('#articles').append('<h3>Articles</h3>');
                            if (dataSources.sources[series.index].country == "aus") {
                                show_trove_articles(results, query_date, series);
                            } else if (dataSources.sources[series.index].country == "nz") {
                                show_digitalnz_articles(results, query_date, series);
                            }
                            $('#articles').hideLoading();
                    }
            });
    }
    function show_trove_articles(results, query_date, series) {
        if (results.response.zone[0].records.article.length > 0) {
            var articles = $('<ul id="articles"></ul>');
            $.each(results.response.zone[0].records.article, function(key, article) {
                newspaper = article.title.value.match(/(.*?) \(/)[1];
                date = $.format.date(article.date + ' 00:00:00.000', 'd MMMM yyyy');
                articles.append('<li><a target="_blank" class="article" href="'+ article.troveUrl + '">' + article.heading + ' (' + newspaper + ', ' + date + ')</a></li>');
            });
            $('#articles').append(articles);
        }
        $('#articles').append('<div class="more"><p><a target="_blank" href="' + dataSources.sources[series.index].web_query + '&fromyyyy=' + query_date + '&toyyyy=' + query_date + '">&gt; View more in Trove</a></p></div>');

    }
    function show_digitalnz_articles(results, query_date, series) {
        if (results.results.length > 0) {
            var articles = $('<ul id="articles"></ul>');
            $.each(results.results, function(key, article) {
                    articles.append('<li><a target="_blank" class="article" href="'+ article.display_url + '">' + article.title + '</a></li>');
            });
            $('#articles').append(articles);
        }
        $('#articles').append('<div class="more"><p><a target="_blank" href="' + dataSources.sources[series.index].web_query + '&i[year]=%5B' + query_date + '+TO+' + query_date + '%5D&">&gt; View more at DigitalNZ</a></p></div>');
    }
    $('#graph_type').change(function() {
       makeChart($('#graph_type').val());
    });
    function prepareData() {
        $.each(sources["sources"], function(key, source) {
            new_source = new graphData();
            new_source['data'] = source['data'];
            new_source['name'] = source['name'];
            new_source['query'] = source['query'];
            new_source['api_query'] = source['api_query'];
            new_source['web_query'] = source['web_query'];
            new_source['interval'] = source['interval'];
            new_source['country'] = source['country'];
            new_source['accuracy'] = source['accuracy'];
            dataSources["sources"].push(new_source);
        });
    }
    function showSeriesDetails() {
        $.each(dataSources.sources, function(key, source) {
            var $group = $('<div class="accordion-group"></div>');
            var $header = $('<div class="accordion-heading"><a class="accordion-toggle" data-toggle="collapse" data-parent="#series-details" href="#series' + key + '">Query ' + (key+1) + '</a></div>');
            var $body = $('<div id="series' + key + '" class="accordion-body collapse"></div>');
            var $inner = $('<div class="accordion-inner"></div>');
            $inner.append('<p><small>' + source.name + '</small></p>');
            var $show_trove = $('<a href="' + source.query + '" class="btn btn-mini btn-primary">Show in Trove</a>');
            $inner.append($show_trove);
            if (source.country == "Aus") {
                var $new_qp = $('<br><a href="/querypic/create/?trove_query=' + encodeURIComponent(source.query) + '" class="btn btn-mini btn-primary">Use in new QP</a>');
                $inner.append($new_qp);
            }
            $body.append($inner);
            $group.append($header).append($body);
            $("#series-details").append($group);
        });
    }
    prepareData();
    showSeriesDetails();
    makeChart("ratio");
});




















