import struct

class AX25UIFrameDecoder:
    def decode_ax25_frame(self, frame):
        """Decode an AX.25 frame and extract the source, destination, SSID, and info fields."""
        if frame[0] != 0x7E or frame[-1] != 0x7E:
            raise ValueError("Invalid AX.25 frame")

        destination_callsign = ''.join([chr((frame[i] >> 1) & 0x7F) for i in range(1, 7)]).strip()
        destination_ssid = (frame[7] >> 1) & 0x0F

        source_callsign = ''.join([chr((frame[i] >> 1) & 0x7F) for i in range(8, 14)]).strip()
        source_ssid = (frame[14] >> 1) & 0x0F

        control_field = frame[15]
        pid_field = frame[16]
        info_field = frame[17:-3].decode('ascii')
        received_fcs = frame[-3:-1]
        calculated_fcs = self.compute_fcs(frame[1:-3])

        if received_fcs != calculated_fcs:
            raise ValueError("FCS check failed")

        return {
            'destination_callsign': destination_callsign,
            'destination_ssid': destination_ssid,
            'source_callsign': source_callsign,
            'source_ssid': source_ssid,
            'control_field': control_field,
            'pid_field': pid_field,
            'info_field': info_field
        }

    def compute_fcs(self, frame):
        """Compute the Frame Check Sequence (FCS) for a given frame using the CRC-CCITT algorithm."""
        fcs = 0xFFFF
        for byte in frame:
            fcs ^= byte
            for _ in range(8):
                if fcs & 0x01:
                    fcs = (fcs >> 1) ^ 0x8408
                else:
                    fcs >>= 1
        fcs = ~fcs & 0xFFFF
        return struct.pack('<H', fcs)
