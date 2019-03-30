//http://bl.ocks.org/heybignick/3faf257bbbbc7743bb72310d03b86ee8
//http://bl.ocks.org/mbostock/1129492
//https://observablehq.com/@d3/disjoint-force-directed-graph

function create_graph(graph) {
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
      .strength(function(d) { return -100 * Math.pow(2, radius / 10); })
      )
    .force("x", d3.forceX())
    .force("y", d3.forceY())
    .on("tick", ticked);

  // Encompassing group for zoom.
  var g = svg.append("g").attr("class", "graph");
  var link = g.append("g").attr("class","links");
  var node = g.append("g").attr("class","nodes");

  render_graph();

  function render_graph() {

    node = node.selectAll("g.node").data(graph.nodes);
    node.exit().remove();

    let node_enter = node.enter().append("g")
      .attr("class","node")
      .on("click", select_node)
      .call(drag(simulation));

    node_enter.append("circle")
      .attr("class", "node-circle")
      .attr("fill", color)
      .attr("r", function(d) { return radius * (1 + d["value"]); });

    node_enter.append("text")
      .attr("dy", ".35em")
      .attr("class", "unselectable")
      .attr("text-anchor", "middle")
      .text(function(d) { return d.id });

    node = node_enter.merge(node);

    link = link.selectAll("line").data(graph.links);
    link.exit().remove();
    link = link.enter().append("line")
        .attr("class", "link")
        .attr("id", function(d) { return d.source + "-" + d.target })
      .merge(link)
      .attr("stroke-width", function(d) { return d["value"] / max_value * 6 + 1.0; });

    simulation.nodes(graph.nodes);
    simulation.force("link").links(graph.links);
    simulation.restart();

    // Zoom logic
    // From https://bl.ocks.org/puzzler10/4438752bb93f45dc5ad5214efaa12e4a
    var zoom_handler = d3.zoom()
        .on("zoom", zoom_actions);

    zoom_handler(svg);  
    // Disable double click to zoom.
    svg.on("dblclick.zoom", null)  

    // Zoom functions 
    function zoom_actions(){
        g.attr("transform", d3.event.transform)
    }
  }  

  function select_node(d, i, gs) {
    console.log(graph, graph.links);
    var is_selected = $(gs[i]).hasClass("selected");

    $(gs).removeClass("selected");
    $(gs).removeClass("adj_selected");
    $(".link").removeClass("selected");

    if (!is_selected) {
      $(gs[i]).addClass("selected");
      for (let i = 0; i < graph.links.length; i++) {
        if (graph.links[i].source !== d && graph.links[i].target !== d) continue;
        let other_node = graph.links[i].source;
        if (graph.links[i].source == d) other_node = graph.links[i].target;
        // Add appropriate classes to adjacent nodes and edges.
        if (other_node !== d) {
          let node_e = $(gs[other_node.index]);
          node_e.addClass("adj_selected");
          $("g.nodes").append(node_e); // Move selected nodes to top of DOM.
          let link_e = $("#"+graph.links[i].source.id+"-"+graph.links[i].target.id);
          link_e.addClass("selected");
          $("g.links").append(link_e);  // Move selected links to the top.
        }
      }
      $("g.nodes").append($(gs[i])); // Move selected node to top of DOM.
    }
    else {
      $(gs[i]).removeClass("selected");
    }
  }

  function ticked() {
    link.attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });

    node.attr("transform", function(d) { 
      return "translate(" + d.x + "," + d.y + ")";
    });
  }

  // Drag logic.
  function drag(simulation) {
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
}