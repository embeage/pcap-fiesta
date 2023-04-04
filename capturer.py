import argparse
from subprocess import Popen
import os
import socket

def run_tshark(video_id, capture_time, interface, capture_filter):
    tshark_command = [
        'tshark', 
        '-w', f"pcaps/{video_id}.pcapng",
        '-a', f"duration:{capture_time}", 
        '-i', interface,
        '-f', capture_filter,
        '-q',
        '-n',
    ]

    tshark_process = Popen(tshark_command)
    tshark_process.wait()

def run(host, port, interface, capture_filter):
    if not os.path.exists('pcaps'):
        os.makedirs('pcaps')

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()

        conn, _ = s.accept()
        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                    break

                msg = data.decode()
                if msg == 'terminate':
                    break

                video_id, play_time = msg.split(",")
                conn.sendall(b'start')

                # Run capture a bit longer to make sure to capture everything
                capture_time = int(play_time) + 5

                run_tshark(video_id, capture_time, interface, capture_filter)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Start capturing session and wait for watcher.")
    parser.add_argument('-H', '--host',
                        help="Address to bind to",
                        required=True)
    parser.add_argument('-p', '--port', required=True)
    parser.add_argument('-i', '--interface', required=True)
    parser.add_argument('-f', '--capture-filter', default='')
    args = parser.parse_args()
    run(args.host, int(args.port), args.interface, args.capture_filter)
