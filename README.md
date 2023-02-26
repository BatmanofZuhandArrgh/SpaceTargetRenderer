# SpaceTargetRenderer
Rendering space targets (CubeSats, debris and other satellites) using Blender Python API

**Installation guide**
1. Install blender python module:
- Follow the bpy_module_setup.sh

2. Clone the github repo
```
cd SpaceTargetRenderer
pip install -r requirements.txt
```

3. Download asset.zip at 
https://drive.google.com/file/d/15pv2eMMh3eyLeLg5MgKapQ834Nd5gV58/view?usp=sharing

And unzip at SpaceTargetRenderer main directory
```
unzip asset.zip
```

4. Install blender 2.82
```
wget https://download.blender.org/release/Blender2.82/blender-2.82-linux64.tar.xz
tar xf blender-2.82-linux64
```

**Running guide**
I. Generate 1 dataset:

1. Edit paths in pipeline_config.yaml
+ blender_exe: path to blender execute file
+ WIP_blend_file_path: leave empty
+ Edit label_dict to edit the label mapping
+ Edit other values to modify generation process

2. Run generation
'''
python render.py
'''

The output dataset should be in output_dir, in yolov1 format (https://github.com/AlexeyAB/Yolo_mark/issues/60)

II. Generate multiple datasets:

1. Create multiple yaml files like pipeline_config.yaml, as explained in pipeline_config_notes.md

2. Input config_paths varible as the list of paths to pipeline_config yamls, in the file render_datasets.py

3. Run generation
'''
python render_datasets.py
'''
