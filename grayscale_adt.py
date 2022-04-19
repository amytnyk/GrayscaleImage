from typing import List, Tuple
from PIL import Image, ImageOps
from arrays import Array2D


class LZW:
    MAX_DICT_BYTES = 2

    @staticmethod
    def encode(data: bytes) -> bytes:
        dictionary = {(i,): i for i in range(256)}
        result = bytearray()

        def add(num: int):
            result.extend(num.to_bytes(LZW.MAX_DICT_BYTES, "big"))

        w = ()
        for c in data:
            wc = (*w, c)
            if wc in dictionary:
                w = wc
            else:
                add(dictionary[w])
                if len(dictionary) < (1 << (8 * LZW.MAX_DICT_BYTES)):
                    dictionary[wc] = len(dictionary)
                w = (c,)
        if w:
            add(dictionary[w])
        return bytes(result)

    @staticmethod
    def decode(data: bytes) -> bytes:
        dictionary: List[Tuple] = [(i,) for i in range(256)]
        result = bytearray()

        def read(index: int) -> int:
            return int.from_bytes(
                bytes(data[index:index + LZW.MAX_DICT_BYTES]),
                "big"
            )

        w = dictionary[read(0)]
        result.extend(w)

        for i in range(LZW.MAX_DICT_BYTES, len(data), 2):
            if (k := read(i)) < len(dictionary):
                entry = dictionary[k]
            else:
                entry = (*w, w[0])
            result.extend(entry)
            dictionary.append((*w, entry[0]))
            w = entry
        return bytes(result)


class GrayscaleImage:
    def __init__(self, rows: int, cols: int):
        self.array = Array2D(rows, cols)

    def getitem(self, row: int, col: int) -> int:
        return self.array[row, col]

    def setitem(self, row: int, col: int, value: int):
        self.array[row, col] = value

    def width(self):
        return self.array.num_cols()

    def height(self):
        return self.array.num_rows()

    def clear(self, value: int):
        self.array.clear(value)

    def save(self, path: str):
        with Image.new('L', (self.width(), self.height())) as image:
            pixels = image.load()
            for row in range(self.height()):
                for col in range(self.width()):
                    pixels[col, row] = self.getitem(row, col)

            image.save(path, 'PNG')

    @staticmethod
    def from_file(path: str):
        with Image.open(path) as image:
            image_grayscale = ImageOps.grayscale(image)
            im = GrayscaleImage(*image_grayscale.size[::-1])
            pixels = image_grayscale.load()
            for i in range(image_grayscale.size[1]):
                for j in range(image_grayscale.size[0]):
                    im.setitem(i, j, pixels[j, i])

            return im

    def lzw_compression(self) -> bytes:
        header = self.height().to_bytes(4, "big") + \
                 self.width().to_bytes(4, "big")
        data = [self.getitem(i, j)
                for i in range(self.array.num_rows())
                for j in range(self.array.num_cols())]
        return bytes(header) + LZW.encode(bytes(data))

    @staticmethod
    def lzw_decompression(data: bytes):
        height, width = int.from_bytes(data[:4], "big"),\
                        int.from_bytes(data[4:8], "big")
        image = GrayscaleImage(height, width)
        pixels = LZW.decode(data[8:])
        for row in range(height):
            for col in range(width):
                image.setitem(row, col, pixels[row * width + col])

        return image

    def lzw_compression_ratio(self) -> float:
        return (self.width() * self.height()) / (len(self.lzw_compression()) - 8)


image2 = GrayscaleImage.from_file("image.jpg")
image2.save('test2.png')
print(image2.lzw_compression_ratio())
image3 = GrayscaleImage.lzw_decompression(image2.lzw_compression())
image3.save('test.png')
