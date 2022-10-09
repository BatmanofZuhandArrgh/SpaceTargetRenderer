# Modified from https://gist.github.com/chrdiller/ae72a70ce7414ec9d35609536113345c
# Requirements: ubuntu 20.04.4
#Install pyenv
env PYTHON_CFLAGS=-fPIC pyenv install 3.7.8
pyenv virtualenv 3.7.8 bpy_env 

git clone https://git.blender.org/blender.git; cd blender

pyenv local 3.7.8
pip install numpy

git checkout v2.82a
git submodule update --init --recursive
mkdir lib; cd lib; svn checkout https://svn.blender.org/svnroot/bf-blender/tags/blender-2.82-release/lib/linux_centos7_x86_64; cd ..
./build_files/build_environment/install_deps.sh #Do not add any extra tag (--with all or opencollada, etc)
mkdir build; cd build
#Edit here for  virtual env site-packages
cmake .. -DWITH_PYTHON_INSTALL=OFF -DWITH_PYTHON_MODULE=ON -DWITH_INSTALL_PORTABLE=ON -DWITH_CYCLES_EMBREE=OFF -DWITH_MEM_JEMALLOC=OFF -DPYTHON_ROOT_DIR=/path/to/.pyenv/versions/3.7.8/ -DCMAKE_INSTALL_PREFIX=/path/to/venv/lib/python3.7/site-packages/
make -j8
make install

pyenv activate bpy_env
python -c "import bpy; bpy.ops.wm.save_as_mainfile(filepath='my.blend')"
