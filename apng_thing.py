import binascii
import struct

apng_file = 'test 720p 15fps zopfli.png'
new_delay = 25

with open(apng_file, 'rb+') as f:
    data = f.read()
    f.seek(data.find(b'acTL') + 4)
    header = struct.unpack('>II', f.read(8))
    number_of_frames = header[0]  # Note that this includes the first frame even if skipped
    last_position = 0
    for i in range(number_of_frames - 1):
        curr_position = data.find(b'fcTL', last_position)  # Find fcTL chunk
        f.seek(curr_position)  # Go to chunk beginning
        frame_info = list(struct.unpack('>ccccIIIIIHHBB', f.read(30)))  # Read in chunk data as a list
        frame_info[10] = new_delay  # Set new delay denominator

        # Generate CRC checksum from binary data
        crc = binascii.crc32(struct.pack('>ccccIIIIIHHBB', *frame_info))
        frame_info.append(crc)

        f.seek(curr_position)  # Move back to chunk beginning
        frame_binary = struct.pack('>ccccIIIIIHHBBI', *frame_info)  # Pack with CRC checksum
        f.write(frame_binary)  # Write changes

        last_position = curr_position + 34  # Prevent the same chunk from being found
