//http://bl.ocks.org/heybignick/3faf257bbbbc7743bb72310d03b86ee8
//http://bl.ocks.org/mbostock/1129492
//https://observablehq.com/@d3/disjoint-force-directed-graph

var svg = d3.select("svg"),
    width = document.getElementById("d3-viewport").clientWidth,
    height = document.getElementById("d3-viewport").clientHeight,
    radius = 8;
svg.attr("viewBox", [-width / 2, -height / 2, width, height]);

var color = d3.scaleOrdinal(d3.schemeCategory10);

var simulation = d3.forceSimulation()
    .force("link", d3.forceLink()
      .id(function(d) { return d.id; }))
    .force("charge", d3.forceManyBody()
      .strength(function(d) { return -100 * Math.pow(2, radius / 8); })
      )
    .force("x", d3.forceX())
    .force("y", d3.forceY());

function render_chart(graph) {
  // Clear svg.
  d3.selectAll("svg > *").remove();

  // Encompassing group for zoom.
  var g = svg.append("g")
    .attr("class", "everything");

  const links = g.append("g")
      .attr("class", "links")
      .attr("stroke", "#999")
      .attr("stroke-opacity", 0)
    .selectAll("line")
    .data(graph.links)
    .enter().append("line")
      .attr("class", "link")
      .attr("stroke-width", function(d) { return d["value"] / max_value * 6 + 1.0; });

  const nodes = g.append("g")
      .attr("class", "nodes")
    .selectAll("circle")
    .data(graph.nodes)
    .enter().append("g")
      .attr("class", "node")
      .on("click", select_node)
      .call(drag(simulation));

  nodes.append("circle")
    .attr("r", function(d) { return radius * (1 + d["value"]); })
    .attr("fill", color);

  nodes.append("text")      
    .attr("dy", ".35em")
    .attr("class", "unselectable")
    .attr("text-anchor", "middle")
    .text(function(d) { return d.id });

  function select_node(d, i, gs) {
    console.log(graph, links);
    var is_selected = $(gs[i]).hasClass("selected");

    $(gs).removeClass("selected");
    $(gs).removeClass("adj_selected");
    $(links._groups[0]).removeClass("selected");

    if (!is_selected) {
      $(gs[i]).addClass("selected");
      for (let i = 0; i < graph.links.length; i++) {
        if (graph.links[i].source !== d && graph.links[i].target !== d) continue;
        let other_node = graph.links[i].source;
        if (graph.links[i].source == d) other_node = graph.links[i].target;
        if (other_node !== d) {
          $(gs[other_node.index]).addClass("adj_selected");
          $(links._groups[0][graph.links[i].index]).addClass("selected");
        }
      }
    }
    else {
      $(gs[i]).removeClass("selected");
    }
  }

  simulation
      .nodes(graph.nodes)
      .on("tick", ticked);

  simulation.force("link")
      .links(graph.links);

  function ticked() {
    links.attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });

    nodes.attr("transform", function(d) {
          return "translate(" + d.x + "," + d.y + ")";
        });
  }

  // Zoom logic
  // From https://bl.ocks.org/puzzler10/4438752bb93f45dc5ad5214efaa12e4a
  var zoom_handler = d3.zoom()
      .on("zoom", zoom_actions);

  zoom_handler(svg);  
  svg.on("dblclick.zoom", null)  

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