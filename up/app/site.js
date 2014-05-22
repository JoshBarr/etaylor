var Site = (function(window, document, $) {
    
    var config = require("./components/config.js");
    var zip = require("./components/zip.js");
    var loading = require("./components/loading.js");
    var nav = require("./components/nav.js");
    var question = require("./components/question.js");
    var album = require("./components/album.js");
    var PageTransitions = require("./components/page-transitions.js");

    var $doc = config.$doc;
    var $stage = config.$stage;


    // ----------------------------------------------------
    // App
    // ----------------------------------------------------
    var Site = function() {
    
    };

    Site.prototype = {
        init: function() {
           
            nav.init();
            PageTransitions.init();

            var $step = $("[data-step]");

            if ($step.data("step") === "start") {
                PageTransitions.showBrush(0);
            }

            if ($step.data("step") === "credits") {
                PageTransitions.showBrush(0);
            }

            if ($step.data("step") === "question") {
                question.init();
                PageTransitions.showBrush(0);
            }

            if ($step.data("step") === "share") {
                PageTransitions.showBrush(0);
            }

            if ($step.data("step") === "album") {
                album.init(zip);
                zip.init();
                PageTransitions.showBrush(500, 900);
            }

            return this;
        }
    };

    var site = new Site();

    // ----------------------------------------------------
    // Boot
    // ----------------------------------------------------
    $doc.ready(function() {
        return site.init();
    });

    return site;

})(window, document, $);
