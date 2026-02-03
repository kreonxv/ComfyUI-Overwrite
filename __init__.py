from .overwrite_video import OverwriteVideo
from .overwrite_image import OverwriteImage

NODE_CLASS_MAPPINGS = {
    "Overwrite Video": OverwriteVideo,
    "OverwriteImage": OverwriteImage
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Overwrite Video": "Overwrite Video (No Suffix, Overwrite)",
    "OverwriteImage": "Overwrite Image (Enhanced)"
}