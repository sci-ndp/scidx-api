import msgpack
import zstandard as zstd

def compress_data(data: dict) -> bytes:
    compressor = zstd.ZstdCompressor()
    return compressor.compress(msgpack.packb(data, use_bin_type=True))

def decompress_data(data: bytes) -> dict:
    decompressor = zstd.ZstdDecompressor()
    decompressed = decompressor.decompress(data)
    return msgpack.unpackb(decompressed, raw=False)
