from dataclasses import dataclass

@dataclass
class Telecommand():
    word: str
    id: hex
    description: str

@dataclass
class Telemetry():
    topic: str
    format: str

@dataclass
class Plot():
    topic: str
    title: str
    y_label: str
    legend: str

@dataclass
class PlotDataAC():
    yaw_target: float
    yaw_filtered: float
    yaw_speed_target: float
    yaw_speed_filtered: float
    pos_ctrl_out: float
    pos_ctrl_p: float
    pos_ctrl_i: float
    pos_ctrl_d: float
    spd_ctrl_out: float
    spd_ctrl_p: float
    spd_ctrl_i: float
    spd_ctrl_d: float

    def __getitem__(self, index):
        return (self.yaw_target, self.yaw_filtered, self.yaw_speed_target, self.yaw_speed_filtered, self.pos_ctrl_out, self.pos_ctrl_p, self.pos_ctrl_i, self.pos_ctrl_d
                , self.spd_ctrl_out, self.spd_ctrl_p, self.spd_ctrl_i, self.spd_ctrl_d)[index]

@dataclass
class PlotDataAD():
    roll_measured: float
    roll_filtered: float
    pitch_measured: float
    pitch_filtered: float
    yaw_measured: float
    yaw_filtered: float
    yawSpeed_measured: float
    yawSpeed_filtered: float
    

    def __getitem__(self, index):  #enables indexing
        return (self.roll_measured, self.roll_filtered, self.pitch_measured, self.pitch_filtered, self.yaw_measured, self.yaw_filtered, self.yawSpeed_measured
                , self.yawSpeed_filtered)[index]

@dataclass
class PlotDataIMU():
    ax: float
    ay: float
    az: float
    gx: float
    gy: float
    gz: float
    mx: float
    my: float
    mz: float

    def __getitem__(self, index):
        return (self.ax, self.ay, self.az, self.gx, self.gy, self.gz, self.mx, self.my, self.mz)[index]

@dataclass
class PlotDataLS():
    lux: float

    def __getitem__(self, index):
        return (self.lux)[index]

@dataclass
class PlotDataMT():
    pwm_torquer1: float
    pwm_torquer2: float

    def __getitem__(self, index):
        return (self.pwm_torquer1, self.pwm_torquer2)[index]

@dataclass
class PlotDataPL():
    x: float
    #TODO

@dataclass
class PlotDataPW():
    x: float
    #TODO

@dataclass
class PlotDataRW():
    speed_target: float
    speed_filtered: float
    spd_ctrl_out: float
    spd_ctrl_p: float
    spd_ctrl_i: float
    spd_ctrl_d: float

    def __getitem__(self, index):
        return (self.speed_target, self.speed_filtered, self.spd_ctrl_out, self.spd_ctrl_p, self.spd_ctrl_i, self.spd_ctrl_d)[index]

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
            Telecommand("AC_MODEXXX", 0x1006, "set control mode (RW = 0, RWMT = 1, MT = 2)"),

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

        self.telemetry = [
            Telemetry("Attitude Control","  TIME  TMPRD CTRPRD  YAWREF  YAWSPDREF"),
            Telemetry("Attitude Determination","  TIME    TMPRD   ROLL    PITCH      YAW"),
            Telemetry("IMU","  TIME  TMPRD SNSPRD     AX      AY      AZ      GX       GY      GZ       MX      MY      MZ"),
            Telemetry("Light Sensor","  TIME  TMPRD SNSPRD"),
            Telemetry("Magnetic Torquer","  TIME  TMPRD IREF  TRQNR"),
            Telemetry("Payload","  TIME  TMPRD"),
            Telemetry("Power","  TIME   TMPRD  SNSPRD  BATV    BATI   BATPCT   SPLV   SPLI    SPRV   SPRI"),
            Telemetry("Reaction Wheel","  TIME  TMPRD SNSPRD   SPD     SPDREF"),
            Telemetry("Error Messages",""),
            Telemetry("Debug","")
        ]

        self.plots = [
            Plot("Attitude Control","Position Controller System Response","Yaw [deg]","target"),
            Plot("Attitude Control","Position Controller System Response","Yaw [deg]","filtered"),
            Plot("Attitude Control","Speed Controller System Response","Yaw Speed [deg/s]","target"),
            Plot("Attitude Control","Speed Controller System Response","Yaw Speed [deg/s]","filtered"),
            Plot("Attitude Control","Position Controller Info","Speed [deg/s]","output"),
            Plot("Attitude Control","Position Controller Info","Speed [deg/s]","p-term"),
            Plot("Attitude Control","Position Controller Info","Speed [deg/s]","i-term"),
            Plot("Attitude Control","Position Controller Info","Speed [deg/s]","d-term"),
            Plot("Attitude Control","Speed Controller Info","Speed [RPM]","output"),
            Plot("Attitude Control","Speed Controller Info","Speed [RPM]","p-term"),
            Plot("Attitude Control","Speed Controller Info","Speed [RPM]","i-term"),
            Plot("Attitude Control","Speed Controller Info","Speed [RPM]","d-term"),

            Plot("Attitude Determination","Roll","[deg]","measured"),
            Plot("Attitude Determination","Roll","[deg]","filtered"),
            Plot("Attitude Determination","Pitch","[deg]","measured"),
            Plot("Attitude Determination","Pitch","[deg]","filtered"),
            Plot("Attitude Determination","Yaw","[deg]","measured"),
            Plot("Attitude Determination","Yaw","[deg]","filtered"),
            Plot("Attitude Determination","Yaw Speed","[deg/s]","measured"),
            Plot("Attitude Determination","Yaw Speed","[deg/s]","filtered"),

            Plot("IMU","Accelerometer","[g]","x"),
            Plot("IMU","Accelerometer","[g]","y"),
            Plot("IMU","Accelerometer","[g]","z"),
            Plot("IMU","Gyroscope","[deg/s]","x"),
            Plot("IMU","Gyroscope","[deg/s]","y"),
            Plot("IMU","Gyroscope","[deg/s]","z"),
            Plot("IMU","Magnetometer","[gauss]","x"),
            Plot("IMU","Magnetometer","[gauss]","y"),
            Plot("IMU","Magnetometer","[gauss]","z"),

            Plot("Light Sensor","Lux","","measured"),

            Plot("Magnetic Torquer","Torquer Actuation","PWM","torquer1"),
            Plot("Magnetic Torquer","Torquer Actuation","PWM","torquer2"),

            Plot("Payload","","",""),

            Plot("Power","","",""),

            Plot("Reaction Wheel","Speed Controller System Response","Speed [RPM]","target"),
            Plot("Reaction Wheel","Speed Controller System Response","Speed [RPM]","filtered"),
            Plot("Reaction Wheel","Speed Controller Info","PWM","output"),
            Plot("Reaction Wheel","Speed Controller Info","PWM","p-term"),
            Plot("Reaction Wheel","Speed Controller Info","PWM","i-term"),
            Plot("Reaction Wheel","Speed Controller Info","PWM","d-term")
        ]



        

