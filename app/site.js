var Site = (function(window, document, $) {
    
    var config = require("./components/config.js");
    var zip = require("./components/zip.js");
    var loading = require("./components/loading.js");
    var nav = require("./components/nav.js");
    var question = require("./components/question.js");

    var $doc = config.$doc;


    // ----------------------------------------------------
    // App
    // ----------------------------------------------------
    var Site = function() {
    
    };

    Site.prototype = {
        init: function() {
            zip.init();
            nav.init();
            
            var $step = $("[data-step]");

            if ($step.data("step") === "question") {
                question.init();
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
