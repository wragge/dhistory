var width = 960, height = 700;
$(function(){
  var facets = [
    'Abstract',
    'Book chapter',
    'Conference paper',
    'Journal or magazine article',
    'Other article',
    'Report',
    'Review',
    'Working paper',
    'Braille',
    'Illustrated',
    'Large print',
    'Aerial photograph',
    'Atlas',
    'Electronic',
    'Globe or object',
    'Large print',
    'Map series',
    'Microform',
    'Single map',
    'Journal, magazine, other',
    'Newspaper',
    'Interview, lecture, talk',
    'Other sound',
    'Recorded music',
    'Captioned',
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

  var radius = Math.min(width, height) / 2.1,
      color = d3.scale.category20c();

  var x = d3.scale.linear()
      .range([0, 2 * Math.PI]);

  var y = d3.scale.linear()
      .range([0, radius]);

  var svg = d3.select("#svg").append("svg")
      .attr("width", width)
      .attr("height", height)
    .append("g")
      .attr("transform", "translate(" + width / 2 + "," + (height / 2 + 10) + ")");

  var partition = d3.layout.partition()
      .value(function(d) { return d.size; });

  var arc = d3.svg.arc()
      .startAngle(function(d) { return Math.max(0, Math.min(2 * Math.PI, x(d.x))); })
      .endAngle(function(d) { return Math.max(0, Math.min(2 * Math.PI, x(d.x + d.dx))); })
      .innerRadius(function(d) { return Math.max(0, y(d.y)); })
      .outerRadius(function(d) { return Math.max(0, y(d.y + d.dy)); });

  var tooltip = d3.select("body")
    .append("div")
    .attr("class", "tooltip")
    .style("position", "absolute")
    .style("z-index", "10")
    .style("opacity", 0);

  function format_number(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  }

  function format_name(d) {
    var name = d.name;
    if (name in zone_names) {
      name = zone_names[name];
    }
    return  '<b>' + name + '</b><br>' + format_number(d.value) + ' resources';
  }

  function display_sunburst(data) {

    var path = svg.selectAll("path")
        .data(partition.nodes(data))
      .enter().append("path")
        .attr("d", arc)
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
      $('.results').empty();
      if (typeof d.children === "undefined" && d.name != 'Other') {
        get_zone(d);
      }
      path.transition()
        .duration(750)
        .attrTween("d", arcTween(d));
    }
  }

  //d3.select(self.frameElement).style("height", height + "px");

  // Interpolate the scales!
  function arcTween(d) {
    var xd = d3.interpolate(x.domain(), [d.x, d.x + d.dx]),
        yd = d3.interpolate(y.domain(), [d.y, 1]),
        yr = d3.interpolate(y.range(), [d.y ? 20 : 0, radius]);
    return function(d, i) {
      return i
          ? function(t) { return arc(d); }
          : function(t) { x.domain(xd(t)); y.domain(yd(t)).range(yr(t)); return arc(d); };
    };
  }

  function get_zone(d, leaf) {
    if (typeof leaf === 'undefined') {
      leaf = d;
    }
    if(d.depth !== 1) {
      get_zone(d.parent, leaf);
    } else {
      console.log(d.name);
      get_resources(leaf, d.name);
    }
  }

  function get_resources(leaf, zone) {
    $('.results').append('<p id="loading" class="muted">Loading resources...</p>');
    if ($.inArray(leaf.name, facets) > -1) {
      facet = leaf.parent.name + '/' + leaf.name;
    } else {
      facet = leaf.name;
    }
    start = Math.floor(Math.random() * (leaf.value - 10));
    console.log(start);
    get_results(zone, facet, start);
  }

  function get_results(zone, facet, start) {
    var url;
    if (typeof start === 'undefined') {
      //url = "http://api.trove.nla.gov.au/result?q=date:[* TO *] NOT nuc:SUSA&zone=" + zone + "&l-format=" + facet + "&n=0&encoding=json&key=" + api_key;
      url = "http://api.trove.nla.gov.au/result?q= &zone=" + zone + "&l-format=" + facet + "&n=0&encoding=json&key=" + api_key;

    } else {
      //url = "http://api.trove.nla.gov.au/result?q=date:[* TO *] NOT nuc:SUSA&zone=" + zone + "&l-format=" + facet + "&s=" + start + "&n=10&encoding=json&key=" + api_key;
      url = "http://api.trove.nla.gov.au/result?q= &zone=" + zone + "&l-format=" + facet + "&s=" + start + "&n=10&encoding=json&key=" + api_key;
    }
    $.jsonp({
      //"dataType": "jsonp",
      //"jsonp": callback,
      "callbackParameter": 'callback',
      "url": url,
      "timeout": 30000,
      "success": function(results) {
        prepare_results(zone, facet, start, results);
      },
      "error": function() {
        $('.results').empty().append('<p id="loading" class="muted">Botheration, something bad happened...</p>');
      }
    });
  }

  function prepare_results(zone, facet, start, results) {
    if (typeof start === 'undefined') {
      var total = results.response.zone[0].records.total;
      start = Math.floor(Math.random() * total);
      get_results(zone, facet, start);
    } else {
      var web_url = "http://trove.nla.gov.au/" + zone + "/result?q&l-format=" + facet;
      show_resources(results, web_url);
    }
  }

  function show_resources(results, web_url) {
    var list = $('<ul></ul>');
    $.each(results.response.zone[0].records.work, function(key, record) {
      var item = $('<li></li>');
      item.append('<a target="_blank" href="' + record.troveUrl + '">' + record.title + '</a>');
      list.append(item);
    });
    $('#loading').remove();
    $('.results').append(list);
    $('.results').append('<a target="_blank" id="more" class="pull-right btn btn-small" href="' + web_url + '">View more results</a>');
  }

  function get_data() {
    $.jsonp({
      //"dataType": "jsonp",
      //"jsonp": callback,
      "callbackParameter": 'callback',
      "url": "http://api.trove.nla.gov.au/result?q= &zone=book,article,collection,picture,map,music&facet=format&n=0&encoding=json&key=" + api_key,
      "timeout": 20000,
      "success": function(results) {
          process_results(results);
      }
    });
  }

  function process_results(results) {
    var data = {'name': 'Trove', 'children': []};
    $.each(results.response.zone, function(index, zone) {
      var this_zone = {'name': zone.name, 'children': []};
      $.each(zone.facets.facet.term, function(index, term) {
        this_child = process_term(term);
        this_zone.children.push(this_child.term);
      });
      data.children.push(this_zone);
    });
    display_sunburst(data);
  }

  function process_term(term) {
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
  }
  get_data();
});