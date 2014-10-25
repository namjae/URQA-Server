$(document).ready(function()
{
    filterData = {
        "rank": "unhandled,native,critical,major,minor",
        "datestart": 1,
        "dateend": 1,
        "status": "all"
    };

    /** Data Table */
    var _dataTable = $('#dynamic-table').dataTable( {
        "bJQueryUI": true,
        "bStateSave": true,
        "bProcessing": true,
        "bServerSide": true,
        "sAjaxSource": "./test.json",
        "sAjaxDataProp": "aaData",
        "aaSorting": [[ 1, "desc" ]],
        "bUseRendered": true,
        "bLengthChange": false,
        "bFilter": false,
        "bInfo": false,
        "aoColumnDefs":[
            {
                "aTargets": [0, 1, 2, 3, 4],
                "fnCreatedCell": function(nTd, sData, oData, iRow, iCol){
                    var nameList = ["Rank", "Count", "Name", "Tags", "Date"];
                    var styleList = ["text-center", "text-center", "table-text-ellipsis", "tags", "res-hidden"];
                    $(nTd).attr("data-title", nameList[iCol]).addClass(styleList[iCol]);

                    if (iCol == 0)
                    {
                        $(nTd).html('<span class=\"label label-' + sData.toLowerCase() + ' label-mini\" style=\"width:100%\">' + sData + '</span>');
                    }
                    else if (iCol == 1)
                    {
                        if (iRow == 0)
                            $(nTd).addClass("text-danger text-bold");
                    }
                    else if (iCol == 2)
                    {
                        $(nTd).html('<div>\n ' + sData + '\n </div>');
                    }
                    else if (iCol == 3)
                    {
                        sHTML = "<p>\n";
                        oDataList = sData.split(",");
                        for (sTag in oDataList)
                            sHTML += "<span class=\"label label-primary label-mini\">" + oDataList[sTag] + "</span>\n ";
                        sHTML += "\n</p>";

                        $(nTd).html(sHTML);
                    }
                }
            }
        ],
        "fnServerParams": function (aoData) {
            for (prop in filterData) {
                aoData.push( { "name": prop, "value": filterData[prop] } );
            }
        },
        "aoColumns":[
            {"bSortable": true},
            {"bSortable": true},
            {"bSortable": false},
            {"bSortable": false},
            {"bSortable": true}
        ],
        "oLanguage":{
            "oPaginate":{
                "sPrevious": "Prev"
            }
        }
    } );
    updateFilterData = function() { _dataTable.api().ajax.reload(); }

    $('#btnTranding').click(function() {
        _dataTable.api().ajax.url('./test.json').load();
    } );
    $('#btnLatest').click(function() {
        _dataTable.api().ajax.url('./test2.json').load();
    } );


    /** iCheck */
    $(function(){
        $('.flat-red input').on('ifCreated ifClicked ifChanged ifChecked ifUnchecked ifDisabled ifEnabled ifDestroyed check ', function(event){                
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
            checkboxClass: 'icheckbox_flat-red',
            radioClass: 'iradio_flat-red'
        });
    });
    $(function(){
        $('.flat-grey input').on('ifCreated ifClicked ifChanged ifChecked ifUnchecked ifDisabled ifEnabled ifDestroyed check ', function(event){                
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
            checkboxClass: 'icheckbox_flat-grey',
            radioClass: 'iradio_flat-grey'
        });
    });
    $(function(){
        $('.flat-green input').on('ifCreated ifClicked ifChanged ifChecked ifUnchecked ifDisabled ifEnabled ifDestroyed check ', function(event){                
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
        });
    });
    $(function(){
        $('.flat-blue input').on('ifCreated ifClicked ifChanged ifChecked ifUnchecked ifDisabled ifEnabled ifDestroyed check ', function(event){                
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
            checkboxClass: 'icheckbox_flat-blue',
            radioClass: 'iradio_flat-blue'
        });
    });
    $(function(){
        $('.flat-yellow input').on('ifCreated ifClicked ifChanged ifChecked ifUnchecked ifDisabled ifEnabled ifDestroyed check ', function(event){                
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
            checkboxClass: 'icheckbox_flat-yellow',
            radioClass: 'iradio_flat-yellow'
        });
    });
    $(function(){
        $('.flat-purple input').on('ifCreated ifClicked ifChanged ifChecked ifUnchecked ifDisabled ifEnabled ifDestroyed check ', function(event){                
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
            checkboxClass: 'icheckbox_flat-purple',
            radioClass: 'iradio_flat-purple'
        });
    });

    // Checkbox
    var checkInfo = [
        {
            "keyword": "rank",
            "prefix": "check-rank-",
            "all": $("#check-rank-all"),
        },
        {
            "keyword": "status",
            "prefix": "check-status-",
            "all": $("#check-status-all")
        },
        {
            "keyword": "appversion",
            "prefix": "check-app-",
            "all": $("#check-app-all"),
            "filterString": function(obj) {
                return obj.attr("id").split("-")[obj.attr("id").split("-").length - 1].split("_").join(".");
            }
        }
    ];

    reloadFilterData = function() {
        for (var i in checkInfo)
        {
            var info = checkInfo[i];

            filterData[info["keyword"]] = "";
            for (var j in info["list"])
            {
                var checkbox = info["list"][j];
                if (checkbox.prop("checked"))
                    filterData[info["keyword"]] += info["filterString"](checkbox) + ",";
            }
        }

        updateFilterData();
    };
    checkboxCheck = function() {
        var obj = $(this);
        var index = obj.attr("data-index");

        var checkCount = 0;
        var info = checkInfo[index];

        filterData[info["keyword"]] = "";
        for (var i in info["list"])
        {
            var checkbox = info["list"][i];
            if (checkbox[0] != obj[0] && checkbox.prop("checked"))
            {
                checkCount ++;
                filterData[info["keyword"]] += info["filterString"](checkbox) + ",";
            }
        }
        if (obj.prop("checked") == false)
        {
            checkCount ++;
            filterData[info["keyword"]] += info["filterString"](obj) + ",";
        }

        if (checkCount == info["list"].length)
            info["all"].prop("checked", true);
        else
            info["all"].prop("checked", false);

        updateFilterData();
    };
    checkAll = function() {
        var obj = $(this);
        var index = obj.attr("data-index");

        var info = checkInfo[index];

        if (obj.prop("checked") == false)
        {
            var arguments = "";
            for (var i in info["list"])
            {
                arguments += info["filterString"](info["list"][i]) + ",";
                info["list"][i].prop("checked", true);
            }

            filterData[info["keyword"]] = arguments;
        }
        else
        {
            for (var i in info["list"])
                info["list"][i].prop("checked", false);

            filterData[info["keyword"]] = "";
        }
        updateFilterData();
    };

    // Initialize
    for (var i in checkInfo)
    {
        // Checkbox
        if (checkInfo[i]["info"] !== undefined)
        {
            for (var j in checkList[i])
                checkList[i][j].click(checkboxCheck).attr("data-index", i);
        }
        else
        {
            var j = 0;
            checkInfo[i].list = [];
            $("[id^=" + checkInfo[i]["prefix"] + "]").each(function(){
                if ($(this)[0] != checkInfo[i]["all"][0])
                {
                    $(this).click(checkboxCheck).attr("data-index", i);
                    checkInfo[i].list[j++] = $(this);
                }
            });
        }

        // Filtering String
        if (checkInfo[i]["filterString"] === undefined)
        {
            checkInfo[i]["filterString"] = function(o) {
                return o.attr("id").split("-")[o.attr("id").split("-").length-1];
            };
        }

        // Check All
        checkInfo[i]["all"].click(checkAll);
        checkInfo[i]["all"].attr("data-index", i);
    }
    reloadFilterData();

    /** SelectBox */
    $("#select-app").change(function(){
        if ($(this).val() === "Select")
            return;

        // Add Checkbox
        var obj = $("#select-app option:selected");
        var IDName = checkInfo[2]["prefix"] + obj.val().split(".").join("_");
        $(this).before("<div class=\"flat-green\" style=\"white-space:nowrap;overflow:hidden\">\
            <div class=\"radio\">\
                <input id=\"" + IDName + "\" type=\"checkbox\" checked>\
                <label>" + obj.val() + "</label>\
            </div>\
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
        }).click(checkboxCheck).attr("data-index", 2);
        checkInfo[2]["list"][checkInfo[2]["list"].length] = $("#" + IDName);
        updateFilterData();

        // Checkbox Animation
        var newObj = $(this).prev();
        var lastWidth = newObj.width();
        newObj.css("width", 0);
        setTimeout(function(){
            newObj.css("transition", "width 0.35s").css("-webkit-transition", "width 0.35s").css("width", lastWidth);
            setTimeout(function(){
                newObj.css("width", "").css("white-space", "").css("overflow", "");
            }, 350);
        }, 50);

        // SelectBox
        $(this).val("Select");
        obj.remove();
    });

    /** Iron Range Slider */
    $("#date-slider").ionRangeSlider({
        onFinish: function(data) {
            filterData["datestart"] = data.fromNumber;
            filterData["dateend"] = data.toNumber;
            updateFilterData();
        }
    });

    var updateSliderScale = null;
    $(window).resize(function(){
        clearTimeout(updateSliderScale);
        updateSliderScale = setTimeout(function(){
            $("#date-slider").ionRangeSlider('update');
        }, 100);
    });
    $('.panel .tools .fa').click(function () {
        clearTimeout(updateSliderScale);
        updateSliderScale = setTimeout(function(){
            $("#date-slider").ionRangeSlider('update');
        }, 100);
    });
});