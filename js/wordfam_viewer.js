var fileName = localStorage.getItem('fileName');
var task_results = {};
// The graph viewer supports multi-visualizations (e.g. view multiple analysis results at once).
// To use this feature, simply add entries to the task_results dict.
task_results[fileName] = [
  JSON.parse(localStorage.getItem('fcms')),
  JSON.parse(localStorage.getItem('word_freqs')),
  JSON.parse(localStorage.getItem('word_families'))];

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
  // assert(Object.keys(task_results).length == 1)
  var id = Object.keys(task_results)[0];
  return convert_data_by_id(id, year);
}

var convert_data_by_id = function(id, year) {
  let raw_data = task_results[id]
  var adj_matrix = raw_data[0][year];
  var node_set = new Set();
  var links = [];

  var link_val_threshold = 0;

  for (var node in adj_matrix) {
    node_set.add(node);
    for (var adj_node in adj_matrix[node]) {
      node_set.add(adj_node);

      let weight = adj_matrix[node][adj_node];
      if (weight <= link_val_threshold) continue;
      // All edges are recorded twice, so avoid double counting.
      if (adj_node < node) continue;

      links.push({
        "source": node,
        "target": adj_node,
        "value": weight
      });     
    }
  }

  // Convert text labels of node groups to numbers for 
  // coloring purposes.
  var node_groups = {}
  for (var group in raw_data[2]) {
    for (var j = 0; j < raw_data[2][group].length; j++) {
      node_groups[raw_data[2][group][j]] = group;
    }
  }

  var nodes = [];
  node_set.forEach(function(element) {
    nodes.push({
      "id": element,
      "group": node_groups[element],
      "value": raw_data[1][year][element]
    });
  });

  let result = {"nodes": nodes, "links": links, "metadata": {}};

  // Has metadata.
  if (raw_data.length > 3) {
    result["metadata"] = raw_data[3];
  }
  return result;
}

if (!is_multi_result()) {
  $("#task-info").text(Object.keys(task_results)[0]);
}