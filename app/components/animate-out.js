var AnimateOut = function($element, props, options) {
    this.$el = $element;

    var complete = $.proxy(this.animationComplete, this, options.href || false);

    if (typeof(options.complete) === "function") {
        complete = options.complete;
    }

    this.$el.velocity(props, {
        duration: options.duration || 300,
        delay: 200,
        complete: complete,
        easing: options.easing || "ease"
    });

    $("[data-ui-brush]").velocity({
        opacity: 0
    },{
        duration: 300,
        easing: "easeOutSine"
    });
};

AnimateOut.prototype = {
    animationComplete: function(href) {
        if (href) {
           window.location = href;
        }
    }
};

module.exports = AnimateOut;