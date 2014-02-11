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
    watch: {
      sass: {
        files: ["static/sass/**/*.scss"],
        tasks: ["sass:dev"],
        options: {
          livereload: true
        }
      },
      js: {
        files: ["static/js/**/*.js"],
        tasks: ["uglify"],
        options: {
          livereload: true
        }
      }
    },
    sass: {
      dev: {
        files: {
          "static/css/screen.css": "static/sass/screen.scss"
        }
      }
    }
  });

  // Load the plugin that provides the "uglify" task.
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-sass');

  // Default task(s).
  grunt.registerTask('default', ['uglify']);

};