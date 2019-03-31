//http://bl.ocks.org/heybignick/3faf257bbbbc7743bb72310d03b86ee8
//http://bl.ocks.org/mbostock/1129492
//https://observablehq.com/@d3/disjoint-force-directed-graph
/*
var task_results = {"nodes":[{"id":"0","group":1},{"id":"1","group":1},{"id":"2","group":1},{"id":"3","group":1},{"id":"4","group":1},{"id":"100","group":1},{"id":"5","group":1},{"id":"8","group":1},{"id":"7","group":1},{"id":"6","group":1},{"id":"9","group":1},{"id":"10","group":1},{"id":"PINE","group":1},{"id":"STATE","group":1},{"id":"503160","group":1},{"id":"MENTHOL","group":1},{"id":"NON","group":1},{"id":"S","group":1},{"id":"TOB","group":1},{"id":"25","group":1}],
"links":[{"source":"0","target":"1","value":10149},{"source":"0","target":"0","value":6874},{"source":"1","target":"1","value":3997},{"source":"0","target":"2","value":3701},{"source":"1","target":"2","value":3327},{"source":"0","target":"3","value":2042},{"source":"1","target":"3","value":1890},{"source":"0","target":"4","value":1888},{"source":"0","target":"100","value":1806},{"source":"2","target":"3","value":1619},{"source":"0","target":"5","value":1326},{"source":"0","target":"8","value":1292},{"source":"2","target":"2","value":1286},{"source":"1","target":"4","value":1273},{"source":"2","target":"4","value":1209},{"source":"0","target":"7","value":1104},{"source":"0","target":"6","value":1084},{"source":"1","target":"5","value":983},{"source":"3","target":"4","value":974},{"source":"1","target":"6","value":919},{"source":"3","target":"5","value":903},{"source":"1","target":"9","value":889},{"source":"1","target":"7","value":829},{"source":"3","target":"3","value":765},{"source":"2","target":"5","value":754},{"source":"3","target":"6","value":738},{"source":"0","target":"9","value":709},{"source":"3","target":"8","value":707},{"source":"2","target":"6","value":704},{"source":"1","target":"8","value":658},{"source":"2","target":"8","value":644},{"source":"4","target":"5","value":609},{"source":"4","target":"7","value":583},{"source":"2","target":"7","value":579},{"source":"4","target":"8","value":561},{"source":"2","target":"9","value":555},{"source":"5","target":"6","value":546},{"source":"5","target":"9","value":522},{"source":"3","target":"7","value":452},{"source":"0","target":"10","value":446},{"source":"4","target":"4","value":414},{"source":"6","target":"7","value":409},{"source":"3","target":"9","value":392},{"source":"PINE","target":"STATE","value":391},{"source":"503160","target":"PINE","value":380},{"source":"MENTHOL","target":"NON","value":366},{"source":"100","target":"S","value":360},{"source":"STATE","target":"TOB","value":358},{"source":"0","target":"25","value":352},{"source":"5","target":"8","value":347}]};
var data2 = {"nodes":[{"id":"0","group":1,"value":1},{"id":"01","group":1,"value":1},{"id":"12","group":1,"value":1},{"id":"1","group":1,"value":1},{"id":"100","group":1,"value":1},{"id":"Morris","group":1,"value":1},{"id":"Philip","group":1,"value":1},{"id":"D","group":1,"value":1},{"id":"Ph","group":1,"value":1},{"id":"A","group":1,"value":1},{"id":"I","group":1,"value":1},{"id":"2","group":1,"value":1},{"id":"pgNbr","group":1,"value":1},{"id":"BAUER","group":1,"value":1},{"id":"MS","group":1,"value":1},{"id":"STATES","group":1,"value":1},{"id":"UNITED","group":1,"value":1},{"id":"00","group":1,"value":1},{"id":"5","group":1,"value":1},{"id":"1993","group":1,"value":1},{"id":"94","group":1,"value":1},{"id":"BILLS","group":1,"value":1},{"id":"FEDERAL","group":1,"value":1},{"id":"1994","group":1,"value":1},{"id":"REGULATIONS","group":1,"value":1},{"id":"02","group":1,"value":1},{"id":"11","group":1,"value":1},{"id":"AVAILABLE","group":1,"value":1},{"id":"CALL","group":1,"value":1},{"id":"ROLL","group":1,"value":1},{"id":"PROCESSED","group":1,"value":1},{"id":"1995","group":1,"value":1},{"id":"3","group":1,"value":1},{"id":"M","group":1,"value":1},{"id":"think","group":1,"value":1},{"id":"pa","group":1,"value":1},{"id":"Q","group":1,"value":1},{"id":"4","group":1,"value":1},{"id":"al","group":1,"value":1},{"id":"et","group":1,"value":1},{"id":"S","group":1,"value":1},{"id":"U","group":1,"value":1},{"id":"type","group":1,"value":1},{"id":"And","group":1,"value":1},{"id":"low","group":1,"value":1},{"id":"tar","group":1,"value":1},{"id":"Well","group":1,"value":1},{"id":"care","group":1,"value":1},{"id":"health","group":1,"value":1},{"id":"n","group":1,"value":1},{"id":"Senate","group":1,"value":1},{"id":"States","group":1,"value":1},{"id":"United","group":1,"value":1}],"links":[{"source":"0","target":"0","value":340},{"source":"01","target":"12","value":193},{"source":"0","target":"1","value":186},{"source":"0","target":"100","value":167},{"source":"Morris","target":"Philip","value":164},{"source":"D","target":"Ph","value":149},{"source":"A","target":"I","value":142},{"source":"0","target":"2","value":130},{"source":"1","target":"pgNbr","value":128},{"source":"BAUER","target":"MS","value":123},{"source":"STATES","target":"UNITED","value":115},{"source":"0","target":"00","value":113},{"source":"0","target":"5","value":112},{"source":"1993","target":"94","value":111},{"source":"1","target":"1","value":111},{"source":"BILLS","target":"FEDERAL","value":110},{"source":"01","target":"1994","value":110},{"source":"BILLS","target":"REGULATIONS","value":110},{"source":"94","target":"FEDERAL","value":110},{"source":"02","target":"11","value":109},{"source":"AVAILABLE","target":"CALL","value":109},{"source":"0","target":"AVAILABLE","value":109},{"source":"CALL","target":"ROLL","value":109},{"source":"0","target":"PROCESSED","value":109},{"source":"REGULATIONS","target":"UNITED","value":109},{"source":"12","target":"1995","value":109},{"source":"02","target":"PROCESSED","value":108},{"source":"11","target":"1995","value":106},{"source":"0","target":"3","value":106},{"source":"D","target":"M","value":105},{"source":"I","target":"think","value":104},{"source":"A","target":"pa","value":100},{"source":"01","target":"94","value":98},{"source":"1","target":"2","value":95},{"source":"I","target":"I","value":87},{"source":"2","target":"5","value":82},{"source":"Q","target":"pa","value":80},{"source":"0","target":"4","value":77},{"source":"al","target":"et","value":77},{"source":"S","target":"U","value":76},{"source":"I","target":"type","value":76},{"source":"And","target":"Q","value":75},{"source":"low","target":"tar","value":75},{"source":"A","target":"Well","value":74},{"source":"care","target":"health","value":70},{"source":"A","target":"n","value":68},{"source":"94","target":"Senate","value":65},{"source":"States","target":"United","value":64},{"source":"1","target":"3","value":62},{"source":"Q","target":"n","value":62}]};

// Development stuff for static task_results.
var max_value = -1;
for (var i = 0; i < task_results.links.length; i++) {
  max_value = Math.max(max_value, task_results.links[i].value);
}
for (var i = 0; i < task_results["nodes"].length; i++) {
  task_results["nodes"][i]["value"] = Math.random();
}
*/
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
      "group": 1,
      "value": 1
    });
  });
  return {"nodes": nodes, "links": links};
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

  let action_items = diff(old_data.nodes, new_data.nodes, function(d) { return d.id; });
  action_items[0].forEach(function(d) {
    graph.addNode(d);
  });
  action_items[1].forEach(function(d) {
    graph.updateNodeValue(d.id, d.value);
  });
  action_items[2].forEach(function(d) {
    graph.removeNode(d.id);
  });

  action_items = diff(old_data.links, new_data.links, getLinkId);
  action_items[0].forEach(function(d) {
    graph.addLink(d);
  });
  action_items[1].forEach(function(d) {
    graph.updateLinkValue(d);
  });
  action_items[2].forEach(function(d) {
    graph.removeLink(d);
  });
}
/*
var graph = new createGraph(task_results);

setTimeout(function() {
task_results["nodes"].push({"id":"NEW_ADDITION","group":1,"value":Math.random()});
task_results["nodes"].push({"id":"7","group":1,"value":1.0});
task_results["links"].push({"source":"MENTHOL","target":"7","value":1.0});
task_results["links"][10].value = 10149;
task_results["links"].splice(task_results.links.length - 3, 1);
updateGraph(graph, task_results);
}, 2000);*/
//render_chart(task_results);

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
    let year = ui.values[0];
    $("#selected-year").text("Year: " + year);
    updateGraph(graph, convert_data(year));
  },
});

// Initialize graph.
let init_year = $("#year-slider").slider("values")[0];
$("#selected-year").text("Year: " + init_year);
var graph = new createGraph(convert_data(init_year));
