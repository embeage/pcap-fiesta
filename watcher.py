import argparse
import csv
import os
import socket

from video_player import svt_play_video

def run(host, port, play_time, filename):
    if not os.path.exists('requests'):
        os.makedirs('requests')

    with open(filename, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)

        # Skip header row
        next(csv_reader)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))

            for video_id, url, start_time in csv_reader:
                # Check if this video already done
                if os.path.exists(f"requests/{video_id}.json"):
                    continue

                msg = f"{video_id},{play_time}"
                s.sendall(msg.encode())

                data = s.recv(1024)
                if data.decode() == 'start':
                    url = url + f"?position={start_time}"
                    svt_play_video(video_id, url, play_time, save_requests=True)

            s.sendall(b'terminate')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Start watching session and communicate with capturer.")
    parser.add_argument('-H', '--host',
                        help="Host running capturer",
                        required=True)
    parser.add_argument('-p', '--port', required=True)
    parser.add_argument('--play-time', default=180,
                        help="Should be lower than 4 minutes")
    parser.add_argument('-r', '--read-file',
                        help="Comma-separated file to read with fields video_id, url, start_time.",
                        required=True)
    args = parser.parse_args()
    run(args.host, int(args.port), int(args.play_time), args.read_file)
