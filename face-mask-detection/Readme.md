# Running face mask detection on NVIDIA Jetson Nano.
## Note: Currently Jetson Nano does not support INT8. So will stick to fp16

## Install Deepstream on Jetson Nano (Refer [NVIDIA's webpage](https://docs.nvidia.com/metropolis/deepstream/dev-guide/text/DS_Quickstart.html#jetson-setup))
### Install Dependencies
Enter the following commands to install the prerequisite packages:
```
$ sudo apt install \
libssl1.0.0 \
libgstreamer1.0-0 \
gstreamer1.0-tools \
gstreamer1.0-plugins-good \
gstreamer1.0-plugins-bad \
gstreamer1.0-plugins-ugly \
gstreamer1.0-libav \
libgstrtspserver-1.0-0 \
libjansson4=2.11-1
```

#### Install librdkafka (to enable Kafka protocol adaptor for message broker)
* Clone the librdkafka repository from GitHub:
```
$ git clone https://github.com/edenhill/librdkafka.git
```
* Configure and build the library:
```
cd librdkafka
git reset --hard 7101c2310341ab3f4675fc565f64f0967e135a6a
./configure
make
sudo make install
```
* Copy the generated libraries to the deepstream directory:
```
sudo mkdir -p /opt/nvidia/deepstream/deepstream-5.0/lib
sudo cp /usr/local/lib/librdkafka* /opt/nvidia/deepstream/deepstream-5.0/lib
```

####  Install NVIDIA V4L2 GStreamer plugin
Check if gstreamer is already installed
```
man gstreamer
```

If not,
* Open the apt source configuration file in a text editor, for example: 
```
sudo vi /etc/apt/sources.list.d/nvidia-l4t-apt-source.list
```

* Change the repository name and download URL in the deb commands shown below:
```
deb https://repo.download.nvidia.com/jetson/common r32.4 main
deb https://repo.download.nvidia.com/jetson/<platform> r32.4 main
```
Where 'platform' identifies the platform’s processor:
t186 for Jetson TX2 series

t194 for Jetson AGX Xavier series or Jetson Xavier NX

t210 for Jetson Nano or Jetson TX1

For example, if your platform is Jetson Xavier NX:
```
deb https://repo.download.nvidia.com/jetson/common r32.4 main
deb https://repo.download.nvidia.com/jetson/t194 r32.4 main
```
* Save and close the source configuration file.

* Enter the commands:
```
sudo apt update
sudo apt install --reinstall nvidia-l4t-gstreamer
```
If apt prompts you to choose a configuration file, reply Y for yes (to use the NVIDIA updated version of the file).

### Install the DeepStream SDK
Using the apt-server

* Open the apt source configuration file in a text editor, using a command similar to
```
sudo vi /etc/apt/sources.list.d/nvidia-l4t-apt-source.list
```
* Change the repository name and download URL in the deb commands shown below: 
```
deb https://repo.download.nvidia.com/jetson/common r32.4 main
```
* Save and close the source configuration file.

* Enter the commands:
```
sudo apt update
sudo apt install deepstream-5.0
```

## Installing NVIDIA tlt-converter
* For the Jetson platform, the tlt-converter is available to download in the [dev zone](https://developer.nvidia.com/tlt-converter-trt71). 
Once the tlt-converter is downloaded, please follow the instructions below to generate a TensorRT engine.
Check if version of tlt-converter downloaded matches that of  tensorRT installed on Jetson
```
dpkg -l | grep nvinfer
```


### Convert .etlt cmodel to  .trt engine
* Clone the git repo
```
git clone https://github.com/edgepipes.git
cd edgepipes/face-mask-detection
```
* Unzip tlt-converter-trt7.1.zip on the target machine.
```
unzip <path>/tlt-converter-trt7.1.zip . 
chmod +x tlt_converter
```
* Convert .etlt. model to .trt engine
```
chmod +x convert_trt.sh
./convert_trt
```

## Run Deepstream
```
deepstream-app -c ds_configs/deepstream_app_source1_camera_masknet_gpu.txt 
```

