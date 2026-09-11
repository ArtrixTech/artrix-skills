#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["bleak>=1.1,<4", "pycryptodome>=3.20,<4", "pillow>=10,<13"]
# ///
"""MJBQDYJ1-WC: scan, status, render, or explicitly print one text label."""
import argparse
import asyncio
import json
import struct
import time
import uuid
import zlib
from datetime import datetime, timezone
from pathlib import Path

from Crypto.Cipher import AES
from bleak import BleakClient, BleakScanner

SERVICE = '0000fe95-0000-1000-8000-00805f9b34fb'
TX = '0000001f-0000-1000-8000-00805f9b34fb'
RX = '00000020-0000-1000-8000-00805f9b34fb'
KEY = bytes.fromhex('99b829436cdd5647aadb8816f73e8644')
IV = bytes.fromhex('0001020f3cf899ababcd25318df446b1')
MAX_DOTS = 600


def encode(payload):
    body = AES.new(KEY, AES.MODE_CBC, IV).encrypt(payload + bytes(-len(payload) % 16))
    return b'\xa3\x20' + struct.pack('<H', len(body)) + body + struct.pack('<I', zlib.crc32(body, 0x76953521))


def decode(frame):
    if len(frame) < 8 or frame[:2] not in (b'\xa3\x00', b'\xa3\x20'):
        raise ValueError('Invalid envelope')
    n = int.from_bytes(frame[2:4], 'little')
    if len(frame) != n + 8:
        raise ValueError('Invalid frame length')
    body = frame[4:4+n]
    if zlib.crc32(body, 0x76953521) != int.from_bytes(frame[-4:], 'little'):
        raise ValueError('CRC mismatch')
    if frame[1] == 32 and (not n or n % 16):
        raise ValueError('Invalid AES block length')
    plain = AES.new(KEY, AES.MODE_CBC, IV).decrypt(body) if frame[1] == 32 else body
    if len(plain) < 5:
        raise ValueError('Missing payload header')
    length = int.from_bytes(plain[3:5], 'little')
    if len(plain) < length + 5:
        raise ValueError('Truncated payload')
    return plain[:length+5]


def tlvs(body):
    result = {}
    while body:
        if len(body) < 3:
            raise ValueError('Truncated TLV header')
        tag, n = body[0], int.from_bytes(body[1:3], 'little')
        if len(body) < 3+n or tag in result:
            raise ValueError('Truncated or duplicate TLV')
        result[tag] = body[3:3+n]
        body = body[3+n:]
    return result


def u32_field(fields, tag):
    value = fields.get(tag)
    if value is None or len(value) != 4:
        raise ValueError(f'Missing uint32 TLV {tag}')
    return int.from_bytes(value, 'little')


def require_ready(flags, buffer_free, size):
    if flags != 0:
        raise RuntimeError(f'Printer not ready: flags={flags!r}; no print sent')
    if buffer_free is None or buffer_free < size + 1024:
        raise RuntimeError('Insufficient confirmed buffer capacity; no print sent')


def raster_text(text, output, font_path=None):
    from PIL import Image, ImageDraw, ImageFont
    if not text.strip() or any(c in text for c in '\n\r\t') or len(text) > 200:
        raise ValueError('Use one non-empty line of at most 200 characters')
    fonts = [Path(font_path)] if font_path else [
        Path('/System/Library/Fonts/Hiragino Sans GB.ttc'),
        Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'),
        Path('C:/Windows/Fonts/msyh.ttc'),
    ]
    found = next((p for p in fonts if p.is_file()), None)
    if found is None:
        raise ValueError('No CJK font found; supply --font /path/to/font.ttf')
    font = ImageFont.truetype(str(found), 48)
    x0, y0, x1, y1 = font.getbbox(text)
    width = max(240, x1-x0+32)
    if width > MAX_DOTS or y1-y0 > 80:
        raise ValueError('Text exceeds short-label bounds; shorten it')
    preview = Image.new('1', (width, 96), 1)
    ImageDraw.Draw(preview).text(((width-x1+x0)//2-x0, (96-y1+y0)//2-y0), text, font=font, fill=0)
    preview.save(output/'preview.png')
    vertical = preview.transpose(Image.Transpose.ROTATE_90)
    vertical.save(output/'raster.png')
    return bytes(v ^ 255 for v in vertical.tobytes()), width


def print_payloads(raster, height):
    if not 1 <= height <= MAX_DOTS or len(raster) != height * 12:
        raise ValueError('Invalid 96-dot raster dimensions')
    yield bytes.fromhex('11050b0700') + struct.pack('<HH', 96, height) + b'\x01\x00\x00'
    total = (len(raster)+1799)//1800
    for i in range(total):
        block = raster[i*1800:(i+1)*1800]
        yield bytes.fromhex('11050d') + struct.pack('<HHH', len(block)+11, i+1, total) + bytes.fromhex('100c0000000000') + block
    yield bytes.fromhex('11050c0900010200000002010000')


async def device_action(args, log, event, raster, height):
    rxbuf = bytearray()
    fresh_status, heartbeat, ack = asyncio.Event(), asyncio.Event(), asyncio.Event()
    state = {'flags': None, 'buffer_free': None}

    def receive(_, chunk):
        rxbuf.extend(chunk)
        while len(rxbuf) >= 4:
            size = int.from_bytes(rxbuf[2:4], 'little')+8
            if rxbuf[:2] not in (b'\xa3\x00', b'\xa3\x20') or size > 8192:
                event('rx_error', error='Invalid frame header'); rxbuf.clear(); return
            if len(rxbuf) < size:
                return
            wire = bytes(rxbuf[:size]); del rxbuf[:size]
            try:
                plain = decode(wire)
                event('rx', wire=wire.hex(), plain=plain.hex())
                if plain[:3] == bytes.fromhex('210113'):
                    state['flags'] = u32_field(tlvs(plain[5:]), 1)
                    fresh_status.set()
                elif plain[:3] == bytes.fromhex('10011f'):
                    fields = tlvs(plain[5:])
                    state['buffer_free'] = u32_field(fields, 1)
                    state['flags'] = u32_field(fields, 2)
                    state['unknown_tag3_hex'] = fields.get(3, b'').hex()
                    heartbeat.set()
                elif plain == bytes.fromhex('21050c0000'):
                    ack.set()
            except Exception as e:
                event('rx_error', error=str(e), wire=wire.hex())

    client = BleakClient(args.address, timeout=20)
    try:
        async with client:
            event('connected')
            service = client.services.get_service(SERVICE)
            if service is None:
                raise RuntimeError('Expected printer service absent')
            char = next((c for c in service.characteristics if c.uuid == TX), None)
            notify = next((c for c in service.characteristics if c.uuid == RX), None)
            if not char or 'write-without-response' not in char.properties or not notify or 'notify' not in notify.properties:
                raise RuntimeError('Expected printer GATT characteristics absent')
            await client.start_notify(notify, receive)

            async def send(payload):
                wire = encode(payload)
                event('tx', plain=payload.hex(), wire=wire.hex())
                chunk_size = min(204, char.max_write_without_response_size)
                if chunk_size <= 0:
                    raise RuntimeError('Invalid BLE write size')
                for offset in range(0, len(wire), chunk_size):
                    await client.write_gatt_char(char, wire[offset:offset+chunk_size], response=False)
                    await asyncio.sleep(0.04)

            async def query():
                fresh_status.clear()
                await send(bytes.fromhex('1101130000'))
                await asyncio.wait_for(fresh_status.wait(), 5)

            await send(bytes.fromhex('11011e010001'))
            await asyncio.sleep(0.3)
            await query()
            log['initial_state'] = dict(state)
            if args.command == 'print':
                await asyncio.wait_for(heartbeat.wait(), 5)
                await query()
                require_ready(state['flags'], state['buffer_free'], len(raster))
                log['ready_state'] = dict(state)
                log['submission_started'] = True
                event('print_begin', width=96, height=height, raster_bytes=len(raster))
                for payload in print_payloads(raster, height):
                    await send(payload)
                    await asyncio.sleep(0.15)
                await asyncio.wait_for(ack.wait(), 30)
                log['finalize_ack_received'] = True
                # Fresh status after ACK is evidence of device state, not paper quality.
                await asyncio.sleep(1)
                deadline = time.monotonic()+15
                while True:
                    await query()
                    if state['flags'] == 0:
                        log['idle_after_ack'] = True
                        break
                    if state['flags'] != 0x80:
                        raise RuntimeError(f'Device reports flags {state["flags"]:#x} after submission; do not auto-reprint')
                    if time.monotonic() >= deadline:
                        raise TimeoutError('Device still printing; do not auto-reprint')
                    await asyncio.sleep(0.5)
                log['physical_output'] = 'requires_user_observation'
            log['final_state'] = dict(state)
            await client.stop_notify(notify)
    finally:
        log['disconnected'] = not client.is_connected


async def run(args):
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    output = args.output.expanduser().resolve()/f'{stamp}-{args.command}-{uuid.uuid4().hex[:8]}'
    output.mkdir(parents=True, exist_ok=False)
    log = dict(time=datetime.now(timezone.utc).isoformat(), command=args.command, events=[])
    if hasattr(args, 'address'):
        log['address'] = args.address
    if hasattr(args, 'text'):
        log['text'] = args.text

    def event(kind, **fields):
        log['events'].append(dict(t=round(time.monotonic(), 3), kind=kind, **fields))

    try:
        if args.command == 'scan':
            devices = await BleakScanner.discover(timeout=args.seconds, return_adv=True)
            log['candidates'] = [dict(address=d.address, name=a.local_name or d.name, rssi=a.rssi,
                                      service_uuids=a.service_uuids,
                                      service_data={k:v.hex() for k,v in a.service_data.items()})
                                 for d,a in devices.values() if 'printer' in (a.local_name or d.name or '').lower()]
        elif args.command == 'render':
            raster, height = raster_text(args.text, output, args.font)
            log.update(width=96, height=height, raster_bytes=len(raster))
        else:
            raster, height = raster_text(args.text, output, args.font) if args.command == 'print' else (None, None)
            await device_action(args, log, event, raster, height)
    except Exception as e:
        log['error'] = repr(e)
        if log.get('submission_started'):
            log['retry_guidance'] = 'Check the paper and device; do not automatically replay this job'
    finally:
        (output/'result.json').write_text(json.dumps(log, ensure_ascii=False, indent=2))
        print(json.dumps({k:v for k,v in log.items() if k != 'events'}, ensure_ascii=False, indent=2))
        print(f'Evidence: {output}')
    return int('error' in log)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ('scan', 'status', 'render', 'print'):
        sub = commands.add_parser(name)
        sub.add_argument('--output', type=Path, required=True, help='Parent directory; each run creates a unique child')
        if name == 'scan':
            sub.add_argument('--seconds', type=float, default=10)
        if name in ('status', 'print'):
            sub.add_argument('--address', required=True, help='Selected device ID from scan; macOS uses a UUID')
        if name in ('render', 'print'):
            sub.add_argument('--text', required=True)
            sub.add_argument('--font', help='CJK-capable TrueType/OpenType font')
    args = parser.parse_args()
    if args.command == 'scan' and not 1 <= args.seconds <= 60:
        parser.error('--seconds must be between 1 and 60')
    raise SystemExit(asyncio.run(run(args)))


if __name__ == '__main__':
    main()
