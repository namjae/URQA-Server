function supportsSVG() {
	return !!document.createElementNS && !!document.createElementNS('http://www.w3.org/2000/svg', "svg").createSVGRect && !!(window.SVGSVGElement);
}

function addWindowResize(fun)
{
	var oldresize = window.onresize;
	
	window.onresize = function(e) {
		if(typeof oldresize == 'function') oldresize(e);
		fun(e);
	}
	return fun;
}