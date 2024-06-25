"""
    There are the functions that make requests to the Valdi API
"""

import requests, asyncio, os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from models import Khachkar
from mesh_handling import get_mesh_from_video

def login(email: str, password: str) -> tuple:
    payload = {
        "email": email,
        "password": password
    }
    response = requests.post("https://api.valdi.ai/account/login", json=payload)
    if response.status_code == 200:
        return response.json()["access_token"], response.json()["refresh_token"]
    return None, None

def enter_with_refresh_token(refresh_token: str) -> str | None:
    payload = {
        "token": refresh_token
    }
    response = requests.post("https://api.valdi.ai/account/refresh_token", json=payload)
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def list_vms(token: str) -> dict:
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get("https://api.valdi.ai/v1/devices/available", headers=headers)
    return response.json()

def get_vms_status(token: str) -> dict:
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get("https://api.valdi.ai/v1/vm", headers=headers)
    return response.json()


def __start_or_stop_vm(token: str, server_id: str, action: str) -> bool:
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.post(f"https://api.valdi.ai/v1/vm/{action}/{server_id}", headers=headers)
    if response.status_code == 200 and "message" in response.json() and response.json()["message"] == "success":
        return True
    return False

def stop_vm(token: str, server_id: str) -> bool:
    return __start_or_stop_vm(token, server_id, "stop")

def start_vm(token: str, server_id: str) -> bool:
    return __start_or_stop_vm(token, server_id, "start")


class ValdiTask():
    def __init__(self, delay_minutes: int = 15):
        load_dotenv()
        self.delay_seconds = delay_minutes * 60
        self.email = os.getenv("VALDI_EMAIL")
        self.password = os.getenv("VALDI_PASSWORD")
        self.vm_id = os.getenv("VALDI_VM_ID")
        self.refresh_token = None
    
    def get_access_token(self) -> str | None:
        if self.refresh_token is not None:
            return enter_with_refresh_token(self.refresh_token)
        token, self.refresh_token = login(self.email, self.password)
        return token
    
    def mesh_every_khachkar(self, db: Session):
        queued_khachkars = db.query(Khachkar).filter(Khachkar.state == "queued_for_meshing").all()
        for khachkar in queued_khachkars:
            if khachkar is None:
                print(f" - Khachkar with id {khachkar.id} not found")
                continue
            print(f" -> Meshing khachkar with id {khachkar.id}")
            res = get_mesh_from_video(khachkar, db)
            print(res)

    def no_khachkars_queued(self, db: Session) -> bool:
        return db.query(Khachkar).filter(Khachkar.state == "queued_for_meshing").count() == 0

    def no_khachkars_meshing(self, db: Session) -> bool:
        return db.query(Khachkar).filter(Khachkar.state == "creating_mesh").count() == 0

    def get_is_vm_status_data(self, token: str) -> bool | None:
        vms_status = get_vms_status(token)
        if "virtual_machines" not in vms_status:
            print("Error getting the status of the virtual machines")
            return None
        elif len(vms_status["virtual_machines"]) == 0:
            print("No virtual machines available")
            return None
        for vm_status in vms_status["virtual_machines"]:
            if vm_status["server"] == self.vm_id:
                return vm_status
        print("Virtual machine not found")
        return None

    async def try_to_call_gsplatting_server(self, db: Session):
        """
            Tries to call the Gaussian Splatting server for the queued khachkars.
            The task has a wait time of 'self.delay_seconds' when there is nothing to do.
            If the server is stopped, it starts it (if is available).
        """
        while True:
            token = self.get_access_token()
            vm_data = self.get_is_vm_status_data(token)
            if vm_data is None:
                await asyncio.sleep(self.delay_seconds)
                continue

            # If there are no queued khachkars, we don't need to do anything
            if self.no_khachkars_queued(db):
                if vm_data["status"] == "running" and self.no_khachkars_meshing(db):
                    #print("Server is running and there are no khachkars to mesh... Stopping the server")
                    #if stop_vm(token, vm_data["server"]):
                    #    print(" -> Server stopped")
                    #else:
                    #    print(" -> Error stopping the server")
                    pass
                await asyncio.sleep(self.delay_seconds)
                continue

            # If there are queued khachkars, we need to mesh them
            match vm_data["status"]:
                case "running":
                    print("Server is running, and there are khachkars to mesh... Meshing them")
                    self.mesh_every_khachkar(db)
                case "stopped":
                    print("Server is stopped, and there are khachkars to mesh... Starting the server")
                    if start_vm(token, vm_data["server"]):
                        # We need to wait for the server to start
                        print(" -> Server started, waiting for the meshing API to start")
                        await asyncio.sleep(45)
                        print(" -> Starting the meshing process...")
                        self.mesh_every_khachkar(db)
                    else:
                        print(" -> Error starting the server")
                        await asyncio.sleep(self.delay_seconds)
                case _:
                    print("Server is in another status:", vm_data["status"])
                    await asyncio.sleep(self.delay_seconds)
           