for (var i = 0; i < task_results.length; i++)
  task_results[i] = JSON.parse(task_results[i]);

var get_data_years = function() {
  var years = [];
  Object.keys(task_results[0]).forEach(function(year) {
    years.push(parseInt(year));
  });
  return years;
}

var convert_data = function(year) {
  var adj_matrix = task_results[0][year];
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
  for (var group in task_results[2]) {
    for (var j = 0; j < task_results[2][group].length; j++) {
      node_groups[task_results[2][group][j]] = group;
    }
  }

  var nodes = [];
  node_set.forEach(function(element) {
    nodes.push({
      "id": element,
      "group": node_groups[element],
      "value": task_results[1][year][element]
    });
  });
  return {"nodes": nodes, "links": links};
}