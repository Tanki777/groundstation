from dataclasses import dataclass

@dataclass
class Telecommand():
    word: str
    id: hex
    description: str

class DataModel():
    def __init__(self):
        self.telecommands = [
            #---GENERAL---#
            Telecommand("REBOOTXXXX", 0x0000, "reboot the satellite"),
            Telecommand("MODE_SAFEX", 0x0001, "enter safe mode"),
            Telecommand("MODE_IDLEX", 0x0002, "enter idle mode"),
            Telecommand("MODE_SUNPT", 0x0003, "enter sun-pointing mode"),
            Telecommand("MODE_MISSN", 0x0004, "enter mission mode"),

            #---Attitude Control---#
            Telecommand("AC_APP_ONX", 0x1000, "turn on application attitude control"),
            Telecommand("AC_APP_OFF", 0x1001, "turn off application attitude control"),
            Telecommand("AC_TM_PRDX", 0x1002, "set period of the telemetry thread [ms]"),
            Telecommand("AC_YAWXXXX", 0x1003, "set desired yaw angle [deg]"),
            Telecommand("AC_YAWSPDX", 0x1004, "set desired yaw angular speed [deg/s]"),
            Telecommand("AC_CTRLPRD", 0x1005, "set period of the attitude controller [ms]"),

            #---Attitude Determination---#
            Telecommand("AD_APP_ONX", 0x2000, "turn on application attitude determination"),
            Telecommand("AD_APP_OFF", 0x2001, "turn off application attitude determination"),
            Telecommand("AD_TM_PRDX", 0x2002, "set period of the telemetry thread [ms]"),

            #---IMU---#
            Telecommand("IMU_APP_ON", 0x3000, "turn on application IMU"),
            Telecommand("IMU_APP_OF", 0x3001, "turn off application IMU"),
            Telecommand("IMU_TM_PRD", 0x3002, "set period of the telemetry thread [ms]"),
            Telecommand("IMU_CAL_AX", 0x3003, "calibrate accelerometer"),
            Telecommand("IMU_CAL_GX", 0x3004, "calibrate gyroscope"),
            Telecommand("IMU_CAL_MX", 0x3005, "calibrate magnetometer"),
            Telecommand("IMU_SNSPRD", 0x3006, "set period of the sensor [ms]"),

            #---Light Sensor---#
            Telecommand("LS_APP_ONX", 0x4000, "turn on application light sensor"),
            Telecommand("LS_APP_OFF", 0x4001, "turn off application light sensor"),
            Telecommand("LS_TM_PRDX", 0x4002, "set period of the telemetry thread [ms]"),
            Telecommand("LS_SNSPRDX", 0x4003, "set period of the sensor [ms]"),

            #---Magnetic Torquer---#
            Telecommand("MT_APP_ONX", 0x5000, "turn on application magnetic torquer"),
            Telecommand("MT_APP_OFF", 0x5001, "turn off application magnetic torquer"),
            Telecommand("MT_TM_PRDX", 0x5002, "set period of the telemetry thread [ms]"),
            Telecommand("MT_CURRENT", 0x5003, "set applied current [A]"),
            Telecommand("MT_SET_MTX", 0x5004, "set torquer to be used [1 or 2]"),

            #---Payload---#
            Telecommand("PL_APP_ONX", 0x6000, "turn on application payload"),
            Telecommand("PL_APP_OFF", 0x6001, "turn off application payload"),
            Telecommand("PL_TM_PRDX", 0x6002, "set period of the telemetry thread [ms]"),
            Telecommand("PL_SCANXXX", 0x6003, "scan the environment"),
            Telecommand("PL_TRACKXX", 0x6004, "track an object [?]"),
            Telecommand("PL_CAMERAX", 0x6005, "take a photo"),

            #---Power---#
            Telecommand("PW_APP_ONX", 0x7000, "turn on application power"),
            Telecommand("PW_APP_OFF", 0x7001, "turn off application power"),
            Telecommand("PW_TM_PRDX", 0x7002, "set period of the telemetry thread [ms]"),
            Telecommand("PW_SP_DEPL", 0x7003, "deploy solar panels"),
            Telecommand("PW_SP_RETR", 0x7004, "retract solar panels"),
            Telecommand("PW_SNSPRDX", 0x7005, "set period of the thread for estimating battery status and reading solar panels"),

            #---Reaction Wheel---#
            Telecommand("RW_APP_ONX", 0x8000, "turn on application reaction wheel"),
            Telecommand("RW_APP_OFF", 0x8001, "turn off application reaction wheel"),
            Telecommand("RW_TM_PRDX", 0x8002, "set period of the telemetry thread [ms]"),
            Telecommand("RW_SETVTAR", 0x8003, "set target speed for the controller [RPM]"),
            Telecommand("RW_SNSPRDX", 0x8004, "set period of the sensor for the motor speed"),

            #---TMTC---#
            Telecommand("TTC_APP_ON", 0xA000, "turn on application TMTC"),
            Telecommand("TTC_APP_OF", 0xA001, "turn off application TMTC"),
            Telecommand("TTC_TM_PRD", 0xA002, "set period of the telemetry thread [ms]")
            ]

        self.telemetryWindows = [
            "Attitude Control",
            "Attitude Determination",
            "IMU",
            "Light Sensor",
            "Magnetic Torquer",
            "Payload",
            "Power",
            "Reaction Wheel"
        ]

        

