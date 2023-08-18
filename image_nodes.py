
class GetImageSize:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("width", "height")

    FUNCTION = "get_size"

    CATEGORY = "stability/image"

    def get_size(self, image):
        _, height, width, _ = image.shape
        return (width, height)

NODE_CLASS_MAPPINGS = {
    "GetImageSize": GetImageSize
}

NODE_DISPLAY_NAME_MAPPINGS = {
}
