//http://bl.ocks.org/heybignick/3faf257bbbbc7743bb72310d03b86ee8
//http://bl.ocks.org/mbostock/1129492
//https://observablehq.com/@d3/disjoint-force-directed-graph

var svg = d3.select("svg"),
    width = +svg.attr("width"),
    height = +svg.attr("height"),
    radius = 6;
svg.attr("viewBox", [-width / 2, -height / 2, width, height]);

var color = d3.scaleOrdinal(d3.schemeCategory10);

var render_chart = function(graph) {
  d3.selectAll("svg > *").remove();

  var simulation = d3.forceSimulation()
    .force("link", d3.forceLink().id(function(d) { return d.id; }))
    .force("charge", d3.forceManyBody())
    .force("x", d3.forceX())
    .force("y", d3.forceY());

  const link = svg.append("g")
      .attr("class", "links")
      .attr("stroke", "#999")
      .attr("stroke-opacity", 0.6)
    .selectAll("line")
    .data(graph.links)
    .enter().append("line")
      .attr("stroke-width", function(d) { return 1.5; });

  const node = svg.append("g")
      .attr("class", "nodes")
      .attr("stroke", "#fff")
      .attr("stroke-width", 1.5)
    .selectAll("circle")
    .data(graph.nodes)
    .enter().append("circle")
      .attr("r", radius)
      .attr("fill", color)
      .call(drag(simulation));

  var text = svg.append("g")
      .attr("class", "labels")
      .selectAll("text")
      .data(graph.nodes)
      .enter().append("text")
      .attr("dx", radius+5)
      .attr("dy", ".35em")
      .attr("class", "unselectable")
      .text(function(d) { return d.id });

  simulation
      .nodes(graph.nodes)
      .on("tick", ticked);

  simulation.force("link")
      .links(graph.links);

  function ticked() {
    link.attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });

    node.attr("transform", function(d) {
          return "translate(" + d.x + "," + d.y + ")";
        });

    text.attr("x", function(d) { return d.x; })
        .attr("y", function(d) { return d.y; });
  }
}

var drag = function(simulation) {
  function dragstarted(d) {
    if (!d3.event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
  }
  
  function dragged(d) {
    d.fx = d3.event.x;
    d.fy = d3.event.y;
  }
  
  function dragended(d) {
    if (!d3.event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
  }
  
  return d3.drag()
      .on("start", dragstarted)
      .on("drag", dragged)
      .on("end", dragended);
}

// Zoom stuff from https://bl.ocks.org/puzzler10/4438752bb93f45dc5ad5214efaa12e4a
// Add zoom capabilities 
var zoom_handler = d3.zoom()
    .on("zoom", zoom_actions);

zoom_handler(svg);    

// Zoom functions 
function zoom_actions(){
    svg.attr("transform", d3.event.transform)
}

var convert_data = function(year) {
  var data = task_results[year];
  var node_set = new Set([]);
  var links = [];
  data.forEach(function(element) {
    node_set.add(element[0][0]);
    node_set.add(element[0][1]);
    links.push({
      "source": element[0][0],
      "target": element[0][1],
      "value": element[1]
    });
  });
  var nodes = [];
  node_set.forEach(function(element) {
    nodes.push({
      "id": element,
      "group": 1
    });
  });
  return {"nodes": nodes, "links": links};
}

var min_year = 3000;
var max_year = 0;
Object.keys(task_results).forEach(function(year) {
  year = parseInt(year);
  if (year > max_year)
    max_year = year;
  if (year < min_year)
    min_year = year;
});

$("#year-slider").slider({
  min: min_year,
  max: max_year,
  values: [(min_year + max_year) / 2],
  slide: function(event, ui) {
    update_graph(ui.values[0]);
  },
});

function update_graph(year) {
  $("#selected-year").text("Year: " + year);
  render_chart(convert_data(year));
}
update_graph($("#year-slider").slider("values")[0]);