import torch
import comfy.model_management
import comfy.utils
import folder_paths
import os

CLAMP_QUANTILE = 0.99

def extract_lora(diff, rank):
    conv2d = (len(diff.shape) == 4)
    kernel_size = None if not conv2d else diff.size()[2:4]
    conv2d_3x3 = conv2d and kernel_size != (1, 1)
    out_dim, in_dim = diff.size()[0:2]
    rank = min(rank, in_dim, out_dim)

    if conv2d:
        if conv2d_3x3:
            diff = diff.flatten(start_dim=1)
        else:
            diff = diff.squeeze()


    U, S, Vh = torch.linalg.svd(diff.float())
    U = U[:, :rank]
    S = S[:rank]
    U = U @ torch.diag(S)
    Vh = Vh[:rank, :]

    dist = torch.cat([U.flatten(), Vh.flatten()])
    hi_val = torch.quantile(dist, CLAMP_QUANTILE)
    low_val = -hi_val

    U = U.clamp(low_val, hi_val)
    Vh = Vh.clamp(low_val, hi_val)
    if conv2d:
        U = U.reshape(out_dim, rank, 1, 1)
        Vh = Vh.reshape(rank, in_dim, kernel_size[0], kernel_size[1])
    return (U, Vh)

class ControlLoraSave:
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()

    @classmethod
    def INPUT_TYPES(s):
        return {"required": { "model": ("MODEL",),
                              "control_net": ("CONTROL_NET",),
                              "filename_prefix": ("STRING", {"default": "controlnet_loras/ComfyUI_control_lora"}),
                              "rank": ("INT", {"default": 64, "min": 0, "max": 1024, "step": 8}),
                            },}
    RETURN_TYPES = ()
    FUNCTION = "save"
    OUTPUT_NODE = True

    CATEGORY = "stability/controlnet"

    def save(self, model, control_net, filename_prefix, rank):
        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(filename_prefix, self.output_dir)

        output_sd = {}
        prefix_key = "diffusion_model."
        stored = set()

        comfy.model_management.load_models_gpu([model])
        f = model.model_state_dict()
        c = control_net.control_model.state_dict()

        for k in f:
            if k.startswith(prefix_key):
                ck = k[len(prefix_key):]
                if ck not in c:
                    ck = "control_model.{}".format(ck)
                if ck in c:
                    model_weight = f[k]
                    if len(model_weight.shape) >= 2:
                        diff = c[ck].float().to(model_weight.device) - model_weight.float()
                        out = extract_lora(diff, rank)
                        name = ck
                        if name.endswith(".weight"):
                            name = name[:-len(".weight")]
                        out1_key = "{}.up".format(name)
                        out2_key = "{}.down".format(name)
                        output_sd[out1_key] = out[0].contiguous().half().cpu()
                        output_sd[out2_key] = out[1].contiguous().half().cpu()
                    else:
                        output_sd[ck] = c[ck]
                        print(ck, c[ck].shape)
                    stored.add(ck)

        for k in c:
            if k not in stored:
                output_sd[k] = c[k].half()
        output_sd["lora_controlnet"] = torch.tensor([])

        output_checkpoint = f"{filename}_{counter:05}_.safetensors"
        output_checkpoint = os.path.join(full_output_folder, output_checkpoint)

        comfy.utils.save_torch_file(output_sd, output_checkpoint, metadata=None)
        return {}

NODE_CLASS_MAPPINGS = {
    "ControlLoraSave": ControlLoraSave
}

NODE_DISPLAY_NAME_MAPPINGS = {
}
