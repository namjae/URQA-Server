$(function(){
    $("#timezone").select2().select2("val", "Asia/Seoul");
    $('input[type="checkbox"],[type="radio"]').not('#create-switch').bootstrapSwitch();
});

// Checkbox
$(function(){
    var checkInfo = [
        {
            "type": "tags",
            "keyword": "tag",
            "taglist": $("#tagsearch")
        }
    ];
    selectboxChange = function(){
        if ($(this).val() === "Select")
            return;

        // Add Checkbox
        var index = $(this).attr("data-index");
        var obj = $(this).children("option:selected");
        var IDName = checkInfo[index]["prefix"] + obj.val().split(".").join("_");
        $(this).before("<div class=\"flat-green\" style=\"white-space:nowrap;overflow:hidden\">\n\
            <div class=\"radio\">\n\
                <input id=\"" + IDName + "\" type=\"checkbox\" checked>\n\
                <label>" + obj.val() + "</label>\n\
            </div>\n\
        </div>");

        // Add Checkbox Event
        $("#" + IDName).on('ifCreated ifClicked ifChanged ifChecked ifUnchecked ifDisabled ifEnabled ifDestroyed check ', function(event){                
            if(event.type ==="ifChecked"){
                $(this).trigger('click');  
                $('input').iCheck('update');
            }
            if(event.type ==="ifUnchecked"){
                $(this).trigger('click');  
                $('input').iCheck('update');
            }       
            if(event.type ==="ifDisabled"){
                console.log($(this).attr('id')+'dis');  
                $('input').iCheck('update');
            }                                
        }).iCheck({
            checkboxClass: 'icheckbox_flat-green',
            radioClass: 'iradio_flat-green'
        }).click(checkboxCheck).attr("data-index", index);
        checkInfo[index]["list"][checkInfo[index]["list"].length] = $("#" + IDName);

        // Checkbox Animation
        var newObj = $(this).prev();
        var lastWidth = newObj.width();
        newObj.css("width", 0);
        setTimeout(function(){
            newObj.css("transition", "width 0.35s").css("-moz-transition", "width 0.35s").css("-webkit-transition", "width 0.35s").css("width", lastWidth);
            setTimeout(function(){
                newObj.css("width", "").css("white-space", "").css("overflow", "").css("transition", "").css("-moz-transition", "").css("-webkit-transition", "");
            }, 350);
        }, 50);

        // SelectBox
        $(this).val("Select");
        obj.remove();
    };
    tagClick = function() {
        var index = $(this).parent().attr("data-index");
        var nameValue = $(this).children("span").text();

        // Tag Animation
        $(this).parent().children("select").append(new Option(nameValue, nameValue));
        $(this).css("white-space", "nowrap").css("overflow", "hidden").animate({
            width: 0
        }, 350, function() {
            $(this).remove();
        });
    };
    tagSelectboxChange = function() {
        if ($(this).val() === "Select")
            return;

        // Add Checkbox
        var index = $(this).parent().attr("data-index");
        var obj = $(this).children("option:selected");
        $(this).before("<span class=\"tags\" style=\"white-space:nowrap;overflow:hidden\">\n\
            <span>" + obj.val() + "</span>\n\
            <a>x</a>\n\
        </span>");
        $(this).prev().click(tagClick);

        // Tag Animation
        var newObj = $(this).prev();
        var lastWidth = newObj.width();
        newObj.css("width", 0);
        setTimeout(function(){
            newObj.css("transition", "width 0.35s").css("-moz-transition", "width 0.35s").css("-webkit-transition", "width 0.35s").css("width", lastWidth);
            setTimeout(function(){
                newObj.css("width", "").css("white-space", "").css("overflow", "").css("transition", "").css("-moz-transition", "").css("-webkit-transition", "");
            }, 350);
        }, 50);

        // SelectBox
        $(this).val("Select");
        obj.remove();
    };

    // Initialize
    for (var i in checkInfo)
    {
        if (checkInfo[i]["type"] === "tags")
        {
            // SelectBox
            checkInfo[i]["taglist"].children("select").change(tagSelectboxChange);

            // Tags
            checkInfo[i]["taglist"].children("span.tags").filter(function() {
                $(this).click(tagClick);
            });

            // Filtering String
            if (checkInfo[i]["filterString"] === undefined)
            {
                checkInfo[i]["filterString"] = function(obj) {
                    return obj.children("span").text();
                }
            }

            checkInfo[i]["taglist"].attr("data-index", i);
        }
    }
});