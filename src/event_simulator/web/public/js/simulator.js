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
        var lineStep = 15;
        var percentFormat = d3.format(".1%");

        //
        //  Target Rate が Parent より上がれば 緑、下がれば、赤
        //  Transition Rate が高いほど太い
        //
        link.attr("fill", "none")
            .attr("stroke-width", function(d) {
                if (d.source.result) {
                    var tr = d.source.result.getTransitionRate(d.target.event);
                    return 20 * tr;
                } else {
                    return 1;
                }
            })
            .attr("stroke", function(d) {
                if (d.source.result) {
                    var sr = d.source.result;
                    var tr = sr.getTargetTransitionRate(d.target.event);
                    var ntr = sr.getNotTargetTransitionRate(d.target.event);
                    return d3.rgb(Math.log(ntr/tr)*10+127, Math.log(tr/ntr)*10+127, 20);
                } else {
                    return "#ccc";
                }
            })
        ;

        //                     Transition Rate(%)
        //  OnTarget TransitionRate(%) | OnNotTarget TransitionRate(%)
        //  ----------------------------------------------------------
        //  |                         Name                           |
        //  |                     Target Rate(%)                     |
        //  |---------------------------------------------------------
        //

        node.append("rect")
            .attr("x", -rectWidth/2)
            .attr("width", rectWidth)
            .attr("height", rectHeight)
            .attr("fill", function(d) {
                if (d.result && d.parent) {
                    var greenRate = d.result.targetCount / (d.parent.result.targetCount + d.result.targetCount);
                    return d3.rgb((1-greenRate)*255, greenRate*255, 20);
                } else {
                    return "#ccc";
                }
            })
            .append("title")
            .text(function(d) { return d.name})
            ;

        node.append("text")  // label name
            .text(function(d) { return _.last(d.name.split(/[.:=]/))})
            // .attr("x", (-rectWidth/2) + 20)
            .attr("y", lineStep)
            .style("text-anchor", "middle")
            ;

        node.append("text")  // Rate To Target
            .text(function(d) {
                if (d.result) {
                    return "Target: " + percentFormat(d.result.targetRate);
                } else {
                    return "";
                }
            })
            .attr("y", lineStep * 2)
            .style("text-anchor", "middle");

        node.append("text")  // Transition Rate from Parent
            .text(function(d) {
                if (d.parent && d.parent.result) {
                    return percentFormat(d.parent.result.getTransitionRate(d.event));
                }
            })
            .attr("y", -lineStep -3)
            .style("text-anchor", "middle");

        node.append("text")  // OnTarget|OnNotTarget Transition Rate from Parent
            .text(function(d) {
                if (d.parent && d.parent.result) {
                    var parentResult = d.parent.result;
                    return percentFormat(parentResult.getTargetTransitionRate(d.event)) + "|" +
                        percentFormat(parentResult.getNotTargetTransitionRate(d.event));
                }
            })
            .attr("y", -3)
            .style("text-anchor", "middle");

        node.on('click', onClickNode);
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
            d.result = SimulationResult(json, targetEvent);
            var nextHash = d.result.data.next_hash;
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
                    event: event,
                    parent: d,
                    seq: seq
                };
                d.children.push(newNode);
            });
            treeView.draw(root, callback);
        });
    }

    function getTargetEvent() { return "activities.shopping_complete"; }
//    function getTargetCount(d) {return d.result.count_hash[getTargetEvent()];}
//    function getParentTargetCount(d) {return getTargetCount(d.parent);}
}

function SimulationResult(data, targetEvent) {
    var self = {};
    self.data = data;
    self.targetEvent = targetEvent;

    self.targetCount = data.count_hash[targetEvent];
    self.targetRate = self.targetCount / data.n;

    self.getTransitionRate = function(event) {
        return data.next_hash[event] / data.n;
    }
    self.getTargetTransitionRate = function(event) {
        return data.target_next_hash[targetEvent][event] / self.targetCount;
    }
    self.getNotTargetTransitionRate = function(event) {
        return data.not_target_next_hash[targetEvent][event] / (data.n - self.targetCount);
    }
    return self;
}

/*
var req = {init_sequence: ["_new_"], target_event: "activities.shopping_complete"};
d3.json('/api/simulate')
.header("Content-Type", "application/json")
.post(JSON.stringify(req), function(err, json) {
    console.log(json);
});
*/
