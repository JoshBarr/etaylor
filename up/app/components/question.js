var AnimateOut = require("./animate-out.js");
var config = require("./config.js");


if (!String.prototype.trim) {
    String.prototype.trim = function() {
        return this.replace(/^\s+|\s+$/g,'');
    }
}



/**
 * [MaxLength description]
 * @param {[type]} length [description]
 */
var MaxLength = function(length) {
    this._length = length;
    this.onUserInput = true;
};

MaxLength.prototype.validate = function(field) {
    var length = field.value.length;

    this.currentLength = length;

    if (length < this._length) {
        return true;
    }

    return false;
};

MaxLength.prototype.message = function() {
    return [this._length - this.currentLength, " characters remaining"].join("");
};




/**
 * [MaxLength description]
 * @param {[type]} length [description]
 */
var NotNull = function(minLength) {
    this._length = minLength || 2;
    this.onUserInput = false;
};

NotNull.prototype.validate = function(field) {
    var length, emptyStr, notNull;

    length = field.value.length;
    // emptyStr = new RegExp("", "g");
    notNull = field.value.match(/\S/) !== null;
    isLongEnough = (length >= this._length);

    if (isLongEnough && notNull) {
        return true;
    }

    return false;
};

NotNull.prototype.message = function() {
    var message = ["Too short!"];

    if (this._length) {
        message.push(" Make it at least " + this._length + " character");
        if (this._length > 1) {
            message.push("s");
        }
        message.push(" long.");
    }

    return message.join("");
};





/**
 * Field
 * @param {[type]} element [description]
 */
var Field = function(element, options) {
    this.el = element;
    this.$el = $(this.el);
    this.$el.on("change keyup paste", $.proxy(this.validate, this));

    if (options.validation) {
        this.validation = options.validation;
    }

};

Field.prototype = {
    validate: function(e) {
        var i, len, validator, isValid, errors, el;
        len = this.validation.length
        
        errors = [];
        el = this.el;

        for (i = 0; i < len; i++) {
            
            validator = this.validation[i];
            // console.log(validator);
            if (e && !validator.onUserInput) {
                continue;
            }

            result = validator.validate(el);
            
            if (!result) {
                errors.push(validator.message());
            }
        }

        this.errors = errors;
        this.showErrors();

        if (!errors.length) {
            this.$el.trigger("validation:success");
            return true;
        }

        this.$el.trigger("validation:error");
        
        // return true;
    },

    showErrors: function() {
        var errors = this.errors;
        if (errors.length) {            
            if (!this.errorEl) {
                this.errorEl = document.createElement("span");
                this.$errorEl = $(this.errorEl);
                this.$errorEl.addClass("question__errors");
                this.el.parentElement.insertBefore(this.errorEl, this.el.nextSibling);
            }

            this.errorEl.innerHTML = errors.join(" ");
            this.$errorEl.velocity({
                opacity: 1
            }, { 
                duration: 100
            });

        } else {
            if (this.$errorEl) {
                this.$errorEl.velocity({
                    opacity: 0
                }, { 
                    duration: 100
                });
            }
        }
    }
};




var Form = function() {
    this.fields = [];
};

Form.prototype = {
    init: function() {
        this.el = document.querySelector("[data-question-form]");
        this.textarea = document.getElementById("question");
        this.$el = $(this.el);
        var $submit = $("[data-submit]");
        var $questionText = $("[data-question-text]");
        this.$submit = $submit;

        this.$submit.on("click", $.proxy(this.handleSubmit, this));

        this.addField(new Field(this.textarea, {
            validation: [
                new NotNull(2),
                new MaxLength(80)
            ]
        }));

        var $el = $(this.textarea);
        $el.trigger("click");
        $el.focus();
            
        var self = this;
        var ENTER = 13;

        // Prevent newlines in the field.
        $el.on("keydown", function(e) {
            if (e.keyCode === ENTER && !e.shiftKey) {
                // prevent default behavior
                e.preventDefault();
                // self.handleSubmit.call(self, e);
                return false;
            }
        });


        $el.on("keyup change", function(e) {
            var val = e.target.value;
            if (!val.length) {
                if ($questionText.hasClass('question__text--disabled')) {                
                    $questionText.removeClass('question__text--disabled');
                }
            }

            if (e.keyCode === ENTER && !e.shiftKey) {
                self.handleSubmit.call(self, e);
            }
        });

        $el.on("validation:error", function() {
            
            if ($questionText.hasClass('question__text--disabled')) {                
                $questionText.removeClass('question__text--disabled');
            }

            if (!$submit.hasClass('btn--disabled')) {
                $submit.addClass('btn--disabled');
            }
        });

        $el.on("validation:success", function() {
            if (!$questionText.hasClass('question__text--disabled')) {                
                $questionText.addClass('question__text--disabled');
            }

            if ($submit.hasClass('btn--disabled')) {
                $submit.removeClass('btn--disabled');
                
            }
        });

    },
    addField: function(field) {
        this.fields.push(field);
        return field;
    },
    checkFields: function() {
        var i = 0, len, field, errors;
        len = this.fields.length;

        errors = [];

        for (i; i < len; i++) {
            field = this.fields[i];

            if (!field.validate()) {
                field.showErrors();
                errors.push(field);
            }
            field.el.value = field.el.value.trim();
        }


        if (errors.length) {
            return false;
        }

        new AnimateOut(config.$stage, {
            opacity: 0,
        }, {
            duration: 300,
            easing: "easeInQuad",
            complete: $.proxy(this.animComplete, this)
        });


    },

    animComplete: function() {
        return this.$el.trigger("submit");
    },

    handleSubmit: function(e) {
        if (e) {        
            e.preventDefault();
            e.stopPropagation();
        }
        this.checkFields();
    }
};

module.exports = new Form();