# Custom nodes for [ComfyUI](https://github.com/comfyanonymous/ComfyUI)

git clone this repo to your ComfyUI/custom_nodes folder, it should look like: ComfyUI/custom_nodes/stability-ComfyUI-nodes

On the standalone you can run: standalone_install_requirements.bat to install the dependencies. On a manual install you should: ```pip install -r requirements.txt```


These nodes will appear in the stability section.

### ControlLoraSave

This node can be used to create a Control Lora from a model and a controlnet. It will take the difference between the model weights and the controlnet weights and store that difference in Lora format.
