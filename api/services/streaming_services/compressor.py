import blosc
import msgpack

# Compression using Blosc with Zstd
def compress_data(data: dict) -> bytes:
    packed_data = msgpack.packb(data, use_bin_type=True)  # Pack data into a binary format
    compressed_data = blosc.compress(packed_data, cname='zstd', clevel=5, shuffle=blosc.SHUFFLE)
    return compressed_data

# Decompression using Blosc with Zstd
def decompress_data(data: bytes) -> dict:
    decompressed_data = blosc.decompress(data)
    unpacked_data = msgpack.unpackb(decompressed_data, raw=False)
    return unpacked_data
