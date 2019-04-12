//http://bl.ocks.org/heybignick/3faf257bbbbc7743bb72310d03b86ee8
//http://bl.ocks.org/mbostock/1129492
//https://observablehq.com/@d3/disjoint-force-directed-graph
//http://bl.ocks.org/ericcoopey/6c602d7cb14b25c179a4

function getLinkId(link) {
  if (typeof link.source === "string")
    return link.source + "-" + link.target;
  return link.source.id + "-" + link.target.id;
}

function createGraph(graph, graph_id) {
  // Defensive copy.
  graph = $.extend(true, {}, graph);

  var viewport = $(".d3-viewport[value='"+graph_id+"']");
  var svg = d3.select(".d3-viewport[value='"+graph_id+"'] > svg"),
      radius = 8;
  var graph_svg = $(".d3-viewport[value='"+graph_id+"'] > svg");

  this.updateViewport = function() {
    var width = $(graph_svg)[0].clientWidth;
    var height = $(graph_svg)[0].clientHeight;
    svg.attr("viewBox", [-width / 2, -height / 2, width, height]);
  }

  this.updateLabel = function(year) {
    $(viewport).find(".year-label").text(year);
  }

  var colorScale = d3.scaleOrdinal(d3.schemeCategory10);
  colorScale.domain([0,1,2,3,4,5,6,7,8,9]);

  var groupIndex = {};
  var sortedNodes = graph.nodes.slice();
  sortedNodes.sort(function(a, b) {
      if (a.group === b.group) return 0;
      else if (a.group < b.group) return -1;
      return 1;
  });

  for (var i = 0; i < sortedNodes.length; i++) {
    let node = sortedNodes[i];
    if (groupIndex[node.group] === undefined) 
      groupIndex[node.group] = Object.keys(groupIndex).length;
  }

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
  var link = g.append("g").attr("class","links").selectAll("line");
  var node = g.append("g").attr("class","nodes").selectAll("g.node");

  renderGraph();

  function findNode(node_id) {
    for (let i = 0; i < graph.nodes.length; i++) {
      if (graph.nodes[i].id == node_id) return i;
    }
    return -1;
  }

  function findLink(link) {
    let link_id = getLinkId(link);
    for (let i = 0; i < graph.links.length; i++) {
      if (link_id === getLinkId(graph.links[i]))
        return i;
    }
    return -1;
  }

  function clamp(val) {
    if (val < 0.0) return 0.0;
    if (val > 1.0) return 1.0;
    return val;
  }

  this.addNode = function(node) {
    graph.nodes.push(node);
    if (groupIndex[node.group] === undefined) 
      groupIndex[node.group] = Object.keys(groupIndex).length;
    renderGraph();
  }

  this.addLink = function(link) {
    graph.links.push(link);
    renderGraph();
  }

  this.removeNode = function(node_id) {
    let index = findNode(node_id);
    if (index !== -1) {
      graph.nodes.splice(index, 1);
      graph.links = graph.links.filter(function(value, index, arr) {
        return value.source.id !== node_id && value.target.id !== node_id;
      });
    }
    renderGraph();
  };

  this.removeLink = function(link) {
    let index = findLink(link);
    if (index !== -1) {
      graph.links.splice(index, 1);
    }
    renderGraph();
  }

  this.updateNodeValue = function(node_id, node_value) {
    let index = findNode(node_id);
    if (index === -1) return;
    graph.nodes[index].value = clamp(node_value);
    renderGraph();
  }

  this.updateLinkValue = function(link) {
    let index = findLink(link);
    if (index === -1) return;
    graph.links[index].value = link.value;
    renderGraph();
  }

  this.getData = function() {
    return graph;
  }

  function renderGraph() {
    node = node.data(graph.nodes, function(d) { return d.id });
    node.exit().remove();

    let node_enter = node.enter().append("g")
      .attr("class","node")
      .attr("value", function(d) { return d.id; })
      .attr("id", function(d) { return graph_id+"_"+d.id; })
      .call(drag(simulation));

    node_enter.append("circle")
      .attr("class", "node-circle")
      .attr("fill", function(d, i) { return colorScale(groupIndex[d.group]); });

    node_enter.append("text")
      .attr("dy", ".35em")
      .attr("class", "unselectable")
      .attr("text-anchor", "middle")
      .text(function(d) { return d.id });

    node = node_enter.merge(node);

    node
      .classed("adj_selected", false)
      .on("click", handle_select_node);

    node.select("circle")
      .attr("r", function(d) { return radius * (1 + d["value"]); });

    var max_value = -1;
    for (let i = 0; i < graph.links.length; i++) {
      max_value = Math.max(max_value, graph.links[i].value);
    }

    link = link.data(graph.links, function(d) { return getLinkId(d); });
    link.exit().remove();
    link = link.enter().append("line")
        .attr("class", "link")
      .merge(link)
      .attr("value", getLinkId)
      .attr("id", function(d) { return graph_id+"_"+getLinkId(d); })
      .classed("selected", false)
      .attr("stroke-width", function(d) { return d["value"] / max_value * 6 + 1.0; });

    simulation.nodes(graph.nodes);
    simulation.force("link").links(graph.links);
    // Restart with some alpha so that new nodes/links move. 
    simulation.alpha(0.1).restart();

    $("g.node.selected").each(function() {
      select_node($(this).attr("value"));
    });

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
  
  this.select_node = function(value) {
    this.unselect_nodes();

    let node = $("g.node#"+graph_id+"_"+value);
    let id = node.id;
    let idx = findNode(value);
    if (idx == -1) return;
    let data = graph.nodes[idx];

    $(node).addClass("selected");
    for (let i = 0; i < graph.links.length; i++) {
      if (graph.links[i].source !== data && graph.links[i].target !== data) continue;
      let other_node = graph.links[i].source;
      if (graph.links[i].source === data) other_node = graph.links[i].target;
      // Add appropriate classes to adjacent nodes and edges.
      if (other_node !== data) {
	      let node_e = $("g.node#"+graph_id+"_"+other_node.id);
        node_e.addClass("adj_selected");
        $(graph_svg).find("g.nodes").append(node_e); // Move selected nodes to top of DOM.
        let link = $("#"+graph_id+"_"+getLinkId(graph.links[i]));
        link.addClass("selected");
        $(graph_svg).find("g.links").append(link);  // Move selected links to the top.
      }
    }
    $(graph_svg).find("g.nodes").append($(node)); // Move selected node to top of DOM.
  }

  this.unselect_nodes = function() {
    $(graph_svg).find("g.node").removeClass("selected").removeClass("adj_selected");
    $(graph_svg).find(".link").removeClass("selected");
  }

  function handle_select_node(d, i, gs) {
    var is_selected = $(gs[i]).hasClass("selected");
    let value = $(gs[i]).attr("value");

    if (!is_selected) {
      select_node(value);
    }
    else {
      unselect_nodes();
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


function updateGraph(graph, new_data) {
  let old_data = graph.getData();

  function diff(old_data, new_data, get_id) {
    let oldIds = new Set();
    let newIds = new Set();
    let oldIdxs = {};

    let add = new Set();
    let update = new Set();
    let remove = new Set();

    for (let i = 0; i < old_data.length; i++) {
      let id = get_id(old_data[i]);
      oldIds.add(id);
      oldIdxs[id] = i;
    }
    for (let i = 0; i < new_data.length; i++) {
      let id = get_id(new_data[i]);
      newIds.add(id);
      if (!oldIds.has(id)) {
        add.add(new_data[i]);
      } else {
        let oldNode = old_data[oldIdxs[id]];
        // TODO: Generalize.
        if (oldNode.value !== new_data[i].value) {
          update.add(new_data[i]);
        }
      }
    }
    for (let i = 0; i < old_data.length; i++) {
      if (!newIds.has(get_id(old_data[i])))
        remove.add(old_data[i]);
    }
    return [add, update, remove];
  }

  let node_action_items = diff(old_data.nodes, new_data.nodes, function(d) { return d.id; });
  let link_action_items = diff(old_data.links, new_data.links, getLinkId);
  
  node_action_items[2].forEach(function(d) {
    graph.removeNode(d.id);
  });
  node_action_items[0].forEach(function(d) {
      graph.addNode(d);
  });
  node_action_items[1].forEach(function(d) {
      graph.updateNodeValue(d.id, d.value);
  });

  link_action_items[2].forEach(function(d) {
    graph.removeLink(d);
  });
  link_action_items[0].forEach(function(d) {
    graph.addLink(d);
  });
  link_action_items[1].forEach(function(d) {
    graph.updateLinkValue(d);
  });
}

// Create and initialize year buttons.
var years = get_data_years();

years.sort();
years.forEach(function(year) {
  $("#year-options").append("<a value=\""+year+"\" class=\"year-btn btn btn-default\">"+year+"</a>");
});

var year_panes = {};
var selected_years = [];
// Currently, changing this to > 3 will break things. Sorry!
const max_panes = 3;

// If visualizing multiple results, assign panes to each result.
var result_panes = {};
if (is_multi_result()) {
  let pane_num = 0;
  Object.keys(task_results).forEach(function(id) {
    if (pane_num >= max_panes) return;
    result_panes[id] = pane_num++;
  });
}

var graphs = [];

function select_node(value) {
  for (let i = 0; i < graphs.length; i++) {
    graphs[i].select_node(value);
  }
}
function unselect_nodes() {
  for (let i = 0; i < graphs.length; i++) {
    graphs[i].unselect_nodes();
  }
}

$(".year-btn").on("click", function(e) {
  let year = parseInt($(this).attr("value"));

  let multiselect = e.ctrlKey;
  var button_selected = $(this).hasClass("btn-selected");
  var num_selected = $(".btn-selected").length;

  // Disable year multiselect if visualizing from multiple results.
  if (is_multi_result()) multiselect = false;

  // TODO: Comment reasoning
  if (!multiselect) {
    if (num_selected > 1 || !button_selected) {
      select_year(year, multiselect)
    } else if (button_selected) {
      unselect_year(year, multiselect);
    }
  } else {
    if (!button_selected) { // Button was just selected.
      select_year(year, multiselect);
    } else {
      unselect_year(year, multiselect);
    }
  }
  update_panes();
});

function assign_pane(year) {
  if (year_panes[year] !== undefined)
    return year_panes[year];

  var i = 0;
  // Find lowest-indexed pane not in use.
  for (i = 0; i < max_panes; i++) {
    var in_use = false;
    for (var index in year_panes) {
      if (year_panes[index] == i) {
        in_use = true;
        break;
      }
    }
    if (!in_use) break;
  }
  year_panes[year] = i;
  return i;
}

// Adjust width of visible panes.
function update_panes() {
  $(".d3-viewport").removeClass("col-sm-4");
  $(".d3-viewport").removeClass("col-sm-6");
  $(".d3-viewport").removeClass("col-sm-12");
  $(".d3-viewport").addClass("hidden");

  let item_list = is_multi_result() ? Object.keys(task_results) : selected_years;

  let class_to_add;
  if (item_list.length == 3) {
    class_to_add = "col-sm-4";
  } else if (item_list.length == 2) {
    class_to_add = "col-sm-6";
  } else if (item_list.length <= 1) {
    class_to_add = "col-sm-12";
  }
  for (var i = 0; i < item_list.length; i++) {
    let v = is_multi_result() ? result_panes[item_list[i]] : year_panes[item_list[i]];
    let pane_viewport = $(".d3-viewport[value='"+v+"']");
    pane_viewport.addClass(class_to_add);
    pane_viewport.removeClass("hidden");
  }
  let sorted_items = item_list.slice().sort();
  for (var i = 0; i < sorted_items.length; i++) {
    let v = is_multi_result() ? result_panes[item_list[i]] : year_panes[item_list[i]];
    let pane_viewport = $(".d3-viewport[value='"+v+"']");
    graphs[v].updateViewport();
    $("#viewport-container").append(pane_viewport);
  }
}

function unselect_year(year, multiselect) {
  let element = $(".year-btn[value='"+year+"']");
  $(element).removeClass("btn-selected");
  delete year_panes[year];
  selected_years.splice(selected_years.indexOf(year), 1);
}

function select_year(year, multiselect) {
  year = parseInt(year);
  let element = $(".year-btn[value='"+year+"']")[0];

  $(element).addClass("btn-selected");

  let scroll_height = $("#year-options")[0].offsetHeight;
  let element_height = element.offsetHeight;
  let element_pos = $(element).position().top;
  // Element not currently visible. We want to make it visible.
  if (element_pos + element_height < 0 || element_pos > scroll_height) {
    let amount_to_scroll = element_pos - (scroll_height / 2) + element_height;
    $("#year-options")[0].scrollTop += amount_to_scroll;
  }

  if (selected_years.indexOf(year) == -1)
    selected_years.push(year);

  if (multiselect) {
    // If max number of years have been selected, replace one of the old
    // selected years with this new one.
    if (selected_years.length > max_panes) {
      unselect_year(selected_years[0], multiselect);
    }
  } 
  else { // If not multiselect, remove all other years.
    let years_to_remove = selected_years.slice();
    years_to_remove.splice(selected_years.indexOf(year),1);
    for (let i = 0; i < years_to_remove.length; i++) {
      unselect_year(years_to_remove[i], multiselect);
    }
  }

  // Standard year visualization.
  if (!is_multi_result()) {
    let pane_number = assign_pane(year);
    if (graphs.length <= pane_number) {
      graphs.push(new createGraph(convert_data(year), pane_number));
      update_panes();
    } else {
      update_panes();
      updateGraph(graphs[pane_number], convert_data(year));
    }
    graphs[pane_number].updateLabel(year);
  } else {
    let result_ids = Object.keys(task_results);
    for (let i = 0; i < result_ids.length; i++) {
      let result_id = result_ids[i];
      let result_pane = result_panes[result_id];
      if (graphs.length <= result_pane) {
        graphs.push(new createGraph(convert_data_by_id(result_id, year), result_pane));
      } else {
        updateGraph(graphs[result_pane], convert_data(year));
      }
      graphs[result_pane].updateLabel(result_id);
    }
    update_panes();
  }
}

// Initialize visualization.
let init_year = years[Math.floor(years.length / 2)];
select_year(init_year, false);

// Raw Data Show/Hide
$("#show-data").on("click", function(d) {
  if ($("#raw-data").hasClass("hidden")) {
    $(this).text("Hide Raw Data");
    $("#raw-data").removeClass("hidden");
  } else {
    $(this).text("Show Raw Data");
    $("#raw-data").addClass("hidden");
  }
});
