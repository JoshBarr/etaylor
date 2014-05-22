module.exports = {
	init: function(zipManager) {
		this.$btn = $("[data-download-album]");
		this.$cd = $(".cd-image");
		this.$btn.on("click", $.proxy(this.click, this));
		this.zipManager = zipManager;
	},
	click: function(e) {
		if (this.zipManager.noZip) {
			e.preventDefault();
			e.stopPropagation();
			window.location.hash = "cant-download-zip-files";
		}		
	}
};