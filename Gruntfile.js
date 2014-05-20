module.exports = function(grunt) {

  // Project configuration.
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
    uglify: {
      options: {
        banner: '/*! <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> */\n'
      },
      build: {
        src: 'src/<%= pkg.name %>.js',
        dest: 'build/<%= pkg.name %>.min.js'
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
    }
    
  });

  // Load the plugin that provides the "uglify" task.
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-contrib-concat');
  grunt.loadNpmTasks('grunt-sass');
  grunt.loadNpmTasks('grunt-browserify');

  // Default task(s).
  grunt.registerTask('default', ['uglify']);


  grunt.registerTask("js", ["browserify", "concat"]);

};