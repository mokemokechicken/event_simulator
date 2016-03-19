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

        node.on('click', onClickNode);

        link.attr("fill", "none")
            .attr("stroke", "red");
    }

    function onClickNode(d, i) {
        if (!d.children) {
            d.children = [];
        }
        var targetEvent = getTargetEvent();
        var OPEN_RATE = 0.01;

        var req = {init_sequence: d.seq, target_event: targetEvent};
        d3.json(baseApiUrl + '/simulate')
        .header("Content-Type", "application/json")
        .post(JSON.stringify(req), function(err, json) {
            if (err) return console.log(err);
            console.log(json);
            var numSample = json.n;
            d.simulation = json;
            var nextHash = d.simulation.next_hash;
            _(nextHash)
            .toPairs()
            .sortBy(function(o) {return -o[1]})
            .takeWhile(function(o) { return o[1] / numSample > OPEN_RATE})
            .forIn(function(o) {
                var event = o[0];
                var seq = d.seq.concat(event);
                var newNode = {
                    id: seq.join("\t"),
                    name: event,
                    parent: d,
                    seq: seq
                };
                d.children.push(newNode);
            });
            treeView.draw(root, callback);
        });
    }

    function getTargetEvent() { return "activities.shopping_complete"; }
}

/*
var req = {init_sequence: ["_new_"], target_event: "activities.shopping_complete"};
d3.json('/api/simulate')
.header("Content-Type", "application/json")
.post(JSON.stringify(req), function(err, json) {
    console.log(json);
});
*/
