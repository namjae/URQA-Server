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

    var checkboxList = [
        $("#check-unhandled"),
        $("#check-native"),
        $("#check-critical"),
        $("#check-major"),
        $("#check-minor")
    ];
    checkAll = function() {
        var obj = $(this);
        var checkCount = 0;

        filterData["rank"] = "";
        for (var checkbox in checkboxList)
        {
            checkbox = checkboxList[checkbox];
            if (checkbox[0] != obj[0] && checkbox.prop("checked"))
            {
                checkCount++;
                filterData["rank"] += checkbox.attr("id").split("check-")[1];
            }
        }
        if (obj.prop("checked") == false)
            filterData["rank"] += obj.attr("id").split("check-")[1];

        if(checkCount == 4)
        {
            if (obj.prop("checked") == false)
                $("#check-all").prop("checked", true);
            else
                $("#check-all").prop("checked", false);
        }
        else
            $("#check-all").prop("checked", false);

        updateFilterData();
    };
    $("#check-all").click(function(){
        if ($(this).prop("checked") == false)
        {
            for (var checkbox in checkboxList)
                checkboxList[checkbox].prop("checked", true);

            filterData["rank"] = "unhandled,native,critical,major,minor";
        }
        else
        {
            for (var checkbox in checkboxList)
                checkboxList[checkbox].prop("checked", false);

            filterData["rank"] = "";
        }
        updateFilterData();
    });
    $("#check-unhandled").click(checkAll);
    $("#check-native").click(checkAll);
    $("#check-critical").click(checkAll);
    $("#check-major").click(checkAll);
    $("#check-minor").click(checkAll);

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