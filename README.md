# GrayscaleImage ADT
Sample usage:
```python
from grayscale_adt import GrayscaleImage

# Loading file
image = GrayscaleImage.from_file('image.png')

# Modifying file
image.setitem(row=5, col=10, value=20)

# Compression
data = image.lzw_compression()

# Decompression
image = GrayscaleImage.lzw_decompression(data)

# Get compression ratio (uncompressed / compressed)
ratio = image.lzw_compression_ratio()

# Saving
image.save('modified.png')
```