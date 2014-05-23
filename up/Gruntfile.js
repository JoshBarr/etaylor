module.exports = function(grunt) {

  // Project configuration.
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
    uglify: {
      options: {
        banner: '/*! <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> */\n'
      },
      build: {
        src: 'static/js/site.js',
        dest: 'static/js/site.js'
      }
    },
    cssmin: {
      combine: {
        files: {
          'static/css/screen.css': ['static/css/screen.css']
        }
      }
    },
    concat: {
      dist: {
        dest: "static/js/site.js",
        src: [
          "app/lib/jquery.js",
          "app/lib/velocity.js",
          "build/site.js"
        ]
      }
    },
    watch: {
      sass: {
        files: ["app/sass/**/*.scss"],
        tasks: ["sass:dev"],
        options: {
          livereload: true
        }
      },
      js: {
        files: ["app/**/*.js"],
        tasks: ["js"],
        options: {
          livereload: true
        }
      }
    },
    sass: {
      dev: {
        files: {
          "static/css/screen.css": "app/sass/screen.scss"
        }
      }
    },
    browserify: {
      dist: {
        files: {
          'build/site.js': ['app/components/**/*.js', 'app/site.js'],
        },
        options: {
          // transform: ['coffeeify']
        }
      }
    },
    grunticon: {
      site: {
          files: [{
              expand: true,
              cwd: 'static/images/svg/',
              src: ['*.svg', '*.png'],
              dest: "static/css/svg"
          }],
          options: {
          }
      }
    }
    
  });

  // Load the plugin that provides the "uglify" task.
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-contrib-concat');
  grunt.loadNpmTasks('grunt-sass');
  grunt.loadNpmTasks('grunt-browserify');
  grunt.loadNpmTasks('grunt-grunticon');
  grunt.loadNpmTasks('grunt-contrib-cssmin');


  // Default task(s).
  grunt.registerTask('default', ['uglify']);


  grunt.registerTask("js", ["browserify", "concat"]);
  grunt.registerTask("icon", ["grunticon"]);
  grunt.registerTask("dist", ["uglify", "cssmin"]);

};