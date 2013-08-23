Raphael.fn.drawGrid = function (x, y, w, h, wv, hv, color) {
	color = color || "#000";
	//var path = ["M", Math.round(x) + .5, Math.round(y) + .5, "L", Math.round(x + w) + .5, Math.round(y) + .5, Math.round(x + w) + .5, Math.round(y + h) + .5, Math.round(x) + .5, Math.round(y + h) + .5, Math.round(x) + .5, Math.round(y) + .5],
	var    rowHeight = h / hv,
		columnWidth = w / wv;
	var path = ["M", Math.round(x) + .5, Math.round(y + h) + .5, "H", Math.round(x + w) + .5];
	for (var i = 1; i < hv; i++) {
		path = path.concat(["M", Math.round(x) + .5, Math.round(y + i * rowHeight) + .5, "H", Math.round(x + w) + .5]);
	}
	for (i = 1; i < wv; i++) {
		path = path.concat(["M", Math.round(x + i * columnWidth) + .5, Math.round(y) + .5, "V", Math.round(y + h) + .5]);
	}
	return this.path(path.join(",")).attr({stroke: color});
};

Raphael.custom = [];
Raphael.custom.obj = null;
Raphael.custom.stack = [];
Raphael.custom.stack.leng = 0;
Raphael.custom.stack.push = function(item) {
	this[this.leng] = item;
	return this.leng ++;
}
Raphael.custom.stack.remove = function(index) {
	for(var i = index + 1; i < this.leng; i ++)
		this[i - 1] = this[i];
	this[-- this.leng] = null;
}
Raphael.custom.changeKeyText = function(key) { return key; }
Raphael.custom.changeValueText = function(value) { return value; }
Raphael.custom.checkAB = function(att, A, B) {
	return eval("(att)?((att." + A + "!=null)?(att." + A + "):(" + B + ")):(" + B + ")")
}
Raphael.custom.getAnchors = function(p1x, p1y, p2x, p2y, p3x, p3y) {
	var l1 = (p2x - p1x) / 2,
		l2 = (p3x - p2x) / 2,
		a = Math.atan((p2x - p1x) / Math.abs(p2y - p1y)),
		b = Math.atan((p3x - p2x) / Math.abs(p2y - p3y));
	a = p1y < p2y ? Math.PI - a : a;
	b = p3y < p2y ? Math.PI - b : b;
	var alpha = Math.PI / 2 - ((a + b) % (Math.PI * 2)) / 2,
		dx1 = l1 * Math.sin(alpha + a),
		dy1 = l1 * Math.cos(alpha + a),
		dx2 = l2 * Math.sin(alpha + b),
		dy2 = l2 * Math.cos(alpha + b);
	return {
		x1: p2x - dx1,
		y1: p2y + dy1,
		x2: p2x + dx2,
		y2: p2y + dy2
	};
}
Raphael.custom.addRefresh = function(objName, fn, info) {
	if($(objName) && fn && info)
		return this.stack.push({"objectName": objName, "update": fn, "info": info, "data": null});
	return null;
}
Raphael.custom.windowResize = function() {
	var info, w, h;
    var doneResizing = function()
    {
		for(var i = 0; i < Raphael.custom.stack.leng; i ++)
		{
			info = JSON.parse(JSON.stringify(Raphael.custom.stack[i].info));
			if(info.autoResize != true) continue;
			w = $(Raphael.custom.stack[i].objectName).width();
			h = $(Raphael.custom.stack[i].objectName).height();
			if(w != info.width || h != info.height)
			{
				info.width = w;
				info.height = h;
				Raphael.custom.stack[i].update(Raphael.custom.stack[i].objectName, Raphael.custom.stack[i].data, info);
			}
		}
	}

	clearTimeout(this.id);
	this.id = setTimeout(doneResizing, 100);
}
Raphael.custom.dataLoad = function(jsondata, index) {
	//$.get(file, function(data)
	//{
		Raphael.custom.stack[index].data = jsondata;
		Raphael.custom.stack[index].update(Raphael.custom.stack[index].objectName, jsondata, Raphael.custom.stack[index].info);
	//});
}
Raphael.custom.pieGraph = function(file, objName, att)
{
	function update(objName, realData, att)
	{
		obj = $(objName);

		var info = [];
		info.width					= Raphael.custom.checkAB(att, "width", "obj.width()");
		info.height 				= Raphael.custom.checkAB(att, "height", "obj.height()");
		info.radius					= Raphael.custom.checkAB(att, "radius", "(obj.width() > obj.height() ? obj.height() : obj.width() ) / 2.5");
		info.labelPos				= Raphael.custom.checkAB(att, "labelPos", "null");
		info.lineWidth				= Raphael.custom.checkAB(att, "lineWidth", "3");
		info.leftgutter 			= Raphael.custom.checkAB(att, "leftgutter", "10");
		info.bottomgutter 			= Raphael.custom.checkAB(att, "bottomgutter", "10");
		info.topgutter 				= Raphael.custom.checkAB(att, "topgutter", "10");
		info.horizonLine 			= Raphael.custom.checkAB(att, "horizonLine", "true");
		info.verticalLine 			= Raphael.custom.checkAB(att, "verticalLine", "true");
		info.colorTable				= Raphael.custom.checkAB(att, "colorTable", null);
		info.lineColor 				= Raphael.custom.checkAB(att, "lineColor", "\"#fff\" ");
		info.textColor				= Raphael.custom.checkAB(att, "textColor", "\"#000\" ");
		info.autoResize				= Raphael.custom.checkAB(att, "autoResize", "true");

		obj.html("");

		// Grab the data
		var labels = [],
			data = [];

		var response = $.parseJSON(realData);
		var tags = response.tags;
		for(var i = 0; i < tags.length; i ++)
		{
			labels.push(tags[i].key);
			data.push(tags[i].value);
		}

		var r = Raphael(objName.substring(1), info.width, info.height);
	    var pie;
	    if(info.labelPos == "" || info.labelPos == null)
	    	pie = r.piechart((info.width - info.leftgutter) / 2 + info.leftgutter, (info.height - info.bottomgutter) / 2 + info.topgutter, info.radius, data);
	    else
	    	pie = r.piechart((info.width - info.leftgutter) / 3 + info.leftgutter, (info.height - info.bottomgutter) / 2 + info.topgutter, info.radius, data, { legend: labels, legendpos: info.labelPos });

	    var tObj = obj.children("svg").children();
	    for(i = 0; i < tags.length; i ++)
	    {
	    	tObj.eq(2 + i).attr("stroke", info.lineColor);
	    	pie.series[i].attr("fill", info.colorTable[i % info.colorTable.length]);
	    	pie.covers[i].label[0].attr("fill", pie.series[i].attr("fill"));
	    	pie.covers[i].label[0].attr("cy", pie.covers[i].label[0].attr("cy") + 4 * (i - tags.length / 2) );
	    	pie.covers[i].label[1].attr("y", pie.covers[i].label[1].attr("y") + 4 * (i - tags.length / 2) );
	    	pie.covers[i].label[1].attr("font-size", "13px");
	    }

	    pie.hover(function () {
	        this.sector.stop();
	        this.sector.scale(1.1, 1.1, this.cx, this.cy);

	        if (this.label) {
	            this.label[0].stop();
	            this.label[0].attr({ r: 7.5 });
	            if(this.label[1]) this.label[1].attr({ "font-weight": 800 });
	        }
	    }, function () {
	        this.sector.animate({ transform: 's1 1 ' + this.cx + ' ' + this.cy }, 500, "bounce");

	        if (this.label) {
	            this.label[0].animate({ r: 5 }, 500, "bounce");
	            if(this.label[1]) this.label[1].attr({ "font-weight": 400 });
	        }
	    });

	    $(objName + "> svg").css("position", "static");
	}

	var index = this.addRefresh(objName, update, att);
	if(index == null) return null;

	this.dataLoad(file, index);
	return index;
}
Raphael.custom.areaGraph = function(file, objName, att)
{
	function update(objName, realData, att)
	{
		obj = $(objName);

		var info = [];
		info.width					= Raphael.custom.checkAB(att, "width", "obj.width()");
		info.height 				= Raphael.custom.checkAB(att, "height", "obj.height()");
		info.lineWidth				= Raphael.custom.checkAB(att, "lineWidth", "3");
		info.leftgutter 			= Raphael.custom.checkAB(att, "leftgutter", "30");
		info.bottomgutter 			= Raphael.custom.checkAB(att, "bottomgutter", "20");
		info.topgutter 				= Raphael.custom.checkAB(att, "topgutter", "20");
		info.horizonLine 			= Raphael.custom.checkAB(att, "horizonLine", "true");
		info.verticalLine 			= Raphael.custom.checkAB(att, "verticalLine", "true");
		info.color 					= Raphael.custom.checkAB(att, "color", "\"hsl(\" + [.6, .5, .5] + \")\" ");
		info.lineColor 				= Raphael.custom.checkAB(att, "lineColor", "\"#000\" ");
		info.textColor				= Raphael.custom.checkAB(att, "textColor", "\"#fff\" ");
		info.tooltip				= Raphael.custom.checkAB(att, "tooltip", "true");
		info.tooltipStyle			= Raphael.custom.checkAB(att, "tooltipStyle", "{fill: \"#000\", stroke: \"#666\", \"stroke-width\": 2, \"fill-opacity\": .7}");
		info.tooltipKeyText			= Raphael.custom.checkAB(att, "tooltipKeyText", "this.changeKeyText");
		info.tooltipValueText		= Raphael.custom.checkAB(att, "tooltipValueText", "this.changeValueText");
		info.autoResize				= Raphael.custom.checkAB(att, "autoResize", "true");

		obj.html("");

		// Grab the data
		var labels = [],
			data = [];

		var response = $.parseJSON(realData);
        var tags = response.tags;
		for(var i = 0; i < tags.length; i ++)
		{
			labels.push(tags[i].key);
			data.push(tags[i].value);
		}
		
		// Draw
		var width = info.width,
			height = info.height,
			leftgutter = info.leftgutter,
			bottomgutter = info.bottomgutter,
			topgutter = info.topgutter,
			color = info.color;

		var txt = {font: '13px Helvetica, Arial', fill: "#fff"},
			txt1 = {font: '11px Helvetica, Arial', fill: "#fff"},
			txt2 = {font: '12px Helvetica, Arial', fill: "#000"},
			X = (width - leftgutter) / labels.length,
			max = Math.max.apply(Math, data),
			Y = (height - bottomgutter - topgutter) / max;

		var r = Raphael(objName.substring(1), width, height);

		r.drawGrid(leftgutter + X * .5 - .5, topgutter - .5, width - leftgutter - X, height - topgutter - bottomgutter, (info.verticalLine ? 10 : 0), (info.horizonLine ? 5 : 0), info.lineColor);
		
		var path = r.path().attr({stroke: color, "stroke-width": info.lineWidth, "stroke-linejoin": "round"}),
			bgp = r.path().attr({stroke: "none", opacity: .3, fill: color}),
			label = r.set(),
			lx = 0, ly = 0,
			is_label_visible = false,
			leave_timer,
			blanket = r.set();
		
		label.push(r.text(60, 12, info.tooltipValueText(tags.key)).attr(txt));
		label.push(r.text(60, 27, info.tooltipKeyText(tags.value)).attr(txt1).attr({fill: color}));
		label.hide();

		var frame = r.popup(100, 100, label, "right").attr(info.tooltipStyle).hide();
	
		var p, bgpp;
		for (var i = 0, ii = labels.length; i < ii; i++) {
			var y = Math.round(height - bottomgutter - Y * data[i]),
				x = Math.round(leftgutter + X * (i + .5)),
				t = r.text(x, height - 6, labels[i]).attr(txt2).attr({fill: info.textColor}).toBack();
			if (!i) {
				p = ["M", x, y, "C", x, y];
				bgpp = ["M", leftgutter + X * .5, height - bottomgutter, "L", x, y, "C", x, y];
			}
			if (i && i < ii - 1) {
				var Y0 = Math.round(height - bottomgutter - Y * data[i - 1]),
					X0 = Math.round(leftgutter + X * (i - .5)),
					Y2 = Math.round(height - bottomgutter - Y * data[i + 1]),
					X2 = Math.round(leftgutter + X * (i + 1.5));
				var a = Raphael.custom.getAnchors(X0, Y0, x, y, X2, Y2);
				p = p.concat([a.x1, a.y1, x, y, a.x2, a.y2]);
				bgpp = bgpp.concat([a.x1, a.y1, x, y, a.x2, a.y2]);
			}

			var dot = r.circle(x, y, 2).attr({fill: "#333", stroke: color, "stroke-width": 1});
			blanket.push(r.rect(leftgutter + X * i, 0, X, height - bottomgutter).attr({stroke: "none", fill: "#fff", opacity: 0}));
			var rect = blanket[blanket.length - 1];
			(function (x, y, data, lbl, txt, dot) {
				var timer, i = 0;
				rect.hover(function () {
					clearTimeout(leave_timer);
					var side = "right";
					if (x + frame.getBBox().width > width) {
						side = "left";
					}
					var ppp = r.popup(x, (y<25)?25:y, label, side, 1),
						anim = Raphael.animation({
							path: ppp.path,
							transform: ["t", ppp.dx, ppp.dy]
						}, 200 * is_label_visible);
					lx = label[0].transform()[0][1] + ppp.dx;
					ly = label[0].transform()[0][2] + ppp.dy;
					frame.show().stop().animate(anim);
					label[0].attr({text: info.tooltipValueText(data) }).show().stop().animateWith(frame, anim, {transform: ["t", lx, ly]}, 200 * is_label_visible);
					label[1].attr({text: info.tooltipKeyText(lbl) }).show().stop().animateWith(frame, anim, {transform: ["t", lx, ly]}, 200 * is_label_visible);
					dot.stop().animateWith(frame, anim, {opacity: 1.0}, 200 * is_label_visible);
					dot.attr("r", 4);
					txt.attr("font-weight", 800);
					is_label_visible = true;
				}, function () {
					dot.attr("r", 2);
					txt.attr("font-weight", 500);
					dot.stop().attr("opacity", 0.0);
					leave_timer = setTimeout(function () {
						frame.hide();
						label[0].hide();
						label[1].hide();
						is_label_visible = false;
					}, 1);
				});
			})(x, y, data[i], labels[i], t, dot);
			dot.attr("opacity", 0);
		}
		p = p.concat([x, y, x, y]);
		bgpp = bgpp.concat([x, y, x, y, "L", x, height - bottomgutter, "z"]);
		path.attr({path: p});
		bgp.attr({path: bgpp});
		frame.toFront();
		label[0].toFront();
		label[1].toFront();
		blanket.toFront();

		$(objName + "> svg").css("position", "static");
	}

	var index = this.addRefresh(objName, update, att);
	if(index == null) return null;

	this.dataLoad(file, index);
	return index;
}
Raphael.custom.toString = function() {
	return valueOf();
}
Raphael.custom.valueOf = function() {
	return "[Raphaël object]";
}

addWindowResize(Raphael.custom.windowResize);