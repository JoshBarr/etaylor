(function() {

	var csrftoken = $('meta[name=csrf-token]').attr('content')

	$.ajaxSetup({
	    beforeSend: function(xhr, settings) {
	        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
	            xhr.setRequestHeader("X-CSRFToken", csrftoken)
	        }
	    }
	});


})(window, document, $);




var Site = (function(document, window){

	var site = function() {

	}

	site.prototype = {

		maxChars: 100,

		showAlbumArt: function() {
			var self = this;
			setTimeout(function() {
				if (!self.isSticky) {
					self.$cd.addClass("cd-art--active");
					self.hasAlbumArt = true;
					$("[data-sticky-hide]").removeClass("transition-hide");
				}
			}, 800);
			
		},

		hideAlbumArt: function() {
			var self = this;
			self.$cd.removeClass("cd-art--active");
			$("[data-sticky-hide]").addClass("transition-hide");
		},

		makeLogoSticky: function() {
			var self = this;
			if (!this.isSticky) {
				self.$logo.addClass("site-header--fixed");
				self.hideAlbumArt();
				self.$logoPlaceholder.attr("style", "display: block; visibility: hidden");
				this.isSticky = true;
				this.hasAlbumArt = false;
			}
		},

		makeLogoUnSticky: function() {
			var self = this;
			if (this.isSticky) {
				self.$logo.removeClass("site-header--fixed");
				self.$logoPlaceholder.attr("style", "display: block; visibility: visible");
				this.isSticky = false;
			}
		},

		init: function() {
			var self = this;
			console.log("init");
			//this.$textarea = document.getElementById("textarea");
			// document.getElementById("start").scrollIntoView();

			window.location.hash = "start";

			// this.$textarea.focus();
			// this.$textarea.value=""; // prevent chrome...
			this.$logo = $("[data-sticky]");
			this.$logoPlaceholder = $("[data-sticky-placeholder]");
			this.$cd = $("[data-cover]");

			this.placeholderTop = this.$logoPlaceholder.offset().top;
			this.placeholderHeight = this.$logoPlaceholder.height();
			this.magicNumber = 256;

			this.$scrollRoot = $("html, body");

			$("[data-scroll-href]").on("click", $.proxy(self.doScrollClick, self));
			$(document).on("scroll", $.proxy(self.doScroll, self));

			$("[data-tweet-btn]").on("click", $.proxy(self.doTwitter, self));
			$("[data-download-btn]").on("click", $.proxy(self.doDownload, self));


			// document.getElementById("start").scrollIntoView();
			document.documentElement.scrollTop = 9999;
			self.doScroll();
			self.hideAlbumArt();
		},

		doDownload: function(e) {
			e.preventDefault();
			this.$cd.toggleClass("cd-art--download");
			console.log("download");
			window.location.hash = "download";
		},

		doTwitter: function(e) {
			e.preventDefault();
			$("[data-tweet]").toggleClass("block--hide");
		},

		doScroll: function(e) {
			var self = this;
			var scroll = document.body.scrollTop;
				// console.log(scroll);

				if (+scroll < self.placeholderTop + self.magicNumber) {
					
					self.makeLogoUnSticky.call(self);

					if (scroll <= this.placeholderTop + (self.placeholderHeight/2)) {
						if (!self.hasAlbumArt) {
							self.showAlbumArt();
						}
						
					}

				} else {
					self.makeLogoSticky.call(self);
				}
		},

		// Do ajaz request
		onWorking: function(e) {
			var dfd = new jQuery.Deferred();
			console.log("working");

			$.ajax({
				url: "post/",
				success:function(response) {
					return dfd.resolve(this);
				},
				error: function(response) {
					console.log('error');
					setTimeout(function() {
						return dfd.resolve(this);
					}, 500);
					
				}
			})

			
			return dfd.promise();
		},

		onQuestion: function(e) {
			var dfd = new jQuery.Deferred();
			var confession = document.getElementById("confession");
			var remaining = document.getElementById("chars_remaining");
			var submit = document.getElementById("submit");
			var submit_text = submit.innerHTML;
			var char_max = document.getElementById("char_max");

			var self = this;
			console.log("question");
			this.albumText = "";
			confession.value = "";
			remaining.innerHTML = 100;
			char_max.innerHTML = this.maxChars;

			if (!this.didAddListener) {
				this.didAddListener = true;
				
				confession.addEventListener("keydown", function (e) {
					var me = e.target;
					var len = me.value.length;
					var remaining_chars = self.maxChars - len;
					remaining.innerHTML = remaining_chars;

					if (remaining_chars < 0) {
						
						if (!this.warningShown) {
							submit.href = "#question";
							submit.innerHTML = "Ooops... your message is too long";
							submit.className = submit.className.replace(" btn-primary", "");
							this.warningShown = true;
						}

					} else {
						
						if (this.warningShown) {
							this.warningShown = false;
							submit.href = "#working";
							submit.innerHTML = submit_text;
							submit.className += " btn-primary";
						}
					}

				}, false);
			}

			


			return dfd.resolve(this);
		},

		onAlbum: function(e) {
			var dfd = new jQuery.Deferred();
			console.log("album");
			var face = document.getElementById("cd_face");
			if (this.albumText) {

				var confession = document.createElement("h2");
				confession.innerHTML = this.albumText;
				face.innerHTML = "";
				face.appendChild(confession);
			}
			

			return dfd.resolve();
		},

		nextScreen: function(top, id, $parent) {
			var dfd = new jQuery.Deferred();
			var self = this;
			console.log("nextScreen");
			this.$scrollRoot.animate({
				scrollTop: top
			}, {
				duration: 1000,
				easing: "easeInOutQuint",
				complete: function() {
					// window.location.hash = id;
					$parent.removeClass("block--inactive");
							window.location.hash = id;
					return dfd.resolve(self);
				}
			});
			return dfd.promise();
		},

		initWorkingScreen: function() {
			var self = this;
			setTimeout(function() {
				// return dfd.resolve(this);
				// self.nextScreen(0, "album", $(document.getElementById("album")));
				// var $el = $("a[href='#album']");
				// $el.trigger("click");
			}, 5000);
			this.albumText = document.getElementById("confession").value;
		},

		doScrollClick: function(e) {
			var self = this;
			var target = e.currentTarget;
			var $target = $(target);
			var id = $target.attr("href").replace("#", "");
			var targetEl = document.getElementById(id);
			var $targetEl = $(targetEl);
			var top = $targetEl.offset().top;

			// var $parent = $targetEl.parents("[data-stretchy-block]");
			var $parent = $targetEl;
			// console.log($parent);

			history.pushState({href: id});

			e.stopPropagation();
			e.preventDefault();

			if (id === "working") {
				$.when(self.onWorking()).done(function() {
					$.when(self.nextScreen(top, id, $parent)).done(function() {
						self.initWorkingScreen();
					});
				});
			}

			if (id === "question") {
				// self.onQuestion();
				$.when(self.onQuestion()).done(function() {
					self.nextScreen(top, id, $parent);
				});
			}

			if (id === "album") {
				$.when(self.onAlbum()).done(function() {
					self.nextScreen(top, id, $parent);
				});
			}

			return false;
		}
	};

	return new site();

})(document, window);


// Boot it.
(function() {
	$(document).ready(function() {
		// console.log('onload');
		// Site.init();
	});
})();