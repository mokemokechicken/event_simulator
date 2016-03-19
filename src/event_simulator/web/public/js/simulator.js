var Simulator = function(options) {
    var treeView = options.treeView;
    var root = options.root;
    var events = [];
    var baseApiUrl = options.baseApiUrl || '/api';

    d3.json(baseApiUrl + '/events', function(err, json) {
        events = json.events;
        console.log(json);
    });

    treeView.draw(root, callback);

    function callback(node, link) {
        node.append("circle")
            .attr("r", 40)
            .attr("fill","steelblue");

        node.append("text")
            .text(function(d) { return d.name})
            .attr("x", 5);

        node.on('click', function(d, i) {
            if (!d.children) {
                d.children = [];
            }

            var req = {init_sequence: d.seq, target_event: "activities.shopping_complete"};
            d3.json(baseApiUrl + '/simulate')
            .header("Content-Type", "application/json")
            .post(JSON.stringify(req), function(err, json) {
                if (err) return console.log(err);
                console.log(json);

            });

//            var id = d.name + '-' + (d.children.length+1);
//            d.children.push({id: id, name: id, parent: d});
//            treeView.draw(root, callback);
        });

        link.attr("fill", "none")
            .attr("stroke", "red");
    }
}

/*
var req = {init_sequence: ["_new_"], target_event: "activities.shopping_complete"};
d3.json('/api/simulate')
.header("Content-Type", "application/json")
.post(JSON.stringify(req), function(err, json) {
    console.log(json);
});
*/
