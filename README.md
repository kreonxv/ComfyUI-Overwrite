# ComfyUI-Overwrite

These nodes save and overwrite files on disk.

Nodes and relevant save options:

- OverwriteImage: saves an image to disk and overwrites the target file.
  - Formats/options:
    - PNG: `png_compression`
    - JPEG: `quality`, `jpeg_subsampling` (alpha flattened to white)
    - WEBP: `quality`, `webp_lossless`
    - TIFF: `tiff_compression`
    - BMP: no extra options
  - Resize: `resize_width`, `resize_height`, `resize_method`

- OverwriteVideo: encodes a sequence of images into a video and overwrites the target file.
  - Codecs/options:
    - H.264: `fps`, `quality`, `bitrate`
    - ProRes / prores_ks: `prores_profile`


