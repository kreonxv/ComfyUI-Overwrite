import os
import torch
import numpy as np
from PIL import Image

class OverwriteImage:
    OUTPUT_NODE = True
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "output_path": ("STRING", {"default": "C:\\Users\\Cold\\Pictures\\OUTPUTS\\temp.png"}),
                "format": (["PNG", "JPEG", "WEBP", "TIFF", "BMP"], {"default": "PNG"}),
                "quality": ("INT", {"default": 95, "min": 1, "max": 100, "step": 1}),
            },
            "optional": {
                "png_compression": ("INT", {"default": 6, "min": 0, "max": 9, "step": 1}),
                "jpeg_subsampling": (["4:4:4", "4:2:2", "4:2:0"], {"default": "4:2:0"}),
                "webp_lossless": ("BOOLEAN", {"default": False}),
                "tiff_compression": (["none", "lzw", "tiff_deflate", "jpeg"], {"default": "lzw"}),
                "resize_width": ("INT", {"default": 0, "min": 0, "max": 16384}),
                "resize_height": ("INT", {"default": 0, "min": 0, "max": 16384}),
                "resize_method": (["nearest", "bilinear", "bicubic", "lanczos"], {"default": "lanczos"}),
            }
        }
    
    RETURN_TYPES = ()
    FUNCTION = "run"
    CATEGORY = "image"
    
    def get_pil_image(self, image_tensor):
        """Convert tensor to PIL Image"""
        # Handle batch - take first image if batch
        if len(image_tensor.shape) == 4:
            image_tensor = image_tensor[0]
        
        # Convert to numpy and scale to 0-255
        img_np = (image_tensor.cpu().numpy() * 255).astype(np.uint8)
        
        # Convert to PIL Image
        return Image.fromarray(img_np)
    
    def get_resize_filter(self, method):
        """Get PIL resize filter from method name"""
        filters = {
            "nearest": Image.NEAREST,
            "bilinear": Image.BILINEAR,
            "bicubic": Image.BICUBIC,
            "lanczos": Image.LANCZOS
        }
        return filters.get(method, Image.LANCZOS)
    
    def get_jpeg_subsampling(self, subsampling):
        """Convert subsampling string to PIL parameter"""
        mapping = {
            "4:4:4": 0,  # No subsampling
            "4:2:2": 1,  # Medium subsampling
            "4:2:0": 2   # Standard subsampling
        }
        return mapping.get(subsampling, 2)
    
    def run(self, image, output_path, format, quality, 
            png_compression=6, jpeg_subsampling="4:2:0", webp_lossless=False,
            tiff_compression="lzw", resize_width=0, resize_height=0, resize_method="lanczos"):
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Convert tensor to PIL Image
        pil_image = self.get_pil_image(image)
        
        # Handle resize if dimensions are specified
        if resize_width > 0 or resize_height > 0:
            original_width, original_height = pil_image.size
            
            # Calculate dimensions maintaining aspect ratio
            if resize_width > 0 and resize_height > 0:
                new_width, new_height = resize_width, resize_height
            elif resize_width > 0:
                new_width = resize_width
                new_height = int(original_height * (resize_width / original_width))
            else:
                new_height = resize_height
                new_width = int(original_width * (resize_height / original_height))
            
            resize_filter = self.get_resize_filter(resize_method)
            pil_image = pil_image.resize((new_width, new_height), resize_filter)
            print(f"Resized from {original_width}x{original_height} to {new_width}x{new_height}")
        
        # Update output path extension to match format
        base_path, _ = os.path.splitext(output_path)
        output_path = f"{base_path}.{format.lower()}"
        
        # Save with format-specific options
        save_kwargs = {}
        
        if format == "PNG":
            save_kwargs = {
                "format": "PNG",
                "compress_level": png_compression,
                "optimize": True
            }
            print(f"Saving PNG with compression level {png_compression}")
        
        elif format == "JPEG":
            save_kwargs = {
                "format": "JPEG",
                "quality": quality,
                "subsampling": self.get_jpeg_subsampling(jpeg_subsampling),
                "optimize": True
            }
            # Convert RGBA to RGB if necessary
            if pil_image.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", pil_image.size, (255, 255, 255))
                if pil_image.mode == "P":
                    pil_image = pil_image.convert("RGBA")
                background.paste(pil_image, mask=pil_image.split()[-1] if pil_image.mode in ("RGBA", "LA") else None)
                pil_image = background
            print(f"Saving JPEG with quality {quality}, subsampling {jpeg_subsampling}")
        
        elif format == "WEBP":
            save_kwargs = {
                "format": "WEBP",
                "lossless": webp_lossless,
                "quality": quality if not webp_lossless else 100,
                "method": 6  # Best compression
            }
            print(f"Saving WebP ({'lossless' if webp_lossless else f'lossy, quality {quality}'})")
        
        elif format == "TIFF":
            save_kwargs = {
                "format": "TIFF",
                "compression": tiff_compression if tiff_compression != "jpeg" else "jpeg",
            }
            if tiff_compression == "jpeg":
                save_kwargs["quality"] = quality
            print(f"Saving TIFF with {tiff_compression} compression")
        
        elif format == "BMP":
            save_kwargs = {
                "format": "BMP"
            }
            print("Saving BMP (uncompressed)")
        
        # Save the image
        try:
            pil_image.save(output_path, **save_kwargs)
            
            # Get file size
            file_size = os.path.getsize(output_path)
            size_mb = file_size / (1024 * 1024)
            
            print(f"✓ Image saved successfully to: {output_path}")
            print(f"  Size: {file_size:,} bytes ({size_mb:.2f} MB)")
            print(f"  Dimensions: {pil_image.size[0]}x{pil_image.size[1]}")
            print(f"  Mode: {pil_image.mode}")
            
        except Exception as e:
            print(f"✗ Error saving image: {str(e)}")
            raise RuntimeError(f"Failed to save image: {str(e)}")
        
        return ()