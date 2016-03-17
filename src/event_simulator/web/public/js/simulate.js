var width = 960,
    height = 500

var tree = d3.layout.tree()
        //.size([width-100, height-100])
        .nodeSize([120, 120])
        ;

var svg = d3.select("body").append("svg")
        .attr("width", width)
        .attr("height", height)
        ;

enableScrollAndZoom(svg, width, height, 0, 100);

d3.json("/public/data/tree.json", function(error, json) {
    if (error) throw error;

    var nodes = tree.nodes(json);
    var links = tree.links(nodes);
    var diagonal = d3.svg.diagonal();

    var node = svg.selectAll(".node")
        .data(nodes) //nodesの数分gを作る。
        .enter()
        .append("g")
        .attr("class","node")
        .attr("transform", function(d){ return "translate("+ d.x + "," + d.y + ")";})
        ; //ノードの場所まで移動

    node.on('click', function(d, i) {
        console.log([d,i]);
    });

    node.append("circle")
        .attr("r", 60)
        .attr("fill","steelblue");

    node.append("text")
        .text(function(d) { return d.name})
        .attr("x", 5);

    //linksで作ったsource、targetでdiagonal曲線を作る。
    svg.selectAll(".link")
        .data(links)
        .enter()
        .append("path")
        .attr("class","link")
        .attr("fill", "none")
        .attr("stroke", "red")
        .attr("d",diagonal);
});

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
