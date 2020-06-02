//http://bl.ocks.org/heybignick/3faf257bbbbc7743bb72310d03b86ee8
//http://bl.ocks.org/mbostock/1129492
//https://observablehq.com/@d3/disjoint-force-directed-graph
var fileName = localStorage.getItem('fileName');
var task_results = {};
task_results[fileName] = [JSON.parse(localStorage.getItem('word_freqs'))];

$("#raw-data").text(JSON.stringify(task_results[fileName]));

var is_multi_result = function() {
  if (Object.keys(task_results).length > 1) return true;
  return false;
}

var get_data_years = function() {
  var years = new Set();
  Object.keys(task_results).forEach(function(id) {
    Object.keys(task_results[id][0]).forEach(function(year) {
      years.add(parseInt(year));
    });
  });
  years = Array.from(years);
  years.sort();
  return years;
}

var convert_data = function(year) {
  let id = Object.keys(task_results)[0];
  return convert_data_by_id(id, year);
}

var convert_data_by_id = function(id, year) {
  var raw_data = task_results[id];
  var node_set = new Set([]);
  var links = [];
  raw_data[0][year].forEach(function(element) {
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
      "group": 1,
      "value": 1
    });
  });
  
  var result = {"nodes": nodes, "links": links, "metadata": {}};
  if (raw_data.length > 1)
    result["metadata"] = raw_data[1];
  return result;
}

if (!is_multi_result()) {
  $("#task-info").text(Object.keys(task_results)[0]);
}