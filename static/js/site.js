var Site = (function(window, document, $) {
	
	// ----------------------------------------------------
	// Config
	// ----------------------------------------------------
	
	var $doc = $(document);
	var $html = $(document.documentElement);
	var csrftoken = $('meta[name=csrf-token]').attr('content')

	var ua = window.navigator.userAgent;
	var iOS = ( ua.match(/(iPad|iPhone|iPod)/g) ? true : false );
	var windowsPhone = (ua.match(/Windows Phone/) ? true : false );

	var tests = {
		supportsZip: function() {
			return (windowsPhone || iOS ? false : true);
		}
	}

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

	// ----------------------------------------------------
	// Zip Toggler
	// ----------------------------------------------------

	var ZipToggle = {
		selector: "[data-toggle-zip-status]",
		supportedClass: "no-zip",
		init: function() {
			var self = this;
			if (!tests.supportsZip()) {
				this.setNoZip();
			}
			this.$togglers = $(this.selector);
			this.$togglers.click(function(e) {
				e.preventDefault();
				if (!self.noZip) {
					self.setNoZip.call(self);
				} else {
					self.setZip.call(self);
				}
			});
			return this;
		},
		setNoZip: function() {
			$html.addClass(this.supportedClass);
			this.noZip = true;
		},
		setZip: function() {
			$html.removeClass(this.supportedClass);
			this.noZip = false;
		}
	};


	


	// ----------------------------------------------------
	// App
	// ----------------------------------------------------
	var Site = {
		modules: {},
		init: function() {

		}
	};

	// ----------------------------------------------------
	// Boot
	// ----------------------------------------------------
	$doc.ready(function() {
		Site.init();
		Site.modules['zip'] = ZipToggle.init();
	});

	return Site

})(window, document, $);
