//http://bl.ocks.org/heybignick/3faf257bbbbc7743bb72310d03b86ee8
//http://bl.ocks.org/mbostock/1129492
//https://observablehq.com/@d3/disjoint-force-directed-graph

var task_results = {"nodes":[{"id":"0","group":1},{"id":"1","group":1},{"id":"2","group":1},{"id":"3","group":1},{"id":"4","group":1},{"id":"100","group":1},{"id":"5","group":1},{"id":"8","group":1},{"id":"7","group":1},{"id":"6","group":1},{"id":"9","group":1},{"id":"10","group":1},{"id":"PINE","group":1},{"id":"STATE","group":1},{"id":"503160","group":1},{"id":"MENTHOL","group":1},{"id":"NON","group":1},{"id":"S","group":1},{"id":"TOB","group":1},{"id":"25","group":1}],"links":[{"source":"0","target":"1","value":10149},{"source":"0","target":"0","value":6874},{"source":"1","target":"1","value":3997},{"source":"0","target":"2","value":3701},{"source":"1","target":"2","value":3327},{"source":"0","target":"3","value":2042},{"source":"1","target":"3","value":1890},{"source":"0","target":"4","value":1888},{"source":"0","target":"100","value":1806},{"source":"2","target":"3","value":1619},{"source":"0","target":"5","value":1326},{"source":"0","target":"8","value":1292},{"source":"2","target":"2","value":1286},{"source":"1","target":"4","value":1273},{"source":"2","target":"4","value":1209},{"source":"0","target":"7","value":1104},{"source":"0","target":"6","value":1084},{"source":"1","target":"5","value":983},{"source":"3","target":"4","value":974},{"source":"1","target":"6","value":919},{"source":"3","target":"5","value":903},{"source":"1","target":"9","value":889},{"source":"1","target":"7","value":829},{"source":"3","target":"3","value":765},{"source":"2","target":"5","value":754},{"source":"3","target":"6","value":738},{"source":"0","target":"9","value":709},{"source":"3","target":"8","value":707},{"source":"2","target":"6","value":704},{"source":"1","target":"8","value":658},{"source":"2","target":"8","value":644},{"source":"4","target":"5","value":609},{"source":"4","target":"7","value":583},{"source":"2","target":"7","value":579},{"source":"4","target":"8","value":561},{"source":"2","target":"9","value":555},{"source":"5","target":"6","value":546},{"source":"5","target":"9","value":522},{"source":"3","target":"7","value":452},{"source":"0","target":"10","value":446},{"source":"4","target":"4","value":414},{"source":"6","target":"7","value":409},{"source":"3","target":"9","value":392},{"source":"PINE","target":"STATE","value":391},{"source":"503160","target":"PINE","value":380},{"source":"MENTHOL","target":"NON","value":366},{"source":"100","target":"S","value":360},{"source":"STATE","target":"TOB","value":358},{"source":"0","target":"25","value":352},{"source":"5","target":"8","value":347}]};

// Development stuff for static task_results.
var max_value = -1;
for (var i = 0; i < task_results["links"].length; i++) {
  max_value = Math.max(max_value, task_results["links"][i]["value"]);
}
for (var i = 0; i < task_results["nodes"].length; i++) {
  task_results["nodes"][i]["value"] = Math.random();
}

var svg = d3.select("svg"),
    width = document.getElementById("d3-viewport").clientWidth,
    height = document.getElementById("d3-viewport").clientHeight,
    radius = 6;
svg.attr("viewBox", [-width / 2, -height / 2, width, height]);

var color = d3.scaleOrdinal(d3.schemeCategory10);

var simulation = d3.forceSimulation()
    .force("link", d3.forceLink()
      .id(function(d) { return d.id; })      )
    .force("charge", d3.forceManyBody()
      .strength(function(d) { return -100; })
      )
    .force("x", d3.forceX())
    .force("y", d3.forceY());

var render_chart = function(graph) {
  // Clear svg.
  d3.selectAll("svg > *").remove();

  // Encompassing group for zoom.
  var g = svg.append("g")
    .attr("class", "everything");

  const link = g.append("g")
      .attr("class", "links")
      .attr("stroke", "#999")
      .attr("stroke-opacity", 0)
    .selectAll("line")
    .data(graph.links)
    .enter().append("line")
      .attr("stroke-width", function(d) { return d["value"] / max_value * 6 + 1.0; });

  const node = g.append("g")
      .attr("class", "nodes")
      .attr("stroke", "#fff")
      .attr("stroke-width", 1.5)
    .selectAll("circle")
    .data(graph.nodes)
    .enter().append("circle")
      .attr("r", function(d) { return radius * (1 + d["value"]); })
      .attr("fill", color)
      .call(drag(simulation))

  var text = g.append("g")
      .attr("class", "labels")
      .selectAll("text")
      .data(graph.nodes)
      .enter().append("text")
      .attr("dx", radius + 5)
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

  // Zoom logic
  // From https://bl.ocks.org/puzzler10/4438752bb93f45dc5ad5214efaa12e4a
  var zoom_handler = d3.zoom()
      .on("zoom", zoom_actions);

  zoom_handler(svg);    

  // Zoom functions 
  function zoom_actions(){
      g.attr("transform", d3.event.transform)
  }
}  

// Drag logic.
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

//render_chart(convert_data(1905));
render_chart(task_results);

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
