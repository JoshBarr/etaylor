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
			var $btn = this.$btn;

			$thing.show();
			$thing.addClass("cd-downloading--active");
			$btn.css({opacity: 0});

			$arrow.velocity({
				opacity: [1, 0],
				top: ["22%", "18%"]
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
				.delay(3000)
				.velocity({
					opacity: 0
				}, {
					duration: 10,
					begin: function() {
						$btn.css({opacity: 1});
					},
					complete: function(){
						$thing.removeClass("cd-downloading--active");
						$thing.hide();
						$arrow.css({top:"18%", opacity: 0});

					}
				});
		}		
	}
};