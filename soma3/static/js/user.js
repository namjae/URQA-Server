function resizePopupInformation()
{
	var tops = ($(window).height() - $("#popup-information > .body").height()) / 2;
	var lefts = ($(window).width() - $("#popup-information > .body").width()) / 2;
	$("#popup-information > .body").stop(true, true);
	$("#popup-information > .body").animate({'top': tops, 'left': lefts}, 250, function() { $(this).css({'top': tops, 'left': lefts}); } );
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function showPopupInformation(w, h, idinstance)
{
	var oriW = $("#popup-information > .body").width();
	var oriH = $("#popup-information > .body").height();
	if(w)
	{
		var tops = ($(window).height() - h) / 2;
		var lefts = ($(window).width() - w) / 2;
		$("#popup-information > .body").stop(true, true);
		$("#popup-information > .body").animate({
			"top": tops,
			"left": lefts,
			"width": w,
			"height": h
		}, 250, function(){
			$(this).css({"top": tops, "left": lefts, "width": w, "height": h});
		});
	}
	$("body").css("overflow", "hidden");
	$("#popup-information").css("display", "block");

	$("#popup-container").stop(true, true);
	$("#popup-container").css({"display": "block", "opacity": 0.0});
	$("#popup-container").animate({
		opacity: 1.0,
	}, 250, function(){
		$(this).css({"opacity": 1.0});
	});

    //여기서 팝업창 띄울 놈 얻어옴
    getinstancedata(idinstance)
    geteventpath(idinstance)
    getlog(idinstance)

}
//
function getinstancedata(idinstance)
{
    $.ajax({
      type: 'get'
    , url: error_id+'/'+ idinstance
    , beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
            // Send the token to same-origin, relative URLs only.
            // Send the token only if the method warrants CSRF protection
            // Using the CSRFToken value acquired earlier
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }}
    , success : function(data) {
            $('#osversion').text(data['osversion'])
            $('#appversion').text(data['appversion'])
            $('#device').text(data['device'])
            $('#country').text(data['country'])
            $('#freememory').text(data['appmemfree'])
            $('#memoryusage').text(data['appmemtotal'])
            $('#gps').text(data['gpson'] ? 'true' : 'false')
            $('#screenorientation').text(data['scrorientation']? 'vetical': 'horizon')
            $('#bettery').text(data['batterylevel']+ '%')
            $('#wifi').text(data['wifion'] ? 'true' : 'false')
            $('#mobile').text(data['mobileon'] ? 'true' : 'false')
            $('#screensize').text(data['scrwidth'] + ' X ' + data['scrheight'])
            $('#root').text(data['rooted'] ? 'true':'false')
            $('#sdkversion').text(data['sdkversion'])
            $('#locale').text(data['locale'])
            $('#date').text(data['datetime'])
            $('#instanceid').text('#'+data['idinstance'])
        }
    })
}

function geteventpath(idinstance)
{
      $.ajax({
      type: 'get'
    , url: error_id+'/'+ idinstance + '/instanceeventpath'
    , beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
            // Send the token to same-origin, relative URLs only.
            // Send the token only if the method warrants CSRF protection
            // Using the CSRFToken value acquired earlier
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }}
    , success : function(data) {

              //var printstr = sprintf('<tr><td class="center">%s<br>%s</td> <td>%s</td><td>%s</td></tr>',data['date'],data['time'],data['class'],data['methodline'])

              var stringlist = []
              for(var i =0; i< data.length ; i++)
              {
                var stringbuilder = []
                stringbuilder.push('<tr><td class="center">',data[i]['date'],'<br>',data[i]['time'],'</td> <td>',data[i]['class'],'</td><td>',data[i]['methodline'],'</td></tr>')
                stringlist.push(stringbuilder.join(''))
              }
              $('#eventpath').html(stringlist.join(''))
        }
    })
}
function getlog(idinstance)
{
     $.ajax({
      type: 'get'
    , url: error_id+'/'+ idinstance + '/log'
    , beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
            // Send the token to same-origin, relative URLs only.
            // Send the token only if the method warrants CSRF protection
            // Using the CSRFToken value acquired earlier
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }}
    , success : function(data) {
             var stringlist = []

             for(var i = 0 ; i< data.length; i++)
             {
                 var stringbuilder = []
                stringbuilder.push('<tr><td>',i,': ',data[i],'</td></tr>')
                stringlist.push(stringbuilder.join(''))
             }
             $('#log').html(stringlist.join(''))
        }
    })
}

function hidePopupInformation()
{
	$("#popup-container").stop(true, true);
	$("#popup-container").animate({
		opacity: 0.0,
	}, 250, function(){
		$(this).css({"display": "none"});
		$("body").css("overflow", "");
		$("#popup-information").css("display", "none");
	});
}

$(document).ready(function()
{
	$("#container").addClass("container-js");
	if(supportsSVG()) $("#container").addClass("svg");
	if(navigator.userAgent.match(/applewebkit/i))
	{
		if(!navigator.geolocation)
		{
			$("#container").addClass("decelerate");
		}
		else
		{
			if (navigator.platform.match(/ipad/i) ||
				navigator.platform.match(/iphone/i) ||
				navigator.platform.match(/ipod/i) ) $("#container").addClass("ios");
		}
		if (navigator.userAgent.match(/chrome/i) &&
			navigator.userAgent.match(/windows/i) ) $("#container").addClass("noinset");
	}

	var profileCount = 0;
	var timer = null;
	profileShow = function(obj) {
		if(profileCount == 0)
		{
			clearTimeout(timer);
			$("#profile-menu").stop(true, true);
			$("#profile-menu").css({"display": "block", "opacity": 1.0});
			$("#header > .navbar-profile > .profile > img").css("opacity", 0.16);
		}
		profileCount ++;
	};
	profileHide = function() {
		profileCount --;
		if(profileCount == 0)
		{
			$("#profile-menu").stop(true, true);
			$("#profile-menu").css("opacity", 0.0);
			$("#header > .navbar-profile > .profile > img").css("opacity", 1.0);
			timer = setTimeout("$(\"#profile-menu\").css(\"display\", \"none\");", 100);
		}
	};
	$("#header > .navbar-profile > .profile > img").hover(profileShow, profileHide);
	$("#profile-menu").hover(profileShow, profileHide);
});

// Stylesheet is load-complate
$("head").styleReady(function(){
	$("body").css("display", "block");
	
	// Graph rendering
	if($("body").hasClass("insight") )
	{
		$("#dailyES").ready(function(){
			Raphael.custom.areaGraph(server_url + project_id + "/dailyes", "#dailyES", {"lineWidth": 1, "horizonLine": false, "verticalLine": false, "leftgutter": 0, "topgutter": 5,
				"color": "#dca763", "lineColor": "#3a3f42", "textColor": "#303335", "autoResize": true });
		});
		$("#typeES").ready(function(){
			Raphael.custom.pieGraph(server_url + project_id + "/typees", "#typeES", {"lineWidth": 1, "horizonLine": false, "verticalLine": false, "leftgutter": 0, "topgutter": 5,
				"lineColor": "#ffffff", "textColor": "#303335", "labelPos": "east", "colorTable": [ "#de6363", "#5a9ccc", "#72c380", "#cccdc7", "#9d61dd", "#6371dc", "#dca763", "#a96f6e", "#6fa79a", "#737270" ], "autoResize": true });
		});
	}
	if($("body").hasClass("error") )
	{
		$("#event-path-parent").ready(function(){
			//Raphael.custom.eventPath("./data3", "#event-path", {"height": 230, "contentWidth": 20, "contentHeight": 20, "textColor": "#303335", "colorTable": [ "#de6363", "#5a9ccc", "#72c380", "#cccdc7", "#9d61dd", "#6371dc", "#dca763", "#a96f6e", "#6fa79a", "#737270" ], "autoResize": true, "topgutter": 5, "bottomgutter": -10 })
		});
	}

	/** Component Start **/
	// Dropdown(multiple select) component
	$(".dropdown.multiple").ready(function(){
		$(".dropdown.multiple").each(function(){
			var me = $(this);
			var chd = me.children("a");
			var name = chd.html();
			var codename = me.children("input").attr("name");

			chd.html("<div></div>");
			chd = chd.children("div");
			chd.addClass("checkbox").addClass("half");
			chd.html("<span></span><label>" + name + "</label>");

			chd = me.children("span");

			me.children("div").children("ul").children("li").each(function(){
				var chd2;
				var name2 = $(this).children("a").html();

				$(this).html("<div></div>");
				chd2 = $(this).children("div");
				chd2.addClass("checkbox");
				chd2.html("<span></span><label>" + name2 + "</label><input type=\"hidden\" name=\"" + codename + "[]\" data-group=\"" + name + "\" data-value=\"" + name2 + "\" />");
			});
			me.children("input").remove();
		});
	});

	// Radiobox component
	$(".radiobox").ready(function()
	{
		// Initialize
		var radiobox_objects = $(".radiobox");
		for(var i = 0; i < radiobox_objects.length; i ++)
		{
			var me = radiobox_objects.eq(i);
			me.attr("data-name", me.children("input").attr("name") );
			me.attr("data-value", me.children("input").attr("value") );

			var group_info = $(".radiobox[data-name=" + me.attr("data-name") + "]");
			if(group_info.length > 1) me.children("input").remove();

			if($(this).children("span").attr("data-value") == "checked")
				group_info.eq(0).children("input").attr("value", me.attr("data-value") );
		}

		// Click event
		$(".radiobox").click(function(){
			var group_info = $(".radiobox[data-name=" + $(this).attr("data-name") + "]");
			group_info.children("span[data-value=checked]").attr("data-value", "");
			group_info.eq(0).children("input").attr("value", $(this).attr("data-value") );
			$(this).children("span").attr("data-value", "checked");
		});
	});

	// Checkbox component
	$(".checkbox").ready(function()
	{
		// Initialize
		$(".checkbox").each(function(index){
			if($(this).children("input").attr("value") )
				$(this).attr("data-value", "checked");
		});

		// Click event
		$(".checkbox").click(function() {
			if($(this).attr("data-value") == "checked" || $(this).attr("data-value") == "halfed")
			{
				$(this).attr("data-value", "");
				$(this).children("input").removeAttr("value");
			}
			else
			{
				$(this).attr("data-value", "checked");
				$(this).children("input").attr("value", $(this).children("input").attr("data-value"));
			}
			if($(this).parent().parent().hasClass("dropdown") )
			{
				if($(this).attr("data-value") == "checked")
				{
					$(this).parent().parent().children("div").children("ul").children("li").children(".checkbox[data-value!=checked]").click();
				}
				else
				{
					$(this).parent().parent().children("div").children("ul").children("li").children(".checkbox[data-value=checked]").click();
				}
			}
			else if($(this).parent().parent().parent().parent().hasClass("dropdown") )
			{
				var cnt1 = $(this).parent().parent().children("li").children(".checkbox[data-value=checked]").length;
				var cnt2 = $(this).parent().parent().children("li").length;

				if(cnt1 == 0)				
					$(this).parent().parent().parent().parent().children("a").children(".checkbox").attr("data-value", "");
				else if(cnt1 == cnt2)
					$(this).parent().parent().parent().parent().children("a").children(".checkbox").attr("data-value", "checked");
				else
					$(this).parent().parent().parent().parent().children("a").children(".checkbox").attr("data-value", "halfed");
			}
		});
	});

	// Dropdown component
	$(".dropdown").ready(function()
	{
		itemClickEvent = function(obj) {
			$(this).parent().children("li[data-value=\"true\"]").attr("data-value", "false");
			if($(this).attr("data-value") == "true")
				$(this).attr("data-value", "false");
			else
				$(this).attr("data-value", "true");
			$(this).parent().parent().parent().children("a").html($(this).children("a").html());
			$(this).parent().parent().parent().children("input").attr("value", $(this).index() + 1);

			$(this).parent().parent().hide();
		}

		// Dialog showing
		showDialog = function(th)
		{
			var h = $(th).position().top + 40;
			for(var i = 0; i < $(th).children("div").children("ul").children().length; i ++)
			{
				if($(th).children("div").children("ul").children().eq(i).css("display") == "none") continue;
				if(h + 36 > $(document).height() ) break;
				h += 36;
			}
			$(th).children("div").width("");
			$(th).children("div").show();
			$(th).children("div").width($(th).children("div").width() );
			$(th).children("div").height(h - $(th).position().top - 40);
		}

		// Initialize
		$(".dropdown").each(function(index){
			$(this).children("div").children("ul").children("li").attr("data-value", "false");
			$(this).children("div").children("ul").children("li").eq($(this).children("input").attr("value") - 1).attr("data-value", "true");
			$(this).children("a").html($(this).children("div").children("ul").children("li").eq($(this).children("input").attr("value") - 1).children("a").html());

			$(this).children("div").css("min-width", $(this).width() + 42);
		});

		// Mouse over/out event
		$(".dropdown").hover(function() {
			$(this).attr("data-type", "over");
			if($(this).hasClass("simple") )
				showDialog(this);
		}, function() {
			$(this).attr("data-type", "");
			$(this).children("div").hide();
		});

		// Click event
		$(".dropdown").click(function() {
			if(!$(this).hasClass("simple") )
			{
				if($(this).attr("data-type") != "clicked"){
					$(this).attr("data-type", "clicked");
					showDialog(this);
				}
				else
				{
					$(this).attr("data-type", "");
					$(this).children("div").hide();
				}
			}
		});
		// Click to Dropdown component's item event
		$(".dropdown:not(.multiple)").each(function(){
			$(this).children("div").children("ul").children("li").click(itemClickEvent);
		});

		// Tags-list component
		$(".tags-list").ready(function()
		{
			// Add to hidden input
			addHiddenInput = function(obj, name) {
				if(obj.children("input") != null)
					obj.append("<input type=\"hidden\" name=\"" + name + "[]\" value=\"" + obj.html() + "\" />");
			}

			// Add event
			addEvent = function(obj) {
				if($(this).css("display") != "none")
				{
					var newME = $(this).parent().parent().parent().parent().children("li:nth-last-child(1)").before("</li><li>").parent().children("li:nth-last-child(2)");
					newME.click(restoreEvent);
					newME.html($(this).parent().parent().parent().children("a").html());

					$(this).parent().parent().parent().children("a").html("Add More")
					$(this).css("display", "none");
				}
			}
			// Restore event
			restoreEvent = function(obj) {
                //confirm
                var confirmVal = confirm("Realy?");
                if(confirmVal)
                {
                    var dropdown = $(this).parent().children("li:nth-last-child(1)").children("div").children("ul");
                    dropdown.append("<li data-value=\"false\"><a>" + $(this).html() + "</a></li>");
                    dropdown.children("li:nth-last-child(1)").click(itemClickEvent).click(addEvent);
                    $(this).remove();
                    var csrftoken = getCookie('csrftoken')
                    var deletetag = {'tag' : $(this).text()}
                    $.ajax({
                          type: 'post'
                        , url: error_id+'/tag/delete'
                        , data: deletetag
                        , beforeSend: function(xhr, settings) {
                            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                                // Send the token to same-origin, relative URLs only.
                                // Send the token only if the method warrants CSRF protection
                                // Using the CSRFToken value acquired earlier
                                xhr.setRequestHeader("X-CSRFToken", csrftoken);
                            }
                        }
                    })
                }

			}

			// Initialize
			$(".tags-list").each(function(index){
				var child = $(this).children("ul").children("li");
				$(this).attr("data-name", $(this).children("input").attr("name") );
				$(this).children("input").remove();

				for(var i = 0; i < child.length; i ++)
				{
					if(!child.eq(i).hasClass("dropdown") )
					{
						addHiddenInput(child.eq(i), $(this).attr("data-name") );
						child.eq(i).click(restoreEvent);
					}
				}
				$(".tags-list .dropdown > div").css("min-width", parseInt($(".tags-list .dropdown > div").css("min-width") ) - 26);
				$(".tags-list .dropdown > div li").click(addEvent);
			});
		});
	});

	// Scrollbar component
	$(".scrollbar").ready(function()
	{
		// Initialize
		$(".scrollbar").each(function(index){
			var index = $(this).children("input").attr("value");
			var persent = 100.0 / ($(this).children("ul").children("li").length - 1);
			$(this).children("ul").children("li").each(function(){
				if($(this).children("a")[0].innerText == index)
					$(this).attr("data-value", "true");
				$(this).css("width", persent+"%");
			});
		});

		// Mouse over/out event
		$(".scrollbar > ul > li").hover(function() {
			if($(this).attr("data-value") )
				$(this).attr("data-temp", $(this).attr("data-value"));
			else
				$(this).attr("data-temp", "false");
			$(this).attr("data-value", "true");
		}, function() {
			$(this).attr("data-value", $(this).attr("data-temp"));
			$(this).removeAttr("data-temp");
		});
		$(".scrollbar > ul > li").click(function(){
			$(this).parent().children("li[data-value=true]").attr("data-value", "false");
			$(this).attr({"data-value":"true", "data-temp":"true"});
			$(this).parent().parent().children("input").attr("value", $(this).children("a")[0].innerText);
		});
	});
	/** Component End **/

	$(".checkbox.red").click(function() {
		if($(this).attr("data-value") == "checked"){
			$(".checkbox:not(.red)[data-value=checked] > input[name=\""+$(this).children("input").attr("name")+"\"]").each(function() { $(this).parent().click(); });
		}
	});
	$(".checkbox:not(.red)").click(function() {
		if($(this).attr("data-value") == "checked"){
			$(".checkbox.red[data-value=checked] > input[name=\""+$(this).children("input").attr("name")+"\"]").each(function() { $(this).parent().click(); });
		}
	});

	// Auto-resize table
	addWindowResize(function(){
		$("table > tbody > tr.empty").each(function(){
			$(this).css("display", "table-row");
			$(this).children().each(function(child){
				if($(this).attr("data-match") != "true")
					return;

				$(this).parent().parent().children().each(function(){
					if($(this).parent().hasClass("empty") == true)
						return;

					$(this).children().eq(child).children("p").width("0px");
				});

				var w = $(this).width();
				var chd = $(this).parent().parent().children().eq(0).children().eq($(this).index()).children(":not(p)");
				for(var i = 0; i < chd.length; i ++)
				{
					if(chd.eq(i).css("float") != "none")
						w -= chd.eq(i).width() + 12;
				}

				$(this).parent().parent().children().each(function(){
					if($(this).parent().hasClass("empty") == true)
						return;

					$(this).children().eq(child).children("p").width(w);
				});
			});
			$(this).css("display", "none");
		});
	})();

	// Auto-resize popup-information
	//$("#popup-information").click(hidePopupInformation);
	var bodyChecker = false;
	$("#popup-information").click(function(){ if(bodyChecker == false){ hidePopupInformation(); } bodyChecker = false; })
	$("#popup-information > .body").click(function(){ bodyChecker = true; })
	addWindowResize(resizePopupInformation)();
});