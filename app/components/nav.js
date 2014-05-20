var Nav = function() {
	this.brushEl = document.querySelector("[data-ui-brush]");
	this.navEl = document.querySelector("[data-ui-nav]");
	this.navContentEl = document.querySelector("[data-ui-nav] :first-child");
		
	this.isTouch = !!("touchstart" in document);
};

Nav.prototype = {
	init: function() {
		this.$navEl = $(this.navEl);
		this.$brushEl = $(this.brushEl);
		this.$navContentEl = $(this.navContentEl);


		if (!this.isTouch) {
			this.$navEl.on("mouseenter", $.proxy(this.hoverOn, this));
			this.$navEl.on("mouseleave", $.proxy(this.hoverOff, this));
		}
	},
	handleEvent: function(e) {

	},
	hoverOn: function(e) {

		// So this is pretty sweet. Check if the mouse arrived from
		// somewhere. If not, we've probably just hit a page refresh.
		if (e.fromElement === null) {
			return;
		}

		this.$brushEl.velocity({
			opacity: 0.05,
			top: ["-2%", 0],
		}, {
			duration: 100,
			easing: "easeInQuad"
		});

		this.$navEl.velocity({
			opacity: 1,
		}, {
			duration: 130,
			delay: 100,
			easing: "easeInOutQuad"
		});

		this.$navContentEl.velocity({
			// opacity: 1,
			top: [0, "10%"],
		}, {
			duration: 130,
			delay: 100,
			easing: "easeInOutQuad"
		});


	},
	hoverOff: function(e) {
		this.$brushEl.velocity({
			opacity: 1,
			top: 0,
			easing: "easeOutQuad"
		}, {
			duration: 100,
			delay: 200
		});

		this.$navEl.velocity({
			opacity: 0,
		}, {
			duration: 300,
			easing: "easeInOutQuad"
		});

		this.$navContentEl.velocity({
			top: "10%",
		}, {
			duration: 300,
			easing: "easeInOutQuad",
			complete: function($el) {
				if ($el) {
					var el = $el[0];
					el.style.top = "";
				}
			}
		});
	},
};

module.exports = new Nav();

