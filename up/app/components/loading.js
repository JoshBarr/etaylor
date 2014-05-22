var ElaborateProgressBar = function(el, options) {
    this.el = el;
    this.steps = [
        {
            "label": "Briefing the designer...",
            "icon": "icon-designer"
        },
        {
            "label": "Opening editor...",
            "icon": "icon-editor"
        },
        {
            "label": "Sending art to the printer...",
            "icon": "icon-courier-bike"
        },
        {
            "label": "Printing art...",
            "icon": "icon-printer"
        },
        {
            "label": "Trimming and assembling...",
            "icon": "icon-scissors"
        },
        {
            "label": "Ringing courier...",
            "icon": "icon-courier"
        },
        {
            "label": "Knock, knock...",
            "icon": "icon-door"
        }
    ];

    this.step = 0;

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
        var elemIcon = document.createElement("span");
        this.$textEl = $(elem);
        this.$iconEl = $(elemIcon);
        
        $title.html("");
        $title
            .append(this.$textEl)
            .append(this.$iconEl);

        this.changeMessage();

        var percentageStep = 100 / this.steps.length;
        var wait = (this.stepDuration * .75);
        var go = this.stepDuration * .25;
        var last = this.steps.length - 1;

        var $brush = $("[data-ui-brush]");
        $brush.css({"z-index": 0});
        $prog.css({"z-index": 1});

        for (var i = 0; i < this.steps.length; i++) {

            var complete = false;

            if (i === last) {
                complete = $.proxy(this.animationComplete, this);
            }

            if (i === last - 1) {
                complete = function() {
                    $brush.velocity({
                        opacity: 0
                    }, {
                        duration: go * 2
                    });
                }
            }

            $prog
                .velocity({
                    top: (100 - (percentageStep * (i + 1))) + "%"
                }, {
                    duration: go,
                    easing: "spring",
                    complete: complete
                })
                .delay(wait)
        }

            
    },

    showStep: function() {
        this.$textEl
            .velocity({
                opacity: 1,
                top: ["0px", "40px"]
            }, {
                easing: "easeInOutQuad",
                duration: this.stepDuration * .125,
                // complete: $.proxy(this.nextStep, this)
            });
        this.$iconEl
            .velocity({
                opacity: [1,0],
                top: ["0px", "100px"]
            }, {
                duration: this.stepDuration * .125,
                easing: "easeInOutQuad",
            })
    },

    hideStep: function() {
        this.$textEl
            .delay(this.stepDuration * .75)
            .velocity({
                opacity: 0,
                top: "-20px"
            }, {
                easing: "easeInOutQuad",
                duration: this.stepDuration * .125,
                complete: $.proxy(this.changeMessage, this)
            });

        this.$iconEl
            .delay(this.stepDuration * .75)
            .velocity({
                opacity: [0,1],
                top: ["-100px", "0px"]
            }, {
                duration: this.stepDuration * .125,
                easing: "easeInOutQuad",
            });
    },


    changeMessage: function() {
        var html;
        var stepObj = this.steps[this.step];
        var lastStepNum = this.steps.length;

        if (!stepObj) {
            return;
        }

        html = "<span class='i icon-medium " +  stepObj.icon + "'></span>";
       
        this.$textEl.html(stepObj.label);
        this.$iconEl.html(html);

        if (this.step > lastStepNum) {
            return;
        }

        if (this.step === 0) {
            this.step++;
        } else {
            this.step++;
            this.showStep(); 
        }

        if (this.step === lastStepNum) {
            return;
        }

        this.hideStep();
    },
    
    animationComplete: function(el) {
        var duration = 600;
        this.$containerEl.delay(duration).velocity({
            opacity: [0, 1]
        }, {
            duration: duration,
            easing: "easeOutQuad",
            complete: $.proxy(this.navigate, this)
        });
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
