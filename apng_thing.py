import binascii
import mmap
import struct

fcTL_struct_format = '>ccccIIIIIHHBB'
fcTL_struct_format_crc = fcTL_struct_format + 'I'


def main():
    apng_file = 'test 720p 15fps zopfli.png'
    new_delay = 15

    with open(apng_file, 'rb+') as f:
        with mmap.mmap(f.fileno(), 0) as m:
            m.seek(m.find(b'acTL') + 4)
            header = struct.unpack('>II', m.read(8))
            number_of_frames = header[0]  # Note that this includes the first frame even if skipped
            last_position = 0

            for i in range(number_of_frames - 1):
                curr_position = m.find(b'fcTL', last_position)  # Find fcTL chunk
                m.seek(curr_position)  # Go to chunk beginning
                frame_info = list(struct.unpack(fcTL_struct_format, m.read(30)))  # Read in chunk data as a list
                frame_info[10] = new_delay  # Set new delay denominator

                # Generate CRC checksum from binary data
                crc = binascii.crc32(struct.pack(fcTL_struct_format, *frame_info))
                frame_info.append(crc)

                m.seek(curr_position)  # Move back to chunk beginning
                frame_binary = struct.pack(fcTL_struct_format_crc, *frame_info)  # Pack with CRC checksum
                m.write(frame_binary)  # Write changes

                last_position = curr_position + 34  # Prevent the same chunk from being found

            m.flush()


if __name__ == '__main__':
    main()
