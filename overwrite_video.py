import os
import subprocess
import tempfile
import torch
import numpy as np
from PIL import Image

class OverwriteVideo:
    OUTPUT_NODE = True
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "output_path": ("STRING", {"default": "C:\\Users\\Cold\\Pictures\\OUTPUTS\\temp.mp4"}),
                "fps": ("INT", {"default": 24, "min": 1, "max": 120}),
                "codec": (["h264", "prores", "prores_ks"], {"default": "h264"}),
                "quality": (["low", "medium", "high", "very_high", "lossless"], {"default": "high"}),
            },
            "optional": {
                "bitrate": ("STRING", {"default": "auto"}),  # e.g., "5M", "10M", "20M"
                "prores_profile": (["proxy", "lt", "standard", "hq", "4444", "4444xq"], {"default": "standard"}),
            }
        }
    
    RETURN_TYPES = ()
    FUNCTION = "run"
    CATEGORY = "video"
    
    def get_h264_settings(self, quality, bitrate):
        """Get H.264 encoding settings based on quality preset"""
        settings = {
            "low": {"crf": "28", "preset": "fast"},
            "medium": {"crf": "23", "preset": "medium"},
            "high": {"crf": "18", "preset": "slow"},
            "very_high": {"crf": "15", "preset": "slower"},
            "lossless": {"crf": "0", "preset": "veryslow"}
        }
        
        params = ["-c:v", "libx264"]
        
        if bitrate and bitrate.lower() != "auto":
            # Use bitrate mode
            params.extend(["-b:v", bitrate, "-maxrate", bitrate, "-bufsize", f"{int(bitrate[:-1])*2}M"])
        else:
            # Use CRF mode (constant quality)
            params.extend(["-crf", settings[quality]["crf"]])
        
        params.extend([
            "-preset", settings[quality]["preset"],
            "-pix_fmt", "yuv420p"
        ])
        
        return params
    
    def get_prores_settings(self, prores_profile, codec):
        """Get ProRes encoding settings"""
        profile_map = {
            "proxy": "0",
            "lt": "1",
            "standard": "2",
            "hq": "3",
            "4444": "4",
            "4444xq": "5"
        }
        
        if codec == "prores_ks":
            # prores_ks (newer, better quality)
            params = [
                "-c:v", "prores_ks",
                "-profile:v", profile_map[prores_profile],
                "-vendor", "apl0",
                "-pix_fmt", "yuv422p10le" if prores_profile not in ["4444", "4444xq"] else "yuva444p10le"
            ]
        else:
            # prores (legacy)
            params = [
                "-c:v", "prores",
                "-profile:v", profile_map[prores_profile],
                "-pix_fmt", "yuv422p10le" if prores_profile not in ["4444", "4444xq"] else "yuva444p10le"
            ]
        
        return params
    
    def run(self, images, output_path, fps, codec, quality, bitrate="auto", prores_profile="standard"):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Determine output extension based on codec
        base_path, ext = os.path.splitext(output_path)
        if codec in ["prores", "prores_ks"] and ext.lower() not in [".mov", ".mxf"]:
            output_path = base_path + ".mov"
            print(f"ProRes codec requires .mov container. Changed output to: {output_path}")
        elif codec == "h264" and ext.lower() not in [".mp4", ".mkv"]:
            output_path = base_path + ".mp4"
            print(f"H.264 codec works best with .mp4 container. Changed output to: {output_path}")
        
        # Temp folder for frames
        with tempfile.TemporaryDirectory() as tmp:
            # Save frames as PNG
            for i, img in enumerate(images):
                img = (img.cpu().numpy() * 255).astype(np.uint8)
                Image.fromarray(img).save(f"{tmp}/{i:06d}.png")
            
            # Build FFmpeg command
            cmd = [
                "ffmpeg",
                "-y",  # Force overwrite
                "-framerate", str(fps),
                "-i", f"{tmp}/%06d.png"
            ]
            
            # Add codec-specific settings
            if codec == "h264":
                cmd.extend(self.get_h264_settings(quality, bitrate))
            else:
                cmd.extend(self.get_prores_settings(prores_profile, codec))
            
            # Output path
            cmd.append(output_path)
            
            # Print command for debugging
            print(f"Running FFmpeg command: {' '.join(cmd)}")
            
            # Execute FFmpeg
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print("FFmpeg Error Output:")
                print(result.stderr)
                raise RuntimeError(f"FFmpeg failed with return code {result.returncode}")
            else:
                print("FFmpeg Success!")
                print(f"Video saved to: {output_path}")
                if result.stdout:
                    print(result.stdout)
        
        return ()

NODE_CLASS_MAPPINGS = {
    "OverwriteVideo": OverwriteVideo
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "OverwriteVideo": "Overwrite Video (Enhanced)"
}