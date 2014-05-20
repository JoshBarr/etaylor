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
    this._length = minLength || 1;
    this.onUserInput = false;
};

NotNull.prototype.validate = function(field) {
    var length, emptyStr, isNotEmpty;

    length = field.value.length;
    // emptyStr = new RegExp("", "g");
    isNotEmpty = field.value.match(/^\s*\S.*$/) !== null;
    isLongEnough = (length >= this._length);

    if (isLongEnough && isNotEmpty) {
        return true;
    }

    return false;
};

NotNull.prototype.message = function() {
    var message = ["Too short!"];

    if (this._length) {
        message.push(" Make it longer than " + this._length + " character");
        if (this._length > 1) {
            message.push("s");
        }
        message.push(".");
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
            return true;
        }

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
        this.$submit = $("[data-submit]");

        this.$submit.on("click", $.proxy(this.handleSubmit, this));

        this.addField(new Field(this.textarea, {
            validation: [
                new NotNull(4),
                new MaxLength(80)
            ]
        }));
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

        console.log(errors);

        if (errors.length) {
            return false;
        }

        return this.$el.trigger("submit");

    },
    handleSubmit: function(e) {
        e.preventDefault();
        e.stopPropagation();
        this.checkFields();
    }
};

module.exports = new Form();