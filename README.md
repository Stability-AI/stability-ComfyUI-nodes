# Custom nodes for [ComfyUI](https://github.com/comfyanonymous/ComfyUI)

git clone this repo to your ComfyUI/custom_nodes folder, it should look like: ComfyUI/custom_nodes/stability-ComfyUI-nodes

These nodes will appear in the stability section.

### ControlLoraSave

This node can be used to create a Control Lora from a model and a controlnet. It will take the difference between the model weights and the controlnet weights and store that difference in Lora format.
