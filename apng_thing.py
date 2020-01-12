import binascii
import mmap
import struct
import sys

fcTL_struct_format = '>ccccIIIIIHHBB'
fcTL_struct_format_crc = fcTL_struct_format + 'I'


def main():
    args = sys.argv
    apng_file = args[1]  # Input file
    new_delay = args[2]  # FPS

    with open(apng_file, 'rb+') as f:  # Open the APNG file
        with mmap.mmap(f.fileno(), 0) as m:  # Make changes to the file in memory
            m.seek(m.find(b'acTL') + 4)  # Find the Animation Control chunk
            header = struct.unpack('>II', m.read(8))  # Read in information
            number_of_frames = header[0]  # Note that this includes the first frame even if skipped
            last_position = 0  # Start at the beginning of the APNG file

            for i in range(number_of_frames - 1):  # The delay of each frame must be changed individually
                curr_position = m.find(b'fcTL', last_position)  # Find fcTL chunk (This denotes the start of a frame)
                m.seek(curr_position)  # Go to chunk beginning
                frame_info = list(struct.unpack(fcTL_struct_format, m.read(30)))  # Read in chunk data as a list
                frame_info[10] = new_delay  # Set new delay denominator

                # Generate CRC checksum from binary data
                crc = binascii.crc32(struct.pack(fcTL_struct_format, *frame_info))
                frame_info.append(crc)

                m.seek(curr_position)  # Move back to chunk beginning
                frame_binary = struct.pack(fcTL_struct_format_crc, *frame_info)  # Pack with CRC checksum
                m.write(frame_binary)  # Write changes to memory

                last_position = curr_position + 34  # Prevent the same chunk from being found

            m.flush()  # Save changes to disk


if __name__ == '__main__':
    main()
