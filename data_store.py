from datetime import datetime
from zoneinfo import ZoneInfo


def createtestdata():
    data = {
            "Naam": "Jochem",
            "Specs": {
                "Vendor": "ASUSTeK COMPUTER INC.",
                "Model": "ROG STRIX B450-F GAMING",
                "Serial": "200366448903337",
                "CPU": "AMD Ryzen 7 3700X 8-Core Processor",
                "RAM": "31.26 GB",
                "GPU(s)": [
                    "Advanced Micro Devices, Inc. [AMD/ATI] Navi 10 [Radeon RX 5600 OEM/5600 XT / 5700/5700 XT] (rev c1)"
                ]
            },
            "TestResults": {
                "LCD": "1",
                "Touchpad": "Werkt",
                "Keyboard": "Werkt",
                "Audio": {
                    "Linker Speaker": True,
                    "Rechter Speaker": True,
                    "Microfoon": True
                    },
                "Webcam": "Werkt"
                }
            }

    return data

def createbat_data():
    data = {
        "Test ID": "",
        "Serial": "200366448903337"
    }

if __name__ == "__main__":
    testdata = createtestdata()
    print(datetime.now(ZoneInfo("Europe/Amsterdam")).timestamp())
    print(testdata)