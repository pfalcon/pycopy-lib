# (c) 2018 Paul Sokolovsky. Either zlib or MIT license at your choice.
import ffi
import ustruct


_lib = ffi.open("libSDL2_image-2.0.so.0")

IMG_Load = _lib.func("P", "IMG_Load", "s")
IMG_Load_RW = _lib.func("P", "IMG_Load_RW", "Pi")
