#!/usr/bin/env python3

import sys, socket, select, json

my_id = str(sys.argv[1])

replica_ids = sys.argv[2:]

sock = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
sock.connect(my_id)

while True:
    ready = select.select([sock], [], [], 0.1)[0]

    if sock in ready:
        msg_raw = sock.recv(32768)

        if len(msg_raw) == 0:
            continue

        msg = json.loads(msg_raw)

        # For now, fail get() and put() from clients
        if msg['type'] in ['get', 'put']:
            rsp = {'src':my_id,
                   'dst':msg['src'],
                   'leader':None,
                   'type':'fail',
                   'MID':msg['MID']}
            
            sock.sendall(json.loads(rsp))
