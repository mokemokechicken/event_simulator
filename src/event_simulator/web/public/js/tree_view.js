//var svgCanvas = SVGCanvas();
//var treeView = TreeView(svgCanvas.svg);

//d3.json("/public/data/tree.json", function(error, json) {
//    if (error) throw error;
//    treeView.draw(json);
//});

(function (window) {
window.SVGCanvas = SVGCanvas;
window.TreeView = TreeView;

function SVGCanvas(options) {
    options = options || {};
    var self = this;
    var width = options.width || 960,
        height = options.height || 500,
        canvas = options.canvas || 'body'
        ;

    self.svg = d3.select(canvas).append("svg")
            .attr("width", width)
            .attr("height", height)
            ;

    enableScrollAndZoom(self.svg, width, height, 0, 100);

    return self;
}

function TreeView(svg, options) {
    var options = options || {};
    var self = this;
    self.nodeSize = options.nodeSize || [120, 120];
    self.diagonal = d3.svg.diagonal();
    var tree = d3.layout.tree()
            //.size([width-100, height-100])
            .nodeSize(self.nodeSize);
    self.draw = function(root, cb) { return drawTree(svg, tree, root, cb, self.diagonal); };
    return self;
}

function drawTree(svg, tree, root, cb, diagonal) {
    cb = cb || dummyCallback;
    var duration = 200;
    var nodes = tree.nodes(root);

    // Update Nodes
    var node = svg.selectAll(".node").data(nodes, nodeId);

    node.enter()  // 新規に追加されたものだけ、こっちに来るようだ
        .append("g")
        .attr("class","node")
        .attr("transform", function(d){
            if (d.parent) {
                return "translate("+ d.parent.x + "," + d.parent.y + ")";
            } else {
                return "translate("+ d.x + "," + d.y + ")";
            }
        });

    node.exit().remove();  // nodeId で特定されているので、削除ができる。

    node.transition()   // 全ての nodes に対する操作
        .duration(duration)
        .attr("transform", function(d){ return "translate("+ d.x + "," + d.y + ")"; });

    // update Links
    var link = svg.selectAll(".link").data(tree.links(nodes), linkId);

    link.enter()
        .append("path")
        .attr("class","link")
        .attr("d", function(d) {
            var o = {x: d.source.x, y: d.source.y};
            return diagonal({source: o, target: o});
        });

    link.exit().remove();

    link.transition()
        .duration(duration)
        .attr("d", diagonal);

    return cb(node, link);

    function dummyCallback(node, link) {
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
            var id = d.name + '-' + (d.children.length+1);
            d.children.push({id: id, name: id, parent: d});
            drawTree(svg, tree, root);
        });

        link.attr("fill", "none")
            .attr("stroke", "red");

    }
}

function enableScrollAndZoom(svg, width, height, centerX, centerY) {
    centerX = centerX || 0;
    centerY = centerY || 0;
	var vbox_x = -width/2 + centerX;
	var vbox_y = -height/2 + centerY;
	var vbox_default_width = vbox_width = width;
	var vbox_default_height = vbox_height = height;
	var scale = 1;

	setViewBox();

	var drag = d3.behavior.drag()
	.on("drag", function(d) {
		vbox_x -= d3.event.dx * scale;
		vbox_y -= d3.event.dy * scale;
		return svg.attr("translate", "" + vbox_x + " " + vbox_y); //基点の調整。svgタグのtranslate属性を更新
	  });
	svg.call(drag);

	var zoom = d3.behavior.zoom().on("zoom", function(d) {
	    scale = d3.event.scale;
		var befere_vbox_width, before_vbox_height, d_x, d_y;
		befere_vbox_width = vbox_width;
		before_vbox_height = vbox_height;
		vbox_width = vbox_default_width * d3.event.scale;
		vbox_height = vbox_default_height * d3.event.scale;
		d_x = (befere_vbox_width - vbox_width) / 2;
		d_y = (before_vbox_height - vbox_height) / 2;
		vbox_x += d_x;
		vbox_y += d_y;
		return setViewBox();
	});
  　svg.call(zoom);

    function setViewBox() {
        return svg.attr("viewBox", "" + vbox_x + " " + vbox_y + " " + vbox_width + " " + vbox_height);
    }
    return svg;
}


function linkId(d) {
  return d.source.id + "-" + d.target.id;
}

function nodeId(d) {
  return d.id;
}

function nodeX(d) {
console.log(d);
  return d.x;
}

function nodeY(d) {
  return d.y;
}

})(window);
