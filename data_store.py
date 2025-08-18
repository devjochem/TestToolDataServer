from tests.systeminfo import Specs


def createtestdata():
    data = {
        "Serial": Specs().getSerial(),
        "specs": Specs().getSpecs(),
        "disks": Specs().getDisks(),
        "tests": {
            "LCD": "NA",
            "TP": "NA",
            "KB": "NA",
            "CAM": "NA",
            "AUDIO": {
                "LEFTSP": "NA",
                "RIGHTSP": "NA",
                "MIC": "NA"
            },
        },
        "VISUAL": {
            "BACK": "NA",
            "BEZEL": "NA",
            "PALM": "NA",
            "SIDES": "NA",
            "BOTTOM": "NA"
        }
    }

    return data

if __name__ == "__main__":
    testdata = createtestdata()

    print(testdata)