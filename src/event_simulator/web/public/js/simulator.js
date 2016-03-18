var Simulator = function(options) {
    var treeView = options.treeView;
    var root = options.root;
    var events = [];

    d3.json('/api/events', function(err, json) {
        events = json.events;
        console.log(json);
    });

    treeView.draw(root);

    var req = {init_sequence: ["_new_"], target_event: "activities.shopping_complete"};
    d3.json('/api/simulate')
    .header("Content-Type", "application/json")
    .post(JSON.stringify(req), function(err, json) {
        console.log(json);
    });
}

