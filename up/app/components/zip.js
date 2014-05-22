// ----------------------------------------------------
// Zip Toggler
// ----------------------------------------------------

var config = require("./config.js");
var tests = config.tests;
var $html = config.$html;
 

var ZipToggle = {
	selector: "[data-toggle-zip-status]",
	supportedClass: "no-zip",
	init: function() {
		var self = this;
		
		if (!tests.supportsZip()) {
			this.setNoZip();
		}

		if ($html.hasClass("no-zip")) {
			this.setNoZip();
		}

		var noZipEl = $("[data-download-nozip]");
		var zipEl = $("[data-download-zip]");
		
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

module.exports = ZipToggle;
