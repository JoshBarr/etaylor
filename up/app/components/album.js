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
		} else {
			var $thing = $(".cd-downloading");
			var $arrow = $thing.find("h1");
			$thing.show();
			$thing.addClass("cd-downloading--active");

			$arrow.velocity({
				opacity: [1, 0],
				top: ["25%", "20%"]
			}, {
				duration: 200,
				delay: 50,
				easing: "easeOutQuad"
			})

			$thing
				.velocity({
					opacity: 1
				},{
					duration: 100
				})
				.delay(3000).velocity({
					opacity: 0
				}, {
					duration: 300,
					complete: function(){
						$thing.removeClass("cd-downloading--active");
						$thing.hide();
						$arrow.css({top:"20%", opacity: 0});
					}
				});
			e.preventDefault();
		}		
	}
};