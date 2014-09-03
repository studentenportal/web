# Set this to the root of your project when deployed:
http_path = "/"
css_dir = "apps/front/static/css"
fonts_dir = "apps/front/static/fonts"
sass_dir = "apps/front/static/sass"
images_dir = "apps/front/static/img"
javascripts_dir = "apps/front/static/js"

# Make a copy of sprites with a name that has no uniqueness of the hash.
# http://stackoverflow.com/questions/9183133/how-to-turn-off-compass-sass-cache-busting/9332472#9332472
on_sprite_saved do |filename|
  if File.exists?(filename)
    FileUtils.cp filename, filename.gsub(%r{-s[a-z0-9]{10}\.png$}, '.png')
  end
end

# Replace in stylesheets generated references to sprites
# by their counterparts without the hash uniqueness.
on_stylesheet_saved do |filename|
  if File.exists?(filename)
    css = File.read filename
    File.open(filename, 'w+') do |f|
      f << css.gsub(%r{-s[a-z0-9]{10}\.png}, '.png')
    end
  end
end
