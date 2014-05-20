var ElaborateProgressBar = function(el, options) {
    this.el = el;
    this.steps = [
        {
            "label": "Briefing the designer...",
            "icon": "pencil"
        },
        {
            "label": "Opening editor...",
            "icon": "pencil"
        },
        {
            "label": "Sending art to the printer...",
            "icon": "pencil"
        },
        {
            "label": "Printing art...",
            "icon": "pencil"
        },
        {
            "label": "Trimming and assembling...",
            "icon": "pencil"
        },
        {
            "label": "Ringing courier...",
            "icon": "pencil"
        },
        {
            "label": "Knock, knock...",
            "icon": "pencil"
        }
    ];

    this.stepDuration = 2200;
    this.totalDuration = this.steps.length * this.stepDuration;

    this.progressBarEl = document.querySelector("[data-progress-bar]");
    this.titleEl = document.querySelector("[data-progress-title]");

    this.$containerEl = $("[data-container]");
    this.animate();

}

ElaborateProgressBar.prototype = {
    animate: function() {
        var $prog = $(this.progressBarEl);
        var $title = $(this.titleEl);

        this.$containerEl.velocity({
            opacity: [1, 0]
        }, {
            duration: 600,
            easing: "easeOutQuad"
        });

        var elem = document.createElement("span");
        this.$textEl = $(elem);
        this.nextStep();
        $title.html(this.$textEl);

        $prog.velocity({ 
            top: [0, "100%"]
        }, {
            /* Velocity's default options: */
            duration: this.totalDuration,
            easing: "linear",
            queue: "",
            begin: null,
            complete: $.proxy(this.animationComplete, this),
            loop: false,
            delay: false,
            display: false,
            mobileHA: true
        });

    },
    nextStep: function() {
        var step;
        if (!this.step) {
            this.step = 0;
        }
        step = this.steps[this.step];

        if (!step) {
            return false;
        }

        this.$textEl.delay(this.stepDuration * .75).velocity({
            opacity: 0,
            top: "-20px"
        }, {
            easing: "easeInOutQuint",
            duration: this.stepDuration / 8,
            complete: $.proxy(this.changeMessage, this, step)
        });

        this.$textEl.velocity({
            opacity: 1,
            top: ["0px", "40px"]
        }, {
            easing: "easeInOutQuint",
            duration: this.stepDuration / 8,
            complete: $.proxy(this.nextStep, this)
        });

        this.step++;
    },

    changeMessage: function(step) {
        this.$textEl.html(step.label);
    },
    
    animationComplete: function(el) {
        // console.log(el);
        var duration = 600;
        this.$containerEl.delay(duration).velocity({
            opacity: [0, 1]
        }, {
            duration: duration,
            easing: "easeOutQuad",
            complete: $.proxy(this.navigate, this)
        })
    },
    navigate: function() {
        window.location = this.el.dataset.elaborateProgressBar;
    }
};


module.exports = (function() {
    var el = document.querySelector("[data-elaborate-progress-bar]");

    if (!el) {
        return;
    }

    return new ElaborateProgressBar(el);
})();
