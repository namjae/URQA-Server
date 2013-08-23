var func = null;
jQuery.fn.styleReady = function(fn) { func = fn; }

var compileProcessCount = 0;
jQuery.fn.compileCSS = function(cssPath, cssFile, varFiles, complate)
{
	var css;
	var filter = /[{}\s\t:;]+/gi;
	var invFilter = /[^{}\s\t:;]+/gi;
	var commaFilter = /[^,]+/gi;
	var variables = new HashMap();

	if(this.length == 0) return;
	compileProcessCount ++;

	function errorLog(error, description)
	{
		console.log(description + " : \"" + error + "\"");
	}

	function complateLoad()
	{
		var depth = 0, depthCount = 0, depthLevelCount = 0;
		var depthTree = new Array();
		var isDepthEnd = new Array();
		var depthNameTree = new Array();
		var depthLevelTree = new Array();
		var depthChildType = new Array();
		var depthLevelUse = new Array();
		var depthString = "";
		var depthLevelString = "";
		var match = css.match(/[@{};:]+/gi);
		var split = css.split(/[@{};:]+/gi);

		addStep = function(i)
		{
			depth ++;
			var temp1, temp2 = "";
			var name = split[i].replace(/\/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+\//,"").split(/[;]+/gi);
			if(name[name.length - 1].match(invFilter) )
			{
				temp1 = name[name.length - 1].split(invFilter);
				name = name[name.length - 1].match(invFilter);
				for(var j = 1; j < temp1.length - 1; j ++)
					temp2 += name[j - 1] + temp1[j];

				name = temp2 + name[name.length - 1];
				temp2 = name;
				if(name.charAt(0) == ">") name = name.substring(1);
					
				depthNameTree[depth - 1] = name;
				isDepthEnd[depth - 1] = false;
				if(match[i-1] != "@")
				{
					depthChildType[depthLevelCount] = 1;
					if(temp2.charAt(0) == ">")
						depthChildType[depthLevelCount] = 2
					
					depthLevelTree[depthLevelCount] = name;	
					depthLevelUse[depthLevelCount ++] = 0;
					
					if(depthLevelUse[depthLevelCount - 2] == 0)
					{
						isDepthEnd[depth - 2] = true;
						split[i] = "}" + split[i];
					}
					
					depthLevelString = "";
					for(var j = 0; j < depthLevelCount - 1; j ++)
					{
						depthLevelUse[j] ++;
						depthLevelString += depthLevelTree[j];
						if(depthChildType[j] == 1) depthLevelString += " ";
						if(depthChildType[j] == 2) depthLevelString += " > ";
					}
					temp2 = temp2.match(commaFilter);
					name = name.match(commaFilter);
					for(var j = 0; j < name.length; j ++)
						split[i] = split[i].replace(temp2[j], depthLevelString + name[j]);
				}
				
				if(depth > 1)
				{
					if(match[i-1] == "@")
					{
						match[i-1] = "";
						depthTree[depthCount ++] = name;
					}
					depthString = ""
					for(var j = 0; j < depthCount; j ++)
						depthString += depthTree[j] + "-";
				}
			}
			else
			{
				depthNameTree[depth - 1] = "-1";
			}
		}
		backStep = function(i)
		{
			if(depthNameTree[depth - 1] == depthLevelTree[depthLevelCount - 1])
			{
				if(depthLevelUse[depthLevelCount - 1] > 1)
					match[i] = "";
				depthLevelTree[-- depthLevelCount] = null;
			}
				
			if(depth > 1)
			{
				if(depthNameTree[depth - 1] == depthTree[depthCount-1])
					depthTree[-- depthCount] = null;

				depthString = ""
				for(var j = 0; j < depthCount; j ++)
					depthString += depthTree[j] + "-";
			}
			
			depthNameTree[-- depth] = null;
			if(depth < 0)
				errorLog(match[i] + split[i+1], "'{' and '}' is not a match");
		}
		
		groupProcess = function(i)
		{
			var name, temp;
			if(match[i + 1] == "{" || match[i + 1] == ":")
			{
				split[i + 1] = split[i] +  match[i] + split[i + 1];
				match[i] = split[i] = "";
			}
			else
			{
				if(depth > 1)
				{
					for(var j = depthCount - 1; j >= 0; j --)
					{
						name = split[i].match(invFilter)[0];
						if(depthTree[j] != "multi-platform")
							split[i] = split[i].replace(new RegExp(name, "gi"), depthTree[j] + "-" + name);
						else
						{
							temp = "";
							for(var k = i; match[k] != ";"; k ++)
							{
								if(match[k] == "@")
									atProcess(k);
								if(k == i)
									temp += split[k + 1];
								else
									temp += match[k] + split[k + 1];
								split[k+1] = "";
							}
							i = k - 1;
							split[i + 1] = temp;
							if(name == "opacity")
							{
								split[i + 1] += "; " + "-khtml-" + name + ":" + temp;
								split[i + 1] += "; " + "filter: alpha(" + name + "=" + eval(temp+"*100") + ")";
								split[i + 1] += "; " + "-ms-filter: \"progid:DXImageTransform.Microsoft.Alpha(" + name + "=" + eval(temp+"*100") + ")\"";
							}
							split[i + 1] += "; " + "-moz-" + name + ":" + temp;
							split[i + 1] += "; " + "-webkit-" + name + ":" + temp;
							split[i + 1] += "; " + "-ms-" + name + ":" + temp;
							split[i + 1] += "; " + "-o-" + name + ":" + temp;
						}
					}
				}
			}
			return i;
		}
		
		atProcess = function(i)
		{
			var name1, name2, temp1, temp2, counter;
			if(split[i+1].charAt(0) == "(")
			{
				if(/[)]/gi.test(split[i+1]))
				{
					name1 = split[i+1].split(/[()]/gi);
					name2 = split[i+1].match(/[()]/gi);

					counter = 0;
					temp1 = "";
					temp2 = "";
					for(var j = 0; j < name2.length; j ++)
					{
						if(name2[j] == "(")
							counter ++;
						else
						{
							counter --;
							if(counter < 0)
							{
								errorLog(match[i] + split[i+1], "'(' and ')' is not a match");
								break;
							}
						}
						if(counter == 0)
						{
							if(temp2 == "")
							{
								temp1 += name2[j];
								temp2 += name1[j+1];
							}
							else
								temp2 += name2[j] + name1[j+1];
						}
						else
							temp1 += name2[j] + name1[j+1];
					}

					name1 = temp1.match(/[A-Za-z0-9-_]+/gi);
					for(var j = 0; j < name1.length; j ++)
					{
						if(variables.get(name1[j]) )
							temp1 = temp1.replace(new RegExp(name1[j], "gi"), variables.get(name1[j]));
					}
					var unit = "";
					if(/%/gi.test(temp1) ) unit = "%";
					if(/in/gi.test(temp1) ) unit = "in";
					if(/cm/gi.test(temp1) ) unit = "cm";
					if(/mm/gi.test(temp1) ) unit = "mm";
					if(/em/gi.test(temp1) ) unit = "em";
					if(/ex/gi.test(temp1) ) unit = "ex";
					if(/pt/gi.test(temp1) ) unit = "pt";
					if(/pc/gi.test(temp1) ) unit = "pc";
					if(/px/gi.test(temp1) ) unit = "px";
					temp1 = temp1
						.replace(/%/gi, "")
						.replace(/in/gi, "")
						.replace(/cm/gi, "")
						.replace(/mm/gi, "")
						.replace(/em/gi, "")
						.replace(/ex/gi, "")
						.replace(/pt/gi, "")
						.replace(/pc/gi, "")
						.replace(/px/gi, "");
					
					try
					{
						split[i+1] = eval(temp1) + unit + temp2;
						match[i] = "";
					}
					catch (e)
					{
						errorLog(match[i] + split[i+1], e.description);
					}
				}
				else
				{
					errorLog(match[i] + split[i+1], "')' does not exist");
				}
			}
			else
			{
				name1 = split[i+1].split(/[\s;]+/gi)[0];
				if(variables.get(name1) )
				{
					match[i] = "";
					split[i+1] = split[i+1].replace(new RegExp(name1, "gi"), variables.get(name1) );
				}
				else
				{
					if(name1 == "variables")
					{
						name2 = split[i + 2];
						addStep(i);
						for(j = i + 3; j < split.length; j ++)
						{
							if(match[j-1] == "{")
							{
								addStep(i);
								name2 += split[j];
								match[j - 1] = split[j] = "";
								errorLog(match[i] + split[i+1], "Nested braces were used.");
							}
							else if(match[j-1] == "}")
							{
								backStep(i);
								match[j - 1] = "";
								if(depth == 0)
								    break;
							}
							else
							{
								name2 += match[j-1] + split[j];
								match[j - 1] = split[j] = "";
							}
						}
						match[i] = split[i + 1] = match[i + 1] = split[i + 2] = "";
						loadedVariableFile(name2.match(invFilter) );
						i = j - 1;
					}
				}
			}
			return i;
		}

		if(match)
		{
			for(var i = 0; i < match.length; i ++)
			{
				switch(match[i])
				{
					case ":":
						i = groupProcess(i);
						break;

					case "@":
						i = atProcess(i);
						break;

					case "{":
						var cnt = depthCount;
						addStep(i);
						if(cnt != depthCount)
						{
							split[i] = "";
							match[i] = "";
						}
						break;

					case "}":
						var cnt = depthCount;
						backStep(i);
						if(cnt != depthCount || isDepthEnd[depth] == true)
							match[i] = "";
						break;
				}
			}
		}

		css = "";
		for(i = 0; i < match.length; i ++)
			css += match[i] + split[i+1];

		$("head").append("<style>");
		$("head").children(":last")
			.attr({ type: "text/css" })
			.html(css);

		if(complate) complate();
		if(-- compileProcessCount == 0) if(func) func();
	}

	function loadedVariableFile(color)
	{
		var data = null;
		if(color.constructor == Array)
			data = color;
		else
			data = color.split(filter);

		if(data)
		{
			for(var i = 1; i < data.length; i += 2)
				variables.put(data[i-1], data[i]);
		}

		index ++;
		if(index == varFiles.length)
			complateLoad();
	}

	$.get(cssPath + cssFile, function(data)
	{
		css = data;

		index = 0;
		for(var file = 0; file < varFiles.length; file ++)
			$.get(cssPath + varFiles[file], loadedVariableFile);
	});
}