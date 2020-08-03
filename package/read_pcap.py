import numpy as np
import pandas as pd
import struct
from pathlib import Path
from progressbar import ProgressBar
__all__ = ['PcapReader']

"""
class: PcapParser
! in PcapParser.seq_processing() front hemisphere is selected only
Responsibility: transform pcap binary file to human-readable format.
For additional information look up VLP-16 Lidar user documentation.
"""
class PcapReader:
    def __init__(self, file_path):
        self.path = Path(file_path)
        self.LASER_ANGLES = [-15, 1, -13, -3, -11, 5, -9, 7, -7, 9, -5, 11, -3, 13, -1, 15]
        self.NUM_LASERS = 16
        self.DISTANCE_RESOLUTION = 0.002
        self.ROTATION_MAX_UNITS = 36000

        self.pcap_XYZ_data = []

        self.azimuth_bin = 100
        self.first_timestamp = None
        self.factory = None

        pcap_data = open(self.path, 'rb').read()
        self.pcap_data = pcap_data[24:]

    # Transforms single pcap file to human readable format
    # Returns list with columns [x, y, z, R, azimuth, laser_id, timestamp, file_number]
    def get_pcap_data(self):
        """
        Args:
            file_number: number of pcap file to be processed

        Function description:
            goes throw the all binary symbol inside pcap file
            call seq_processing for each sequence in packets structure:

            pcap file structure:
                0 - 24   <->  global header <-> not read
                24 - end <-> packets with 1264-binary symbol info

            packets structure:
                0 - 16      <->  local header <-> not read
                16 - 58     <->  42 binary symbol of meta info <-> not read
                58  - 1258  <->  12 sequences with 100 binary symbol each with dist and azimuth
                1258 - 1264 <->  4 binary symbol for timestamp and 2 factory bites

        """
        with ProgressBar(max_value=int(len(self.pcap_data))) as bar:
            for offset in range(0, int(len(self.pcap_data)), 1264):
                bar.update(offset)

                if (len(self.pcap_data) - offset) < 1264:
                    break

                cur_packet = self.pcap_data[offset + 16: offset + 16 + 42 + 1200 + 4 + 2]
                cur_data = cur_packet[42:]

                self.first_timestamp, self.factory = struct.unpack_from("<IH", cur_data, offset=1200)
                assert hex(self.factory) == '0x2237', 'Error mode: 0x22=VLP-16, 0x37=Strongest Return'

                packet_1264 = []
                seq_index = 0
                for seq_offset in range(0, 1100, 100):
                    packet_1264 += self.seq_processing(cur_data, seq_offset, seq_index, self.first_timestamp)

                self.pcap_XYZ_data += packet_1264

        self.pcap_XYZ_data = pd.DataFrame(self.pcap_XYZ_data)
        return self.pcap_XYZ_data

    # Parses sequences inside each 1264 byte packet
    # ! Front hemisphere is selected only
    def seq_processing(self, data, seq_offset, seq_index, first_timestamp):
        """

        Args:
            data: current sequence
            seq_offset: number of the sequence in packet (0 - 1200 )
            seq_index: number of current sub-sequence in sequence (0- 22)
            first_timestamp: 4 binary symbol of timestamp
            file_number: number of pcap file to be processed

        Function description:
        unpack sequence data into seq_row_list for each laser_id block
        with {'X', 'Y', 'Z', 'D', 'azimuth', 'laser_id','first_timestamp', 'pcap_num'} info

        seq_row_list pushed into self.seq_list


            each sequence contain 2*11 sub-sequence
                sub-sequence structure:
                    flag
                    first_azimuth
                    16 laser_id block of binary symbol

        """
        flag, first_azimuth = struct.unpack_from("<HH", data, seq_offset)
        step_azimuth = 0

        assert hex(flag) == '0xeeff', 'Flag error'

        seq_row_list = []
        for step in range(2):
            if step == 0 and seq_index % 2 == 0 and seq_index < 22:
                flag, third_azimuth = struct.unpack_from("<HH", data, seq_offset + 4 + 3 * 16 * 2)

                assert hex(flag) == '0xeeff', 'Flag error'

                if third_azimuth < first_azimuth:
                    step_azimuth = third_azimuth + self.ROTATION_MAX_UNITS - first_azimuth
                else:
                    step_azimuth = third_azimuth - first_azimuth
            arr = struct.unpack_from('<' + "HB" * self.NUM_LASERS, data, seq_offset + 4 + step * 3 * 16)

            for i in range(self.NUM_LASERS):
                azimuth = first_azimuth + (step_azimuth * (55.296 / 1e6 * step + i * 2.304 / 1e6)) / (2 * 55.296 / 1e6)
                if azimuth > self.ROTATION_MAX_UNITS:
                    azimuth -= self.ROTATION_MAX_UNITS
                x, y, z = self.calc_real_val(arr[i * 2], azimuth, i)
                # azimuth_time = (55.296 / 1e6 * step + i * (2.304 / 1e6)) + first_timestamp
                """restriction below due to the real distance to the surface(m)"""
                if (-2 <= x <= 2) and (0 <= y <= 2) and (-2 <= z <= 2):
                #if y > 0:
                    d = arr[i * 2 + 1]
                    azimuth_v = round(azimuth * 1.0 / self.azimuth_bin)
                    row = [{'X': x, 'Y': y, 'Z': z, 'D': d, 'azimuth': azimuth_v,
                        'laser_id': i, 'first_timestamp': first_timestamp}]
                    #row = [{'X': x, 'Y': y, 'Z': z, 'D': d, 'azimuth': azimuth_v, 'laser_id': i,'first_timestamp': first_timestamp}]
                    seq_row_list += row
                    #seq_row_list.append({'X': x, 'Y': y, 'Z': z, 'D': d, 'azimuth': azimuth_v, 'laser_id': i,
                                         #'first_timestamp': first_timestamp})
            seq_index += 1
        return seq_row_list

    # Calculates x, y, z
    def calc_real_val(self, dis, azimuth, laser_id):
        r = dis * self.DISTANCE_RESOLUTION
        omega = self.LASER_ANGLES[laser_id] * np.pi / 180.0
        alpha = (azimuth / 100.0) * (np.pi / 180.0)
        x = r * np.cos(omega) * np.sin(alpha)
        y = r * np.cos(omega) * np.cos(alpha)
        z = r * np.sin(omega)
        return x, y, z
