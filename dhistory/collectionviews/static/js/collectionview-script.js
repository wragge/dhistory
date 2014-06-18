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
    this.data.tree = {};
    this.interval = 'year';
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
    var height = 700;
    reset();
    var trove_api_key = "1g8lo7p9vtj0b89";
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

    var SUNBURST = function() {

        var facets = [
            'Article/Abstract',
            'Article/Book chapter',
            'Article/Conference paper',
            'Article/Journal or magazine article',
            'Article/Other article',
            'Article/Report',
            'Article/Review',
            'Article/Working paper',
            'Book/Braille',
            'Book/Illustrated',
            'Book/Large print',
            'Map/Aerial photograph',
            'Map/Atlas',
            'Map/Braille',
            'Map/Electronic',
            'Map/Globe or object',
            'Map/Large print',
            'Map/Map series',
            'Map/Microform',
            'Map/Single map',
            'Periodical/Journal, magazine, other',
            'Periodical/Newspaper',
            'Sound/Interview, lecture, talk',
            'Sound/Other sound',
            'Sound/Recorded music',
            'Video/Captioned',
            ];
          var zone_names = {
            'book': 'Books',
            'article': 'Journals, articles and data sets',
            'picture': 'Pictures, photos, objects',
            'music': 'Music, sound, video',
            'map': 'Maps',
            'collection': 'Diaries, letters, archives'
            };

        var api_key = "1g8lo7p9vtj0b89";

        var format_number = function(x) {
            return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
        };

        var format_name = function(d) {
            var name = d.name;
            if (name in zone_names) {
              name = zone_names[name];
            }
            return  '<b>' + name + '</b><br>' + format_number(d.value) + ' resources';
        };

        var display_sunburst = function(data) {
            var width = $("#graph").width();

            var radius = Math.min(width, height) / 2;

            var color = d3.scale.category20c();

            var x = d3.scale.linear()
              .range([0, 2 * Math.PI]);

            var y = d3.scale.linear()
              .range([0, radius]);

            d3.select(".tooltip").remove();
            d3.select("#sunburst-svg").remove();
            var svg = d3.select("#sunburst-container").append("svg")
              .attr("width", width)
              .attr("height", height)
              .attr("id", "sunburst-svg")
            .append("g")
              .attr("transform", "translate(" + width / 2 + "," + (height / 2) + ")");

            var arc = d3.svg.arc()
              .startAngle(function(d) { return Math.max(0, Math.min(2 * Math.PI, x(d.x))); })
              .endAngle(function(d) { return Math.max(0, Math.min(2 * Math.PI, x(d.x + d.dx))); })
              .innerRadius(function(d) { return Math.max(0, y(d.y)); })
              .outerRadius(function(d) { return Math.max(0, y(d.y + d.dy)); });

            var partition = d3.layout.partition()
              .value(function(d) { return d.size; });

            var tooltip = d3.select("body")
                .append("div")
                .attr("class", "tooltip")
                .style("position", "absolute")
                .style("z-index", "10")
                .style("opacity", 0);

            var path = svg.selectAll("path").data(partition.nodes(data))
            
            .enter().append("path")
                .attr("d", function(d) { return arc(d); })
                .style("fill", function(d) { return color((d.children ? d : d.parent).name); })
                .on("click", click)
                .on("mouseover", function(d) {
                  tooltip.html(function() {
                      var name = format_name(d);
                      return name;
                  });
                  return tooltip.transition()
                    .duration(50)
                    .style("opacity", 0.9);
                })
                .on("mousemove", function(d) {
                  return tooltip
                    .style("top", (d3.event.pageY-10)+"px")
                    .style("left", (d3.event.pageX+10)+"px");
                })
                .on("mouseout", function(){return tooltip.style("opacity", 0);});

            function click(d) {
                $('#format-articles').empty();
                console.log(d.name);
                if (d.name != 'Other') {
                    if (d.depth > 0) {
                        get_zone(d);
                    }
                    path.transition()
                        .duration(750)
                        .attrTween("d", arcTween(d));
                }
            }

            // Interpolate the scales!
            var arcTween = function(d) {
                var xd = d3.interpolate(x.domain(), [d.x, d.x + d.dx]),
                    yd = d3.interpolate(y.domain(), [d.y, 1]),
                    yr = d3.interpolate(y.range(), [d.y ? 20 : 0, radius]);
                return function(d, i) {
                  return i ? function(t) { return arc(d); }
                      : function(t) { x.domain(xd(t)); y.domain(yd(t)).range(yr(t)); return arc(d); };
                };
            };
            $('#graph').hideLoading();
        };

      //d3.select(self.frameElement).style("height", height + "px");

      var get_zone = function(d, leaf) {
        console.log(d);
        if (typeof leaf === 'undefined') {
          leaf = d;
        }
        if (d.depth !== 1) {
          get_zone(d.parent, leaf);
        } else {
          console.log(d.name);
          get_resources(leaf, d.name);
        }
      };

      var get_resources = function(leaf, zone) {
        $("#sunburst-info").hide();
        $('#format-articles').append('<p id="loading" class="muted">Loading resources...</p>');
        if (leaf.depth == 1) {
            facet = null;
        } else if ($.inArray((leaf.parent.name + '/' + leaf.name), facets) > -1) {
            facet = leaf.parent.name + '/' + leaf.name;
        } else {
            facet = leaf.name;
        }
        var start = 0;
        if (leaf.value > 10) {
            start = Math.floor(Math.random() * (leaf.value -10)) + 1;
        }
        console.log(start);
        get_results(zone, facet, start);
      };

      var get_results = function(zone, facet, start) {
        var qstring = dataSources.sources[0].web_query;
        var url = "http://api.trove.nla.gov.au/result?q=" + qstring + " date:[" + year_start + "+TO+" + year_end + "]&zone=" + zone + "&s=" + start + "&n=10&encoding=json&key=" + api_key;
        if (facet !== null) {
            url += "&l-format=" + facet;
        }
        $.jsonp({
          //"dataType": "jsonp",
          //"jsonp": callback,
          "callbackParameter": 'callback',
          "url": url,
          "timeout": 30000,
          "success": function(results) {
            show_resources(zone, facet, qstring, results);
          },
          "error": function() {
            $("#loading").remove();
            $('#format-articles').empty().append('<p id="loading" class="muted">Botheration, something bad happened...</p>');
          }
        });
      };

      var show_resources = function(zone, facet, qstring, results) {
        var web_url = "http://trove.nla.gov.au/" + zone + "/result?q=" + qstring + " date:[" + year_start + "+TO+" + year_end + "]";
        var heading;
        if (facet !== null) {
            web_url += "&l-format=" + facet;
        }
        $('#format-articles').append("<h3>" + zone_names[zone] + "</h3>");
        if ( facet !== null ) {
           $('#format-articles').append("<h4>" + facet + "</h4>");
        }
        var list = $('<ul></ul>');
        $.each(results.response.zone[0].records.work, function(key, record) {
          var item = $('<li></li>');
          item.append('<a target="_blank" href="' + record.troveUrl + '">' + record.title + '</a>');
          list.append(item);
        });
        $('#loading').remove();
        $('#format-articles').append(list);
        $('#format-articles').append("<a class='pull-right btn btn-small' target='_blank' href='" + web_url + "'>View more in Trove</a>");
      };

      var get_data = function(qstring) {
        $.jsonp({
          //"dataType": "jsonp",
          //"jsonp": callback,
          "callbackParameter": 'callback',
          "url": "http://api.trove.nla.gov.au/result?zone=book,article,collection,picture,map,music&q=" + qstring + " date:[" + year_start + "+TO+" + year_end + "]" + "&facet=format&n=0&encoding=json&key=" + api_key,
          "timeout": 30000,
          "success": function(results) {
              process_results(results);
          },
          "error": function() {
                $("#graph").hideLoading();
                $('#format-articles').empty().append('<p id="loading" class="muted">Botheration, something bad happened...</p>');
          }
        });
      };

      var process_results = function(results) {
        var data = {'name': 'All', 'children': []};
        $.each(results.response.zone, function(index, zone) {
            if (typeof zone.facets !== 'undefined' && typeof zone.facets.facet !== 'undefined') {
                var this_zone = {'name': zone.name, 'children': []};
                $.each(zone.facets.facet.term, function(index, term) {
                    var this_child = process_term(term);
                    this_zone.children.push(this_child.term);
                });
                data.children.push(this_zone);
            }
        });
        display_sunburst(data);
      };

      var process_term = function(term) {
        var term_count = parseInt(term.count, 10);
        var this_term = {'name': term.display};
        var count = 0;
        if (typeof term.term !== 'undefined') {
          this_term.children = [];
          $.each(term.term, function(index, child) {
            var this_child = process_term(child);
            this_term.children.push(this_child.term);
            count = count + this_child.term.size;
            console.log(count);
          });
          if (term_count > count) {
            other_count = term_count - count;
            this_term.children.push({'name': 'Other', 'size': other_count});
          }
        } else {
          this_term.size = term_count;
        }
        return {'term': this_term, 'count': count};
      };
      return { get_data: get_data};
    }();

    function reset_query() {
        query = '';
        interval = "year";
        queries = [];
        query_type = 'ratio';
    }

    function get_query() {
        reset();
        $('#panes a').eq(1).tab('show');
        var qstring, params = [];
        if ($("#query").val() !== "") {
            var keywords = $("#query").val();
            if (keywords.match(/^[a-zA-Z0-9\d"\(\)\~\:\-\/\. ]+$/)) {
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
            params.push('q=' + keywords);
        } else {
            qstring = '%20';
        }
        var nucs = [];
        if ($('#nucs').val() !== null) {
            $.each($('#nucs').val(), function(index, nuc) {
                nucs.push(nuc);
                params.push('nuc=' + nuc);
            });
        }
        if (nucs.length > 0) {
            qstring += '+(nuc:"' + nucs.join('"+OR+nuc:"') + '")';
        }
        console.log(qstring);
        do_query(qstring, params);
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
                $("#loading").remove();
                $('#articles').empty().append('<p id="loading" class="muted">Botheration, something bad happened...</p>');
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
                if (typeof zone.facets.facet !== 'undefined') {
                    $.each(zone.facets.facet.term, function(index, value) {
                        var zone_name = zone.name;
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
            dataSources.sources.push(current_series);
            //$("#graph").hideLoading();
            if (dataSources.sources.length > 0) {
                makeChart('total');
                $('#clear_last1').show();
                $('#clear_last2').show();
                if (dataSources.sources.length > 1) {
                    $('#clear_all1').show();
                    $('#clear_all2').show();
                }
            }
            SUNBURST.get_data(current_series.web_query);
        }
    }

    function do_query(qstring, params) {
        year_start = $('#start_year').val();
        year_end = $('#end_year').val();
        params.push('start=' + year_start);
        params.push('end=' + year_end);
        history.pushState('data', '', '/trove/profiler/?' + params.join('&'));
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
                text: '',
                style: {
                    display: 'none'
                }
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
                            showArticles(query_date, this);
                        }
                     }
                  }
               }
            }
        });
    }
    function showArticles(query_date, point) {
        console.log(dataSources.getZone(point.series.name));
        $('#articles').empty().height('50px');
            //$('#graph').showLoading();
            $("#graph-info").hide();
            $('#articles').append('<p id="loading" class="muted">Loading resources...</p>');
            var qstring = dataSources.sources[0].web_query;
            var this_query = trove_api_url + "q=" + qstring + "+date:[" + query_date + "+TO+" + query_date + "]&n=10&encoding=json&key=" + trove_api_key;
            var zone = dataSources.getZone(point.series.name);
            this_query = this_query + "&zone=" + zone;
            start = Math.floor(Math.random() * (point.y -10)) + 1;
            this_query = this_query + "&s=" + start;
            var callback = "callback";
            $.jsonp({
                    "callbackParameter": callback,
                    "timeout": 20000,
                    "url": this_query,
                    "success": function(results) {
                        $('#articles').height('');
                        $('#articles').append('<h3>' + point.series.name + '</h3>');
                        $('#articles').append('<h4>' + query_date + '</h4>');
                            show_trove_articles(results, query_date, point.series, zone);
                        //$('#graph').hideLoading();
                        //$('#articles').ScrollTo();
                    },
                    "error": function(d, status) {

                        if (status == "timeout") {
                            message = "Sorry, the server took too long to respond.";
                        } else if (status == "error") {
                            message = "Sorry, I couldn't retrieve any data.";
                        } else {
                            message = "Sorry, something went wrong.";
                        }
                        $("#loading").remove();
                        $('#format-articles').empty().append('<p id="loading" class="muted">Botheration, something bad happened...</p>');                        //$("#graph").hideLoading();
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
        $('#articles').append("<a class='btn btn-small pull-right' target='_blank' href='" + web_query + "'>View more in Trove</a>");
        $("#loading").remove();
    }

    function clear_all() {
        $('#nucs').multiSelect('deselect_all');
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
        $("#graph").empty();
        $("#trove-results").hide();
        $("#articles").empty();
        $("#format-articles").empty();
        $("#svg").remove();
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

    function checkOnLoad() {
        if ($('#preset').val() == "true") {
            //history.pushState('data', '', '/troveprofiler/');
            showSelected();
            get_query();
        }
    }

    $(".tip-popover").popover();
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
        $(".tooltip").css("opacity", 0);
        $(this).tab('show');
    });
    $('#panes a:first').tab('show');
    //get_query();
    //load_nucs();
    $('#nucs').multiSelect({
        selectableOptgroup: true,
        selectableHeader: "<input type='text' class='search-input' autocomplete='off' placeholder='Filter'>",
        selectionHeader: "<div class='selected-header muted'>Currently selected</div>",
        afterInit: function(ms){
            var that = this,
                $selectableSearch = that.$selectableUl.prev(),
                //$selectionSearch = that.$selectionUl.prev(),
                selectableSearchString = '#'+that.$container.attr('id')+' .ms-elem-selectable:not(.ms-selected)';
                //selectionSearchString = '#'+that.$container.attr('id')+' .ms-elem-selection.ms-selected';

            that.qs1 = $selectableSearch.quicksearch(selectableSearchString,
                {
                    onAfter: function() {
                        $('.ms-optgroup', $('.ms-selectable')).each(function() {
                            $(this).parent().show();
                            if ($(this).children('.ms-elem-selectable:visible').length === 0) {
                                $(this).parent().hide();
                            }
                        });
                    },
                })
            .on('keydown', function(e){
              if (e.which === 40){
                that.$selectableUl.focus();
                console.log(that);
                return false;
              }
            });

        },
        afterSelect: function(){
            this.qs1.cache();
            this.qs2.cache();
        },
        afterDeselect: function(){
            this.qs1.cache();
            this.qs2.cache();
        }
    });
    checkOnLoad();
});




















