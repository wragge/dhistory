/* Author:

*/
var dataSources = {
	'sources': [],
    'zones': {
            'book': 'Books',
            'picture': 'Pictures, photos and objects',
            'article': 'Journals, articles and datasets',
            'music': 'Music, sound and video',
            'map': 'Maps',
            'collection': 'Diaries, letters and archives'
        },
	'listSeries': function(type) {
			var series = [];
            var source = this.sources[0];
			$.each(this.zones, function(zone, label) {
				series.push({'name': label, 'data': source.makeSeries(zone)});
			});
			return series;
		},
    'getZone': function(label) {
        var this_zone = '';
        $.each(this.zones, function(zone, zone_label) {
            if (zone_label == label) {
                this_zone = zone;
            }
        });
        return this_zone;
    }

};
function graphData() {
	this.name = '';
	this.query = '';
    this.api_query = '';
    this.web_query = '';
    this.data = {};
    this.data.book = {};
    this.data.picture = {};
    this.data.article = {};
    this.data.music = {};
    this.data.map = {};
    this.data.collection = {};
    this.interval = 'year';
    this.country = '';
    this.dates = [];
    this.limits = {};
	this.getYears = function(zone) {
		var years = [];
		$.each(this.data[zone], function(year, value) {
			years.push(parseInt(year, 10));
		});
		years.sort();
		return years;
	};
	this.makeSeries = function(zone) {
		var years = this.getYears(zone);
		var series = [];
		var self = this;
                if (this.interval == "year") {
                    //$.each(this.data, function(year, values) {
                        //series.push([Date.UTC(parseInt(year, 10), 0, 1), values[type]]);
                    $.each(years, function(index, year) {
                        series.push([Date.UTC(year, 0, 1), self.data[zone][year]]);

                    });
                } else if (this.interval == "month") {
                    $.each(this.data, function(year, values) {
                        $.each(values, function(month, totals) {
                            series.push([Date.UTC(parseInt(year, 10), parseInt(month, 10)-1, 1), totals[type]]);
                        });
                    });
                }
        console.log(series);
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
    reset();
    var digitalnz_api_key = "9yXNTynMDb3TUQws7QuD";
    var digitalnz_api_url = "http://api.digitalnz.org/v3/records.json?api_key=" + digitalnz_api_key + "&and[display_collection][]=Papers+Past";
    var digitalnz_html_url = "http://digitalnz.org.nz/records?i[display_collection]=Papers+Past";
    var trove_api_key = "6pi5hht0d2umqcro";
    var trove_api_url = "http://api.trove.nla.gov.au/result?";
    var trove_html_url = "http://trove.nla.gov.au/book/result?l-format=Thesis&l-australian=y&q=";
    var trove_api_title_url = "http://api.trove.nla.gov.au/newspaper/title/";
    var trove_html_title_url = "http://trove.nla.gov.au/ndp/del/title/";
    var twitter_url ="http://platform.twitter.com/widgets/tweet_button.html";
    var word_categories = {0: "< 100", 1: "100&ndash;1000", 3: "> 1000"};
    var query = '';
    var decade_start;
    var decade_end;
    var year_start;
    var year_end;
    var interval = "year";
    var decade_current = decade_start;
    var year_current = year_start;
    var queries = [];
    var query_type = 'ratio';
    var current_series;

    function reset_query() {
        query = '';
        interval = "year";
        queries = [];
        query_type = 'ratio';
    }

    function get_query() {
        $('#panes a:last').tab('show');
        var qstring;
        if ($("#query").val() !== "") {
            var keywords = $("#query").val();
            if (keywords.match(/^[a-zA-Z\d"\(\)\~\:\- ]+$/)) {
                if (keywords.match(/(AND|OR|NOT|\(|"|\-|\*)/)) {
                //if (keywords.indexOf('"') == -1) {
                    qstring = keywords;
                } else {
                    qstring = keywords.split(" ").join(" AND ");
                }
            } else {
                $("#status").empty().html('<div class="alert alert-error"><button type="button" class="close" data-dismiss="alert">&times;</button>That&rsquo;s not a valid query...</div>');
                return;
            }
        } else {
            qstring = '%20';
        }
        var nucs = [];
        $('input:checked').each(function() {
            nucs.push($(this).val());
        });
        if (nucs.length > 0) {
            qstring += '+(nuc:"' + nucs.join('"+OR+nuc:"') + '")';
        }
        console.log(qstring);
        do_query(qstring);
    }


    function api_request() {
        var this_query = query;
        $("#status").empty().html("<p>Retrieving data for the " + decade_current + "0s...</p>");
        this_query = this_query + "&l-decade=" + decade_current;
        console.log(this_query);
        $.jsonp({
            //"dataType": "jsonp",
            //"jsonp": callback,
            "callbackParameter": 'callback',
            "url": this_query,
            "timeout": 20000,
            "success": function(results) {
                process_results(results);
            },
            "error": function(d, status) {
                if (status == "timeout") {
                    message = "Sorry, the server took too long to respond.";
                } else if (status == "error") {
                    message = "Sorry, I couldn't retrieve any data.";
                } else {
                    message = "Sorry, something went wrong.";
                }
                $("#status").empty().html('<div class="alert alert-error"><button type="button" class="close" data-dismiss="alert">&times;</button>' + message + '</div>');
                $("#graph").hideLoading();
                if (dataSources.sources.length === 0) {
                    $("#graph").hide();
                }
                reset_query();
            }
        });
   }

    function process_results(results) {
            $.each(results.response.zone, function(index, zone) {
                console.log(zone.name);
                console.log(zone.records.total);
                if (parseInt(zone.records.total, 10) > 0) {
                    var zone_name = zone.name;
                    $.each(zone.facets.facet.term, function(index, value) {
                        current_year = parseInt(value.display, 10);
                        if (current_year >= year_start && current_year <= year_end) {
                            current_series.data[zone_name][current_year] = {};
                            current_series.data[zone_name][current_year] = parseInt(value.count, 10);
                        }
                    });
                }
            });

        if (decade_current < decade_end) {
            decade_current++;
            api_request();
        } else {
            console.log(current_series);
            dataSources.sources.push(current_series);
            $("#graph").hideLoading();
            if (dataSources.sources.length > 0) {
                makeChart('total');
                $('#clear_last1').show();
                $('#clear_last2').show();
                if (dataSources.sources.length > 1) {
                    $('#clear_all1').show();
                    $('#clear_all2').show();
                }
            }
        }
    }

    function do_query(qstring) {
        reset();
        year_start = $('#start_year').val();
        year_end = $('#end_year').val();
        $("#graph").show().showLoading();
        //qstring = encodeURIComponent(qstring);
        query = trove_api_url + "zone=book,article,collection,map,music,collection,picture&q=" + qstring + "&facet=year&n=0&encoding=json&key=" + trove_api_key;
        decade_start = Math.floor(year_start / 10);
        decade_end = Math.floor(year_end / 10);
        decade_current = decade_start;
        current_series = new graphData();
        current_series.api_query = trove_api_url + "q=" + qstring + "&n=20&encoding=json&key=" + trove_api_key;
        current_series.web_query = qstring;
        api_request();
    }

    var chart;

    function makeChart(type) {
        $("#status").empty();
        $("#trove-results").show();
        $('#graph_type').val(type);
        if (dataSources.sources[0].interval == "month") {
            x_date = "%b %Y";
            xLabel = "Month";
        } else {
            x_date = "%Y";
            xLabel = "Year";
        }
        if (type == "total") {
            yLabel = "Number of resources";
        } else if (type == "ratio") {
            yLabel = "% of theses matching query";
        }
        chart = new Highcharts.Chart({
          chart: {
             renderTo: 'graph',
             type: 'spline',
             zoomType: 'x'
          },
          title: {
              text: 'Resources by date'
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
                        return this.value;
                    }
                },
              min: 0
           },
           tooltip: {
              formatter: function() {
                    year = new Date(this.x).getFullYear();
                    displayValue = this.y + " items";
                    return '<b>'+ this.series.name + '</b><br/>' + year +': ' + displayValue + '<br><em>Click to view.</em>';
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
            $('#graph').showLoading();
            var this_query = dataSources.sources[0].api_query;
            var zone = dataSources.getZone(series.name);
            this_query = this_query + "&l-year=" + query_date + "&zone=" + zone;
            var callback = "callback";
            $.jsonp({
                    //"dataType": "jsonp",
                    //"jsonp": callback,
                    "callbackParameter": callback,
                    "timeout": 20000,
                    "url": this_query,
                    "success": function(results) {
                        $('#articles').height('');
                        $('#articles').append('<h3>' + series.name + '</h3>');
                            show_trove_articles(results, query_date, series, zone);
                        $('#graph').hideLoading();
                        $('#articles').ScrollTo();
                    },
                    "error": function(d, status) {
                        if (status == "timeout") {
                            message = "Sorry, the server took too long to respond.";
                        } else if (status == "error") {
                            message = "Sorry, I couldn't retrieve any data.";
                        } else {
                            message = "Sorry, something went wrong.";
                        }
                        $("#status").empty().html('<div class="alert alert-error"><button type="button" class="close" data-dismiss="alert">&times;</button>' + message + '</div>');
                        $("#graph").hideLoading();
                    }
            });
    }
    function show_trove_articles(results, query_date, series, zone) {
        if (results.response.zone[0].records.work.length > 0) {
            var articles = $('<ul id="articles"></ul>');
            $.each(results.response.zone[0].records.work, function(key, article) {
                //newspaper = article.title.value.match(/(.*?) \(/)[1];
                //date = $.format.date(article.date + ' 00:00:00.000', 'd MMMM yyyy');
                articles.append('<li><a target="_blank" class="article" href="'+ article.troveUrl + '">' + article.title + '</a></li>');
            });
            $('#articles').append(articles);
        }
        console.log(dataSources.sources[0].web_query);
        var web_query = 'http://trove.nla.gov.au/' + zone + '/result?q=' + dataSources.sources[0].web_query + '+date%3A%5B' + query_date + '+TO+' + query_date + '%5D';
        $('#articles').append("<div class='more'><p><a class='btn' target='_blank' href='" + web_query + "'>&gt; View more in Trove</a></p></div>");

    }

    function clear_all() {
        $("input[type='checkbox']").prop('checked', false);
        $('#start_year').val('1800');
        $('#end_year').val('2013');
        $('#query').val('');
        $('#selected-heading').hide();
        $('#selected-collections').empty();
        reset();
    }
    function reset() {
        dataSources.sources = [];
        decade_current = decade_start;
        $("#graph").hide();
        $("#trove-results").hide();
        $("#articles").empty();
    }

    $("#do_keyword_query").button().click(function(){ get_query(); });
    $("#clear_all").button().click(function(){ clear_all(); });

    function showSelected() {
        if ($('input:checked').length > 0) {
            $('#selected-heading').show();
        } else {
            $('#selected-heading').hide();
        }
        $('#selected-collections').empty();
        $('input:checked').each(function() {
            $('#selected-collections').append('<li>' + $(this).parent().text() + '</li>');
        });
    }

    $(".tip-popover").popover();
    $("#loading-indicator-graph-overlay").click(function() {
        alert("hello");
        $("#graph").hideLoading();
    });
    $( "input[type='checkbox']" ).change(function() {
        if (this.checked) {
            $(this).parent().parent().parent().find("input[type='checkbox']").prop('checked', true);
        } else {
            $(this).parent().parent().parent().find("input[type='checkbox']").prop('checked', false);
        }
        showSelected();
    });
    $('#selected-heading').hide();
    $('#panes a').click(function (e) {
        e.preventDefault();
        $(this).tab('show');
    });
    $('#panes a:first').tab('show');
    //get_query();
    //load_nucs();
});




















