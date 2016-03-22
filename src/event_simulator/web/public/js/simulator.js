var Simulator = function(options) {
    var baseApiUrl = options.baseApiUrl || '/api';
    var treeView = options.treeView;
    var root = options.root;
    var events = [];

    // View Control
    var controlPlace = options.control || "body";
    var selectTag, addButton;
    var selectedNode;
    var sx = treeView.nodeSize[0]
        , sy = treeView.nodeSize[1]
        , rectWidth = sx/8 * 7
        , rectHeight = sy/2
        ;
    var isBusy;
    setBusy(false);

    // load and setup event list
    d3.json(baseApiUrl + '/events', function(err, json) {
        events = _.sortBy(json.events);
        console.log(json);
        addButton = d3.select(controlPlace)
            .append("button")
            .attr("class", "button")
            .text("Add Event")
            .on("click", function() {console.log(selectTag[0][0].selectedOptions[0].value)})
        selectTag = d3.select(controlPlace)
            .append("select")
            .attr("class", "select");
            //.on("change", function(d) {console.log(select[0][0].selectedOptions[0].value)});
        var options = selectTag
            .selectAll('option')
            .data(events).enter()
            .append('option')
            .text(function (d) { return d; });
    });

    treeView.diagonal = function(d) {
        var newSource = {x: d.source.x, y: d.source.y + rectHeight}
        return d3.svg.diagonal()({source: newSource, target: d.target});
    }

    redrew();

    function callback(node, link, nodeEnter, linkEnter) {
        var longPressTimer;
        var lineStep = 15;
        var percentFormat = d3.format(".1%");

        //
        //  Target Rate が Parent より上がれば 緑、下がれば、赤
        //  Transition Rate が高いほど太い
        //
        linkEnter.attr("fill", "none")
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
                    return d3.rgb(Math.log(ntr/tr)*30+127, Math.log(tr/ntr)*30+127, 20);
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

        nodeEnter.append("rect")
            .attr("x", -rectWidth/2)
            .attr("width", rectWidth)
            .attr("height", rectHeight)
            .append("title")
            .text(function(d) { return d.name})
            ;

        node.selectAll("rect")
            .attr("fill", function(d) {
                if (d.result && d.parent) {
                    var greenRate = d.result.targetCount / (d.parent.result.targetCount + d.result.targetCount);
                    return d3.rgb((1-greenRate)*255, greenRate*255, 20);
                } else {
                    return "#ccc";
                }
            });

        /////////// label name //////////////
        nodeEnter.append("text")
            .text(function(d) { return _.last(d.name.split(/[.:=]/))})
            .attr("y", lineStep)
            .style("text-anchor", "middle")
            ;

        ///////// Rate To Target /////////
        nodeEnter.append("text")
            .attr("class", "rate-to-target")
            .attr("y", lineStep * 2)
            .style("text-anchor", "middle");

        node.selectAll(".rate-to-target")
            .text(function(d) {
                if (d.result) {
                    return "Target: " + percentFormat(d.result.targetRate);
                } else {
                    return "";
                }
            })

        // Transition Rate from Parent
        nodeEnter.append("text")
            .text(function(d) {
                if (d.parent && d.parent.result) {
                    return percentFormat(d.parent.result.getTransitionRate(d.event));
                }
            })
            .attr("y", -lineStep -3)
            .style("text-anchor", "middle");

        nodeEnter.append("text")  // OnTarget|OnNotTarget Transition Rate from Parent
            .text(function(d) {
                if (d.parent && d.parent.result) {
                    var parentResult = d.parent.result;
                    return percentFormat(parentResult.getTargetTransitionRate(d.event)) + "|" +
                        percentFormat(parentResult.getNotTargetTransitionRate(d.event));
                }
            })
            .attr("y", -3)
            .style("text-anchor", "middle");

        nodeEnter.on("dblclick", onDoubleClickNode);
        nodeEnter.on("click", onClickNode);
    }

    function onClickNode(d) {
        if (selectedNode) {
            selectedNode.classed("selected", false);
        }
        selectedNode = d;
        selectedNode.classed("selected", true);
    }

    function onDoubleClickNode(d) {
        d3.event.stopPropagation();
        if (isBusy) return;

        // Show/Hide children nodes
        if (!d.children) {
            if (d._children) { // restore from cache
                d.children = d._children;
                delete d._children;
                redrew();
                return;
            } else {
                d.children = [];
            }
        } else {
            d._children = d.children;
            delete d.children;
            redrew();
            return;
        }

        // Simulate Request
        var OPEN_RATE = 0.01;
        setBusy(true);
        var req = {init_sequence: d.seq, target_event: getTargetEvent()};
        d3.json(baseApiUrl + '/simulate')
        .header("Content-Type", "application/json")
        .post(JSON.stringify(req), function(err, json) {
            setBusy(false);
            if (err) return console.log(err);
            console.log(json);
            d.result = SimulationResult(json, getTargetEvent());
            expandChildren(d, OPEN_RATE);
            redrew();
        });
    }

    function expandChildren(d, openRate) {
        _(d.result.data.next_hash)
        .toPairs()
        .sortBy(function(o) {return -o[1]})
        .takeWhile(function(o) { return o[1] / d.result.numSample > openRate})
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
    }

    function redrew() {
        treeView.draw(root, callback);
        setBusy(false);
    }

    function setBusy(flg) {
        isBusy = flg;
        if (isBusy) {
            d3.selectAll(".node").style("cursor", "wait");
        } else {
            d3.selectAll(".node").style("cursor", "pointer");
        }
    }

    function getTargetEvent() { return "activities.shopping_complete"; }
}

function SimulationResult(data, targetEvent) {
    var self = {};
    self.data = data;
    self.numSample = data.n;
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
