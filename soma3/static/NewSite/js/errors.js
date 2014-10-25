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

    // Checkbox(Rank)
    var checkInfo = [
        "rank",
        "status"
    ];
    var checkList = [
        [
            $("#check-rank-unhandled"),
            $("#check-rank-native"),
            $("#check-rank-critical"),
            $("#check-rank-major"),
            $("#check-rank-minor")
        ],
        [
            $("#check-status-new"),
            $("#check-status-open"),
            $("#check-status-fixed"),
            $("#check-status-ignore")
        ]
    ];
    checkboxCheck = function() {
        splitName = function(n, o){return o.attr("id").split("check-"+n+"-")[1]}

        var obj = $(this);
        var index = obj.attr("data-index");

        var checkCount = 0;
        var checkName = checkInfo[index];

        filterData[checkName] = "";
        for (var i in checkList[index])
        {
            var checkbox = checkList[index][i];
            if (checkbox[0] != obj[0] && checkbox.prop("checked"))
            {
                checkCount ++;
                filterData[checkName] += splitName(checkName, checkbox);
            }
        }
        if (obj.prop("checked") == false)
        {
            checkCount ++;
            filterData[checkName] += splitName(checkName, obj);
        }

        if (checkCount == checkList[index].length)
            $("#check-" + checkName + "-all").prop("checked", true);
        else
            $("#check-" + checkName + "-all").prop("checked", false);

        updateFilterData();
    };
    checkAll = function() {
        splitName = function(n, o){return o.attr("id").split("check-"+n+"-")[1]}

        var obj = $(this);
        var index = obj.attr("data-index");

        var checkName = checkInfo[index];

        if (obj.prop("checked") == false)
        {
            var arguments = "";
            for (var i in checkList[index])
            {
                arguments += splitName(checkName, checkList[index][i]);
                checkList[index][i].prop("checked", true);
            }

            filterData[checkName] = arguments;
        }
        else
        {
            for (var i in checkList[index])
                checkList[index][i].prop("checked", false);

            filterData[checkName] = "";
        }
        updateFilterData();
    };
    for (var i in checkList)
    {
        for (var j in checkList[i])
        {
            checkList[i][j].click(checkboxCheck);
            checkList[i][j].attr("data-index", i);
        }

        $("#check-" + checkInfo[i] + "-all").click(checkAll);
        $("#check-" + checkInfo[i] + "-all").attr("data-index", i);
    }

    // Checkbox(Status)


    $("input[name=status]").click(function(){
        filterData["status"] = $(this).attr("value");
        updateFilterData();
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
});