# Blender Add-on Template
This is a boilerplate template to help you organize your Blender add-on code. You can even install and enable the template as-is, even though it doesn't do anything. Happy Blending!

## How to download
Ready to make your own Blender add-on? Download the latest code, copy it to your project folder, and get started!
    
    git clone https://github.com/lunadigital/blender-addon-template
    cp ./blender-addon-template/* /path/to/your/project/folder



# Installation
The addon is installed using the Blender UI `Menu > Edit > Preferences > Addons > Install...`.

# Requirements
The addon uses the python module pillow to generate the texture images. The module has to be installed to the 
python instance that ships with the Blender installation. For this, open a command line where the binary is located 
(usually `<Blender version>/python/bin`) and execute the following python call:
```
python -m pip install pillow
```

# Compatibility
Developed using Blender 3.4