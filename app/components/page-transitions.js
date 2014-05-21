var config = require("./config.js");
var $stage = config.$stage;
var AnimateOut = require("./animate-out.js");


module.exports = {
    init: function() {
        this.elems = document.querySelectorAll("[data-animate-link]");
        this.$elems = $(this.elems);
        this.$elems.on("click", $.proxy(this.handleClick, this));

        $stage.delay(100).velocity({
            opacity: 1
        }, {
            duration: 500,
            easing: "easeOutQuad",
            complete: function(el) {
                $(el).removeClass('js-ghost');
            }
        });
    },
    handleClick: function(e) {
        e.preventDefault();
        var target = e.originalEvent.target;
        console.log(target);
        var $body = $("body");
        
        var animate = new AnimateOut($body, {
            opacity: 0
        }, {
            duration: 300,
            easing: "easeInQuad",
            href: target.getAttribute('href')
        });
    },
    showBrush: function(delay, duration) {
        $("[data-ui-brush]").velocity({
            opacity: 1
        },{
            duration: duration || 600,
            easing: "easeOutQuad",
            delay: delay
        });
    }
};