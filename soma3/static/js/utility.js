/**
 * Created with PyCharm.
 * User: JeongSeungsu
 * Date: 13. 9. 2
 * Time: 오후 5:46
 * To change this template use File | Settings | File Templates.
 */

//Error Page Function
function getinstancedata(idinstance)
{
    $.ajax({
      type: 'get'
    , url: idinstance
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
    , url: idinstance + '/instanceeventpath'
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
    , url: idinstance + '/log'
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

///////////////////// csrf토큰 가져오기//////////////////////////////
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

///////////////////////////////로그인 로그 아웃///////////////////////////////////
function logout()
{
   $.ajax({
          type: 'get'
        , url: '/urqa/user/logout'
   })
}
function login(data)
{
    //$.(this)
    $.ajax({
          type: 'post'
        , url: '/urqa/user/login'
        , data: data
        , beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
        , success : function (data){
            alert(data)
        }
   })
}

/////////email 정규표현식/////////////

function valid_email(str)
{
    re=/^[0-9a-zA-Z]([-_.]?[0-9a-zA-Z])*@[0-9a-zA-Z]([-_.]?[0-9a-zA-Z])*.[a-zA-Z]{2,3}$/i;

    // 위의 조건을 만족하려면 최소 6자 이상이어야 함.
    if(str.length<6 || !re.test(str))
    {
        alert("메일형식이 맞지 않습니다\n 다시 입력해주세요.\n");
        return false;
    }
    return true;
}


 function post_to_url(path, params, csrftoken) {
    var method = "post";
    var form = document.createElement("form");
    form.setAttribute("method", method);
    form.setAttribute("action", path);
    $(form).append(csrftoken);
    for(var key in params) {
        var hiddenField = document.createElement("input");
        hiddenField.setAttribute("type", "hidden");
        hiddenField.setAttribute("name", key);
        hiddenField.setAttribute("value", params[key]);
        form.appendChild(hiddenField);
    }
    document.body.appendChild(form);
    form.submit();
}

function stringstagetoint(strstage)
{
    if(strstage == 'Test')
        return 1;
    else if(strstage == 'Release')
        return 2;
    else if(strstage == 'Develope')
        return 0;
    else
        return -1;
}