// ----------------------------------------------------
// Transport
// ----------------------------------------------------
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken)
        }
    }
});

// Some sneaky UA detection

var iOS =  ( window.navigator.userAgent.match(/(iPad|iPhone|iPod)/g) ? true : false );
var windowsPhone = (window.navigator.userAgent.match(/Windows Phone/) ? true : false );


module.exports = {
	$doc: $(document),
	$body: $("body"),
	$html: $(document.documentElement),
	$stage: $("[data-stage]"),
	csrftoken: $('meta[name=csrf-token]').attr('content'),

	ua: window.navigator.userAgent,
	iOS: iOS,
	windowsPhone: windowsPhone,
	tests: {
		supportsZip: function() {
			return (windowsPhone || iOS ? false : true);
		}
	},
};
