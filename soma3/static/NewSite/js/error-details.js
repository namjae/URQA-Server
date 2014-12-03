function strip_tags(input, allowed)
{
    allowed = (((allowed || "") + "").toLowerCase().match(/<[a-z][a-z0-9]*>/g) || []).join('');
    // making sure the allowed arg is a string containing only tags in lowercase (<a><b><c>)

    var tags = /<\/?([a-z][a-z0-9]*)\b[^>]*>/gi,
        commentsAndPhpTags = /<!--[\s\S]*?-->|<\?(?:php)?[\s\S]*?\?>/gi;
    return input.replace(commentsAndPhpTags, '').replace(tags, function ($0, $1) {
        return allowed.indexOf('<' + $1.toLowerCase() + '>') > -1 ? $0 : '';
    });
}

$(document).ready(function()
{
	$('#tags_1').tagsInput({'height':'80px',width:'auto'});

    (function(){
    	var d1 = [
            ["10.20", 10],
            ["10.21", 20],
            ["10.22", 33],
            ["10.23", 24],
            ["10.24", 34],
            ["10.25", 36],
            ["10.26", 27],
            ["10.27", 18],
            ["10.28", 11],
            ["10.29", 13],
            ["10.30", 21]

        ];
        var data = ([{
            label: "Too",
            data: d1,
            lines: {
                show: true,
                fill: true,
                lineWidth: 2,
                fillColor: {
                    colors: ["rgba(255,255,255,.1)", "rgba(153,114,181,.8)"]
                }
            }
        }]);
    	var options = {
            grid: {
                backgroundColor: {
                    colors: ["#fff", "#fff"]
                },
                borderWidth: 0,
                borderColor: "#f0f0f0",
                margin: 0,
                minBorderMargin: 0,
                labelMargin: 20,
                hoverable: true,
                clickable: true
            },
            // Tooltip
            tooltip: true,
            tooltipOpts: {
                content: "%s X: %x Y: %y",
                shifts: {
                    x: -60,
                    y: 25
                },
                defaultTheme: false
            },

            legend: {
                labelBoxBorderColor: "#ccc",
                show: false,
                noColumns: 0
            },
            series: {
                stack: true,
                shadowSize: 0,
                highlightColor: 'rgba(153,114,181,.5)'
            },
            xaxis: {
                tickLength: 0,
                show: true,
                font: {
                    style: "normal",
                    color: "#666666"
                }
            },
            yaxis: {
                ticks: 3,
                tickDecimals: 0,
                show: true,
                tickColor: "#f0f0f0",
                font: {
                    style: "normal",
                    color: "#666666"
                }
            },
            points: {
                show: true,
                radius: 2,
                symbol: "circle"
            },
            colors: ["#9972b5"]
        };
        var plot = $.plot($("#error-history-graph"), data, options);
    })();

    $("#comment-form").submit(function(event)
    {
        var i = $(this).children("div").children("input");
        var val = strip_tags(i.val(), "");

        if (val == "")
            return false;

        $(this).parent().before("<div class=\"comment-body col-sm-12\">\
            <div class=\"comment-block\">\
                <div class=\"profile\">\
                    <img src=\"images/avatar1_small.jpg\" alt=\"\" />\
                </div>\
                <div class=\"content\"><div>\
                    <label>John Doe</label>\
                    <span>1 second ago</span>\
                    <p>" + val + "</p>\
                </div></div>\
            </div>\
        </div>");
        i.val("");

        var obj = $(this).parent().prev();
        (function(n){
            var h = n.height();
            var mt = n.css("margin-top");
            var mb = n.css("margin-bottom");

            n.css("opacity", "0").css("height", "0").css("margin-top", "0").css("margin-bottom", "0");
            n.animate({
                opacity: 1.0,
                "margin-top": mt,
                "margin-bottom": mb,
                "height":h
            }, 350, function(){
                $(this).css("margin-top", "").css("margin-bottom", "").css("opacity", "").css("height", "");
            });
        })(obj);

        alert("(AJAX)Saved Comment!");
        return false;
    })
});

function openDetails(obj)
{
    var o = $(obj);
    var n = o.parent().next();
    if (n.css("display") == "none")
    {
        n.css("display", "");
        n = n.children("td");

        var pt = n.css("padding-top");
        var pb = n.css("padding-bottom");
        var h = n.children("form").height();

        n.css("opacity", "0").css("padding-top", "0").css("padding-bottom", "0");
        n.children("form")
            .css("height", "0")
            .css("overflow", "hidden")
            .css("display", "block");

        n.animate({
            opacity: 1.0,
            "padding-top": pt,
            "padding-bottom": pb
        }, 350, function(){
            $(this).css("padding-top", "").css("padding-bottom", "").css("opacity", "");
        });
        n.children("form").animate({
            height: h
        }, 350, function(){
            $(this).css("overflow", "").css("display", "").css("height", "");
        });

        o.children("i").addClass("fa-chevron-up").removeClass("fa-chevron-down");
    }
    else
    {
        n = n.children("td");
        n.animate({
            opacity: 0.0,
            "padding-top": 0,
            "padding-bottom": 0
        }, 350, function(){
            $(this).css("padding-top", "").css("padding-bottom", "").css("opacity", "");
        });
        n.children("form").animate({
            height: 0
        }, 350, function(){
            $(this).css("overflow", "").css("display", "").css("height", "");
            n.parent().css("display", "none");
        });

        o.children("i").addClass("fa-chevron-down").removeClass("fa-chevron-up");
    }
}