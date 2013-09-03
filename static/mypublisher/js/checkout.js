var count_down = 60;
var reboot_happening = false;

function start_checkout()
{
    if(CONF.production()) 
        if(!confirm('Are you sure you want to run checkout on the production server?'))
            return;
    if (reboot_happening)
    {
        alert('be patient!');
        return
    }
    count_down = 60;
    reboot_happening = true;
    jQuery('#countdown').val('contacting the server...');
    run_checkout();
}

function run_checkout()
{
    var rand = Math.random(10000000);
    jQuery.ajax({
        type: "GET",
        url: "/"+CONF.coach+"/publisher/checkout/",
        data: "rand=" + rand,
        success: function(resp) {
            reported_time = (60 - resp);
            if (reported_time < count_down)
                count_down = reported_time;
            //alert('rebooting in ' + count_down + ' seconds');
            jQuery('#countdown').val('rebooting in ' + count_down + ' seconds');
            run_checkout();
        },
        error: function (xhr, ajaxOptions, thrownError){
            //alert('REBOOTING NOW!');
            jQuery('#countdown').val('server is rebooting...');
            run_checkback()
        }
    }).done(function( msg ) {
    });
}

function run_checkback()
{
    var rand = Math.random(10000000);
    jQuery.ajax({
        type: "GET",
        url: "/"+CONF.coach+"/publisher/checkback/",
        data: "rand=" + rand,
        success: function(resp) {
            alert('server is back up');
            jQuery('#countdown').val('--');
            reboot_happening = false;
        },
        error: function (xhr, ajaxOptions, thrownError){
            window.setTimeout("run_checkback();", 2000);  
        }
    }).done(function( msg ) {
    });    
}

