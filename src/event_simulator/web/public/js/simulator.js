var Simulator = function(options) {
    var treeView = options.treeView;
    var root = options.root;
    var events = [];
    var baseApiUrl = options.baseApiUrl || '/api';
    var sx = treeView.nodeSize[0]
        , sy = treeView.nodeSize[1]
        , rectWidth = sx/3 * 2
        , rectHeight = sy/2
        ;

    d3.json(baseApiUrl + '/events', function(err, json) {
        events = json.events;
        console.log(json);
    });

    treeView.diagonal = function(d) {
        var newSource = {x: d.source.x, y: d.source.y + rectHeight}
        return d3.svg.diagonal()({source: newSource, target: d.target});
    }

    treeView.draw(root, callback);

    function callback(node, link) {
        node.append("rect")
            .attr("x", -rectWidth/2)
            .attr("width", rectWidth)
            .attr("height", rectHeight)
            .attr("fill","steelblue")
            .append("title")
            .text(function(d) { return d.name})
            ;

        node.append("text")
            .text(function(d) { return _.last(d.name.split(/[.:=]/))})
            // .attr("x", (-rectWidth/2) + 20)
            .attr("y", 15)
            .style("text-anchor", "middle")
            ;

        node.on('click', onClickNode);

        link.attr("fill", "none")
            .attr("stroke", "red");
    }

    function onClickNode(d, i) {
        if (!d.children) {
            d.children = [];
        }
        var targetEvent = getTargetEvent();
        var OPEN_RATE = 0.05;

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
