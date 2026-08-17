import random
from copy import deepcopy
from typing import Dict, List, Union


# === Inlined from long_context.py ===

CAR_STATUS_METADATA_EXTENSION = "Manufacturer: Audi; Model: A6; Year: 2024; EngineType: V6 Turbocharged; Transmission: Automatic 7-speed; DriveType: AWD; FuelType: Gasoline; Passenger: Fastened; SunroofStatus: Closed; GPSLocation: 34.0522N, 118.2437W; Destination: None; EstimatedArrivalTime: None; AudioSystem: On; AudioVolume: 15; RadioStation: 101.1 FM; BluetoothConnected: Yes; ConnectedDevice: iPhone; WiFiStatus: Connected; CellularSignalStrength: 75%; OTAUpdateStatus: No Updates Available; LastServiceDate: 2023-08-15; NextServiceDue: 2024-08-15 or in 12,000 km; OilLevel: Normal; CoolantTemperature: 90C; TransmissionTemperature: 65C; BrakePadWear: Front: 40%, Rear: 35%; TractionControlStatus: On; StabilityControlStatus: On; LaneAssist: Active; BlindSpotMonitor: Active; CollisionWarning: None; ParkingSensors: Front: Clear, Rear: Clear; BackupCamera: Active; SteeringAngle: 0 degrees; CurrentSpeed: 0 km/h; AverageFuelConsumption: 8.2L/100km; TripOdometer: 256 km; TotalOdometer: 45,112 km; FuelRange: 560 km remaining; BatteryHealth: Good; BrakeFluidLevel: Normal; CoolantLevel: Normal; TireTreadDepth: FrontLeft: 7mm, FrontRight: 7mm, RearLeft: 6mm, RearRight: 6mm; KeyFobBatteryLevel: 75%; RemoteStartEnabled: Yes; RemoteLockEnabled: Yes; CabinAirQuality: Good; CarbonDioxideLevel: Low; AirFilterStatus: Normal; ChildLock: Active; RearWindowDefrost: Off; FrontWindowDefrost: Off; Sunshade: Closed; PassengerAirbagStatus: Enabled; DriverAirbagStatus: Enabled; SideAirbagStatus: Enabled; ABSStatus: Active; EngineOilTemperature: 85C; DifferentialTemperature: 60C; TransferCaseTemperature: 62C; ExhaustTemperature: 200C; TurboBoostPressure: Normal; SuspensionStatus: Normal; RideHeight: Normal; DampingForce: Normal; SuspensionMode: Comfort; TowMode: Off; TrailerBrakeController: Not Installed; PayloadCapacity: 800 kg; TowingCapacity: 3,500 kg; RoofLoadCapacity: 100 kg; CurrentLoadWeight: 200 kg; SeatStatus: Driver: Occupied, Passenger: Empty, RearLeft: Empty, RearRight: Occupied; SeatAdjustmentMemory: Driver: Position 1, Passenger: None; MirrorAdjustmentMemory: Driver: Position 1, Passenger: None; PedalAdjustmentMemory: Driver: Position 1; LumbarSupport: Driver: 3/5, Passenger: 2/5; SeatHeating: Driver: Off, Passenger: Off; SeatCooling: Driver: Off, Passenger: Off; ArmRestPosition: Normal; SteeringWheelHeater: Off; ClimateControlSync: On; DefrostingMirrors: Off; FogLights: Off; RearFogLight: Off; LicensePlateLight: On; BrakeLightStatus: On; TurnSignal: Left: Off, Right: Off; HazardLight: Off; DoorOpenAlert: None; SpeedLimitWarning: None; TrafficSignRecognition: Active; AdaptiveCruiseControlStatus: Inactive; AutoParking: Inactive; ParkingAssist: Active; RearCrossTrafficAlert: None; SurroundViewCamera: Off; DigitalRearViewMirror: Off; HeadUpDisplay: Off; NavigationMapUpdate: None; SoftwareVersion: v5.6.2; BatteryRegenerationStatus: Normal; DrivetrainMode: Comfort; GearPosition: Park; IdleTime: 2 minutes; EngineLoad: 15%; FuelInjectionTiming: Normal; SparkTiming: Normal; CylinderDeactivationStatus: Off; ExhaustGasRecirculation: Normal; EmissionControlSystem: Normal; ParticleFilterStatus: Normal; CatalystTemperature: Normal; StartStopSystem: Active; SteeringResponse: Normal; HandlingMode: Sport; ElectronicLimitedSlipDifferential: On; DifferentialLock: Off; EngineVibration: None; BodyRoll: None; YawRate: 0 degrees/sec; AxleLoadDistribution: Front: 60%, Rear: 40%; ChassisStiffness: Normal; GroundClearance: Normal; PowerSteeringStatus: Active; SteeringWheelVibration: None; LockToLockTurns: 2.8; TurningRadius: 11.5 meters; AirbagReadiness: Normal; PreCollisionSystem: Active; ActiveSteeringAssist: Off; HandsOnWheelAlert: None; OccupantClassificationSystem: Active; EventDataRecorderStatus: Normal; BlackBoxRecording: Active; StabilityControlOverride: None; SeatMassager: Off; ArmRestTemperature: Normal; AmbientLightingColor: Blue; SteeringWheelPosition: Normal; HeatedSteeringWheel: Off; PaddleShifters: Off; SportMode: On; PerformanceMode: Off; AutoHighBeamAssist: Off; TireTemperature: FrontLeft: 32C, FrontRight: 32C, RearLeft: 34C, RearRight: 34C; BrakeRotorTemperature: FrontLeft: 150C, FrontRight: 150C, RearLeft: 130C, RearRight: 130C; MirrorHeating: Off; FuelTankPressure: Normal; EvaporativeEmissionSystem: Normal; GasCapStatus: Closed; FuelDoorStatus: Closed; BatteryChargerStatus: None; ChargingCableConnected: No; ChargerType: None; ChargingPortLight: Off; HighVoltageBatteryInsulation: Normal; HighVoltageBatteryTemperature: Normal; RegenerativeBrakingForce: Normal; BatteryCoolingSystem: Normal; BatteryHeatingSystem: Off; ExteriorTemperature: 20C; WiperFluidLevel: Normal; WasherNozzleHeated: Off; EngineSoundEnhancer: Off; VehicleSoundForPedestrians: Off; ExhaustFlapControl: Normal; EngineCoolingFanStatus: Off; TransmissionOilPressure: Normal; TransmissionOilTemperature: 70C; ThrottleBodyStatus: Normal; IntakeManifoldPressure: Normal; CabinNoiseLevel: Low; SunshadePosition: Closed; RearSunshade: Off; LuggageCompartmentLight: Off; RearSeatBeltReminder: None; RearSeatOccupancySensor: Active; FrontCrashZoneSensors: Active; SideCrashSensors: Active; RearCrashSensors: Active; TireSealantStatus: Full; TireJackStatus: Present; EmergencyKitStatus: Present; SpareTireStatus: Present; Owner'sManualLocation: GloveBox; FirstAidKitLocation: Trunk; FireExtinguisherLocation: Trunk; ChildSeatAnchors: Installed; RoofRackStatus: Not Installed; VehicleWrap: None; RoofColor: BodyColor; PaintProtectionFilm: None; CeramicCoating: None; WheelType: Alloy; WheelSize: 19 inches; WheelBoltTorque: Normal; TireSidewallDamage: None; WheelRimDamage: None; VehicleWarrantyStatus: Active; RoadsideAssistanceStatus: Active; MaintenancePlanStatus: Active; LeaseStatus: Not Leased; FinancingStatus: PaidOff; VehicleTitleStatus: Clear; NumberOfKeys: 2; KeyMemoryStatus: Active; VehicleHistoryReport: Clean; VINNumber: WAUZZZF4XNA123456; RegistrationStatus: Active; InsuranceStatus: FullCoverage; InsuranceProvider: StateFarm; InsuranceExpirationDate: 2025-04-10; RoadTaxStatus: Paid; GarageLocation: Home; LastGarageEntryTime: 2024-04-15 08:30; AlarmSystemStatus: Armed; SecuritySystem: Enabled; AntiTowSystem: Enabled; GlassBreakSensor: Active; MotionSensor: Active; TintedWindows: Yes; DashcamStatus: On; DashcamRecording: Active; DashcamStorage: 128GB; DashcamBatteryLevel: 90%; AdditionalAccessories: RoofBoxInstalled: No; RoofTent: No; TrailerHitch: Installed; Winch: Not Installed; SnowChains: Not Installed; FogLightCovers: Installed; GrilleGuard: Not Installed; RoofLightBar: Not Installed."

LONG_WEATHER_EXTENSION = {'-1_day': {'windSpeed': 15.0, 'humidity': 75.0, 'precipitation': 5.0, 'uvIndex': 6, 'visibility': 8.0, 'airPressure': 1010.0, 'dewPoint': 10.0}, '-2_day': {'windSpeed': 10.0, 'humidity': 65.0, 'precipitation': 2.0, 'uvIndex': 7, 'visibility': 9.0, 'airPressure': 1020.0, 'dewPoint': 8.0}, '-3_day': {'windSpeed': 20.0, 'humidity': 85.0, 'precipitation': 0.0, 'uvIndex': 5, 'visibility': 7.0, 'airPressure': 1005.0, 'dewPoint': 12.0}, '-4_day': {'windSpeed': 18.0, 'humidity': 80.0, 'precipitation': 1.0, 'uvIndex': 6, 'visibility': 9.0, 'airPressure': 1008.0, 'dewPoint': 9.0}, '-5_day': {'windSpeed': 12.0, 'humidity': 70.0, 'precipitation': 3.0, 'uvIndex': 8, 'visibility': 10.0, 'airPressure': 1015.0, 'dewPoint': 11.0}, '-6_day': {'windSpeed': 16.0, 'humidity': 72.0, 'precipitation': 4.0, 'uvIndex': 7, 'visibility': 9.0, 'airPressure': 1009.0, 'dewPoint': 10.0}, '-7_day': {'windSpeed': 14.0, 'humidity': 68.0, 'precipitation': 6.0, 'uvIndex': 6, 'visibility': 8.0, 'airPressure': 1012.0, 'dewPoint': 7.0}, '-8_day': {'windSpeed': 17.0, 'humidity': 78.0, 'precipitation': 0.5, 'uvIndex': 5, 'visibility': 9.0, 'airPressure': 1013.0, 'dewPoint': 8.0}, '-9_day': {'windSpeed': 19.0, 'humidity': 82.0, 'precipitation': 0.0, 'uvIndex': 6, 'visibility': 10.0, 'airPressure': 1011.0, 'dewPoint': 9.0}, '-10_day': {'windSpeed': 13.0, 'humidity': 74.0, 'precipitation': 2.5, 'uvIndex': 7, 'visibility': 9.5, 'airPressure': 1014.0, 'dewPoint': 10.0}, '-11_day': {'windSpeed': 11.0, 'humidity': 70.0, 'precipitation': 1.5, 'uvIndex': 6, 'visibility': 8.5, 'airPressure': 1016.0, 'dewPoint': 8.5}, '-12_day': {'windSpeed': 15.0, 'humidity': 75.0, 'precipitation': 5.0, 'uvIndex': 6, 'visibility': 8.0, 'airPressure': 1010.0, 'dewPoint': 10.0}, '-13_day': {'windSpeed': 10.0, 'humidity': 65.0, 'precipitation': 2.0, 'uvIndex': 7, 'visibility': 9.0, 'airPressure': 1020.0, 'dewPoint': 8.0}, '-14_day': {'windSpeed': 20.0, 'humidity': 85.0, 'precipitation': 0.0, 'uvIndex': 5, 'visibility': 7.0, 'airPressure': 1005.0, 'dewPoint': 12.0}, '-15_day': {'windSpeed': 18.0, 'humidity': 80.0, 'precipitation': 1.0, 'uvIndex': 6, 'visibility': 9.0, 'airPressure': 1008.0, 'dewPoint': 9.0}}

PARKING_BRAKE_INSTRUCTION = "The parking brake, also commonly referred to as the handbrake or emergency brake, is an essential safety component in vehicles. While its primary function is to secure the vehicle when parked, preventing it from rolling forward or backward, it also serves as an emergency stopping mechanism under certain conditions. It is crucial to understand the correct way to use a parking brake to ensure both safety and vehicle longevity. This guide will cover the fundamentals of proper parking brake use, its function, maintenance, and additional tips for various scenarios. Understanding the Parking Brake Mechanism Before diving into the right use, it's essential to understand how the parking brake operates. The parking brake is an independent braking system, separate from the main hydraulic brake system that is used while driving. When engaged, the parking brake applies pressure directly to the vehicle’s rear wheels, locking them in place and preventing movement. In most vehicles, the parking brake is either a lever, a pedal, or an electronic switch. - Lever-style parking brake: This is the most traditional type of parking brake, commonly found between the driver and passenger seats. Pulling the lever engages the brake, and releasing it disengages it. - Pedal-style parking brake: Often found in vehicles with automatic transmissions, this brake is engaged by pressing a pedal located on the far left side of the driver's footwell. A separate release lever or pedal is typically used to disengage the brake. - Electronic parking brake: In modern vehicles, especially those with advanced technological features, the parking brake may be engaged and disengaged with a button or switch. This system automatically applies and releases the brake when necessary, often integrating with other safety features like hill-start assist. When to Use the Parking Brake The parking brake should be used in several situations to ensure that your vehicle remains secure and does not roll unintentionally. Here are the most common circumstances when you should engage the parking brake: 1. When Parking on a Hill or Slope: Parking on an incline is one of the most important times to use the parking brake. Regardless of whether you drive a manual or automatic vehicle, the parking brake provides extra security by ensuring that your car remains stationary even if the primary brakes fail. In vehicles with manual transmissions, leaving the car in gear will add an extra layer of security. For automatic vehicles, ensure the car is in the Park position. Always turn your wheels toward the curb when parking uphill or downhill to minimize the risk of your vehicle rolling into traffic if the brake should fail. 2. When Parking on Level Ground: While using the parking brake on flat ground may not seem necessary, it's still a good practice. Engaging the parking brake takes the strain off the transmission, preventing unnecessary wear and tear. In the case of automatic vehicles, using the parking brake in conjunction with the Park position keeps the car more securely in place. 3. During Emergency Stops: While not typically recommended, the parking brake can be used in emergencies if the primary hydraulic braking system fails. Pulling the parking brake lever slowly and steadily can help reduce speed. However, sudden engagement of the parking brake can cause the rear wheels to lock, resulting in loss of control. Only use it cautiously in situations where you have no other option. Modern electronic parking brakes often feature an automatic emergency braking function that can be activated with a hard press or hold, giving the driver more control over deceleration. 4. While Towing: When towing a vehicle, the parking brake should always be engaged to prevent rolling while loading or unloading. Similarly, when a trailer is attached, ensure the parking brake is engaged when the vehicle is stationary to provide additional security. 5. At Traffic Lights or Stop Signs on a Hill: If you're stopped on a hill, especially in a vehicle with a manual transmission, engaging the parking brake temporarily can prevent rolling backward when you release the foot brake to move forward again. Some vehicles come equipped with hill-start assist systems, but if yours does not, the parking brake is an effective alternative. How to Properly Engage and Disengage the Parking Brake Using the parking brake is relatively simple, but there are a few steps to ensure you're doing it correctly: 1. Engaging the Parking Brake: For a lever-style brake: Pull the lever upwards until you feel resistance and the brake locks in place. Some cars require you to press a button on the end of the lever while pulling it up. The brake lever should remain in the upright position when engaged. For a pedal-style brake: Firmly press the pedal down until it clicks and stays locked in place. The brake is now engaged. For an electronic brake: Press the button or switch to engage the brake. A light on the dashboard will usually indicate that the parking brake is active. 2. Disengaging the Parking Brake: For a lever-style brake: Pull the lever up slightly to release pressure, then press the button on the end and lower the lever fully to disengage the brake. For a pedal-style brake: Either pull the release lever or press the brake pedal again to unlock and disengage it. For an electronic brake: Simply press the button or switch again to disengage the brake. Some vehicles will automatically disengage the parking brake when you press the accelerator pedal, especially if you're in gear and ready to move. Common Mistakes When Using the Parking Brake There are several mistakes that drivers commonly make when using the parking brake. Avoid these errors to prolong the life of the brake and maintain your vehicle's safety: 1. Not Using the Parking Brake: One of the most common mistakes is neglecting to use the parking brake at all. Relying solely on the transmission's Park function (for automatic vehicles) or leaving the vehicle in gear (for manual vehicles) can result in unnecessary stress on the transmission system, especially on hills or inclines. 2. Driving With the Parking Brake Engaged: Forgetting to disengage the parking brake before driving can cause serious damage to your vehicle’s braking system. The brake pads can overheat, warp, or wear prematurely. Always make sure the parking brake is fully disengaged before you start driving. In most cars, a dashboard light will indicate whether the parking brake is engaged. 3. Pulling the Parking Brake Too Hard: Over-tensioning the parking brake by pulling it too hard can cause cables to stretch or snap over time, leading to costly repairs. Pull the brake lever firmly but avoid excessive force. 4. Using the Parking Brake Inappropriately in an Emergency: In a panic situation, some drivers may instinctively pull the parking brake, causing the rear wheels to lock up. This can lead to skidding or spinning, particularly at high speeds. Instead, if you experience a brake failure, try to downshift and use engine braking first. The parking brake should only be used gradually in emergencies. Maintenance and Care for the Parking Brake Regular maintenance of the parking brake is crucial for ensuring its long-term effectiveness. Like any other part of your vehicle, the parking brake can wear down over time and may require adjustment or repair. Follow these tips to keep your parking brake in good condition: 1. Use the Parking Brake Regularly: Even if you drive mostly on flat surfaces, using the parking brake regularly helps keep the components in working order. Regular use ensures that the cables do not rust or seize. 2. Check for Tension: If the parking brake feels too loose or too tight, it may need adjustment. A loose brake may not hold the vehicle securely, while an overly tight brake can cause unnecessary strain on the system. Have your parking brake checked by a mechanic during routine vehicle maintenance to ensure it's properly adjusted. 3. Lubricate the Cables: If your parking brake uses a cable system (lever or pedal style), periodic lubrication can help prevent rust and ensure smooth operation. Electronic parking brakes usually don’t require this kind of maintenance. 4. Listen for Warning Signs: If you hear squeaking or grinding noises when engaging or disengaging the parking brake, it could indicate worn brake components. Get the system inspected to prevent further damage. 5. Test the Parking Brake on a Hill: Periodically test the effectiveness of the parking brake by parking on a slight incline. Engage the brake and see if the car remains stationary. If the vehicle rolls or the brake feels weak, it's time for a professional check-up. Parking Brake Use in Special Conditions 1. Cold Weather: In extremely cold temperatures, moisture can freeze around the parking brake cables, causing them to seize. If you live in a cold climate, be cautious about using the parking brake during freezing weather. If the brake does seize, do not try to force it. Instead, let the vehicle warm up, which may melt the ice, or consult a professional mechanic. 2. Off-Road Conditions: If you frequently drive in muddy or dusty conditions, inspect the parking brake regularly. Dirt and debris can accumulate around the brake components, causing them to function improperly. 3. Towing and Parking on Steep Inclines: When towing or parking on an extremely steep incline, engage both the parking brake and use wheel chocks for added safety. This will reduce the risk of the vehicle rolling. By following these instructions and guidelines, you will ensure that your parking brake is used effectively, maintaining both your vehicle's safety and functionality."

INTERMEDIARY_CITIES = ['New Hamilton', 'Jacksonville', 'Fort Stoneport', 'Lincolnville', 'Madison', 'Clayton Hillport', 'Franklin Heights', 'Old Jefferson', 'Bentondale', 'Sullivan Springs', 'Red Monroe', 'Newtonburg', 'Green Clay', 'East Kingston', 'West Princeton', 'Grand Georgetown', 'Andersonfield', 'Richmond', 'Shelbyton', 'Hamptonfield', 'Fultondale', 'Hudsonview', 'Carsonville', 'Lawrenceburg', 'Masonport', 'Bristol', 'New Clayton', 'Bensondale', 'Clarkville', 'Dawsonsprings', 'Ellisport', 'Floyd', 'Graysonville', 'Hayesburg', 'Irvington', 'Jasperburg', 'Kentport', 'Lamarburg', 'Morganton', 'Nortonville', 'Owenport', 'Perryville', 'Quincyburg', 'Russellton', 'Shermanburg', 'Taylor', 'Uptonville', 'Vernon', 'Wilsonburg', 'Youngtown', 'Zionville', 'Newfield', 'Sanport', 'Fortburg', 'Mountview', 'Lakeport', 'Northfield', 'Southport', 'Eastwood', 'Westdale', 'Grandview', 'Greenwood', 'Redfield', 'Oldtown', 'Saintport', 'Glenwood', 'Springfield', 'Riverdale', 'Rockville', 'Whitefield', 'Blackport', 'Blueburg', 'Silverdale', 'Goldton', 'Crystal Springs', 'Fairview', 'Highfield', 'Lowtown', 'Brightwood', 'Shadowbrook', 'Sunridge', 'Moonlake', 'Starpoint', 'Oakwood', 'Pinecrest', 'Mapleton', 'Cedar Grove', 'Ashland', 'Willowbrook', 'Elmdale', 'Birchwood', 'Greenfield', 'Redwood', 'Oldbridge', 'Saintsville', 'Glendale', 'Springtown', 'Riverport', 'Rockford', 'Whitehaven', 'Blackburn', 'Bluewater', 'Silverton', 'Goldfield', 'Crystal Bay', 'Fairhaven', 'Highpoint', 'Lowridge', 'Brighton', 'Shadow Valley', 'Sun City', 'Moontown', 'Star Lake', 'Oak Ridge', 'Pine Hill', 'Maple Grove', 'Cedar Point', 'Ashville', 'Willow Creek', 'Elmwood', 'Birch Bay', 'River Falls', 'Rock Hill', 'White Plains', 'Black Lake', 'Blue Ridge', 'Silver Springs', 'Golden Grove', 'Crystal Cove', 'Fair Oaks', 'Highland', 'Lowville', 'Bright Meadows', 'Shadow Creek', 'Sunrise', 'Moondale', 'Star City', 'Oakton', 'Pine Valley', 'Maple Ridge', 'Cedar Falls', 'Ashford', 'Willow Springs', 'Elmsford', 'Birchwood', 'River City', 'Rockport', 'Whitewater', 'Blackstone', 'Blue Hills', 'Silver Lake', 'Gold Beach', 'Crystal River', 'Fairfield', 'Highview', 'Low Point', 'Brighton Beach', 'Shadow Lake', 'Sunset', 'Moorestown', 'Star City', 'Oakland', 'Pine City', 'Mapleton', 'Cedar Springs', 'Ash Grove', 'Willowdale', 'Elm Creek', 'Birch Grove', 'River Ridge', 'Rock Valley', 'White Sands', 'Black Rock', 'Blue River', 'Silver Creek', 'Gold Hill', 'Crystal Lake', 'Fairview Heights', 'High Springs', 'Low Gap', 'Bright City', 'Shadow Mountain', 'Sun Valley', 'Moonlight', 'Star Harbor', 'Oak Hollow', 'Pine Grove', 'Maple Valley', 'Cedar Ridge', 'Ash Point', 'Willow Glen', 'Elm Springs', 'Birch Creek', 'Riverside', 'Rockport', 'White Rock', 'Blackwood', 'Blue Mountain', 'Silver City', 'Golden Valley', 'Crystal Springs', 'Fairhope', 'Highland Park', 'Lowtown', 'Brighton Hills', 'Shadow Creek', 'Sunbrook', 'Moon City', 'Star View', 'Oakdale', 'Pinecrest', 'Maple Hill', 'Cedar City', 'Ashwood', 'Willow Valley', 'Elmwood Park', 'Birch Meadow', 'Riverbend', 'Rockland', 'White Mountain', 'Black Creek', 'Blue Ridge', 'Silverton', 'Gold River', 'Crystal Hill', 'Fairmont', 'Highland Springs', 'Lowville', 'Brightwood', 'Shadow Valley', 'Sunbrook', 'Moonside', 'Star City', 'Oak Grove', 'Pine Valley', 'Maple Creek', 'Cedar Lake', 'Ash Hill', 'Willow Creek', 'Elmhurst', 'Birchwood', 'River City', 'Rock Falls', 'Whitehaven', 'Black River', 'Blue Mountain', 'Silver Lake', 'Gold Hill', 'Crystal City', 'Fairhaven', 'High Point', 'Low Gap', 'Brighton', 'Shadow Creek', 'Sun Valley', 'Moon Lake', 'Star Hill', 'Oakwood', 'Pine Ridge', 'Maple Valley', 'Cedar Grove', 'Ashland', 'Willowbrook', 'Elmwood', 'Birch Grove', 'Riverport', 'Rock City', 'White Plains', 'Blackburn', 'Blue Hills', 'Silverton', 'Golden Grove', 'Crystal Cove', 'Fairview', 'Highland', 'Lowtown', 'Brighton', 'Shadow Lake', 'Sunrise', 'Moontown', 'Star Lake', 'Oak Hill', 'Pine Meadow', 'Mapleton', 'Cedar Bluff', 'Ashford', 'Willow Creek', 'Elm Grove', 'Birchwood', 'Green Valley', 'Redstone', 'Old Mill', 'Saintsville', 'Glenview', 'Springfield', 'Riverdale', 'Rockport', 'Whitewater', 'Blackwood', 'Bluefield', 'Silvertown', 'Gold Creek', 'Crystal Falls', 'Fairbank', 'Highfield', 'Lowville', 'Brighton', 'Shadowbrook', 'Sunridge', 'Moonhaven', 'Starpoint', 'Oakton', 'Pinecrest', 'Maple Ridge', 'Cedar Springs', 'Ashland', 'Willowbrook', 'Elmdale', 'Birchwood', 'Greenfield', 'Redwood', 'Oldbridge', 'Saintport', 'Glenwood', 'Springtown', 'Riverport', 'Rockford', 'Whitehaven', 'Blackburn', 'Bluewater', 'Silverton', 'Goldfield', 'Crystal Bay', 'Fairhaven', 'Highpoint', 'Lowridge', 'Brighton', 'Shadow Valley', 'Sun City', 'Moontown', 'Star Lake', 'Oak Ridge', 'Pine Hill', 'Maple Grove', 'Cedar Point', 'Ashville', 'Willow Creek', 'Elmwood', 'Birch Bay', 'River Falls', 'Rock Hill', 'White Plains', 'Black Lake', 'Blue Ridge', 'Silver Springs', 'Golden Grove', 'Crystal Cove', 'Fair Oaks', 'Highland', 'Lowville', 'Bright Meadows', 'Shadow Creek', 'Sunrise', 'Moondale', 'Star City', 'Oakton', 'Pine Valley', 'Maple Ridge', 'Cedar Falls', 'Ashford', 'Willow Springs', 'Elmsford', 'Birchwood', 'River City', 'Rockport', 'Whitewater', 'Blackstone', 'Blue Hills', 'Silver Lake', 'Gold Beach', 'Crystal River', 'Fairfield', 'Highview', 'Low Point', 'Brighton Beach', 'Shadow Lake', 'Sunset', 'Moorestown', 'Star City', 'Oakland', 'Pine City', 'Mapleton', 'Cedar Springs', 'Ash Grove', 'Willowdale', 'Elm Creek', 'Birch Grove', 'River Ridge', 'Rock Valley', 'White Sands', 'Black Rock', 'Blue River', 'Silver Creek', 'Gold Hill', 'Crystal Lake', 'Fairview Heights', 'High Springs', 'Low Gap', 'Bright City', 'Shadow Mountain', 'Sun Valley', 'Moonlight', 'Star Harbor', 'Oak Hollow', 'Pine Grove', 'Maple Valley', 'Cedar Ridge', 'Ash Point', 'Willow Glen', 'Elm Springs', 'Birch Creek', 'Riverside', 'Rockport', 'White Rock', 'Blackwood', 'Blue Mountain', 'Silver City', 'Golden Valley', 'Crystal Spring', 'Greenstone', 'Grandchester', 'Hillbrook', 'Redfield', 'Bridgeton', 'Forest Heights', 'Mountainview', 'Stone Harbor', 'Seaford', 'Crestwood', 'Hillcrest', 'Summitville', 'Waterford', 'Silverstone', 'Lakeshore', 'New River', 'Riverbank', 'Forestport', 'Hightower', 'Midland', 'Pineville', 'Hollow Ridge', 'Ridgeway', 'Sunset Valley', 'Moonlight Bay', 'Hilltown', 'Blue Valley', 'Snowhill', 'Lakewood', 'Eagle Ridge', 'Bayfield', 'Windmill', 'Canyon Valley', 'Cypress Grove', 'Foxwood', 'Pine Grove', 'Evergreen Hill', 'Green Hills', 'Limestone', 'Oceanview', 'Sandalwood', 'Whitestone', 'Timberwood', 'Winterhaven', 'Desert Springs', 'Pinewood', 'Foxburg', 'Haven Ridge', 'Rocky River', 'Shoreview', 'Greystone', 'Fernhill', 'Stoneville', 'Sandridge', 'Highgate', 'Redwater', 'Elmwood Springs', 'Silver Glen', 'Woodside', 'Forest Glen', 'Clearbrook', 'Lakeside', 'Hawkstone', 'Greenbriar', 'Dalesville', 'Brighton Point', 'Highland Bay', 'Brookstone', 'Grand Terrace', 'Ironwood', 'Bluerock', 'Glacier Ridge', 'Wolf Creek', 'Windy Ridge', 'Maple Springs', 'Shady Valley', 'Crescent Ridge', 'Wildwood', 'Shadow Hills', 'Riverstone', 'Canyon Creek', 'Woodland Springs', 'Crystalfall', 'Longstone', 'Moonridge', 'Maplepoint', 'Sunset Hills', 'Frostvalley', 'Eaglewood', 'Woodsford', 'Brookfield', 'Iron Ridge', 'Fossil Ridge', 'Spring Hill', 'Oceancrest', 'Firestone', 'Evergreen Lake', 'Frost Haven', 'Stonecrest', 'Willowstone', 'Stonebridge', 'Shady Hills', 'Forest Edge', 'Treetop Hill', 'Fairbank Heights', 'Hawk Valley', 'Stonegate', 'Timber Ridge', 'Glacier Springs', 'Windward', 'Summit Edge', 'Fox Ridge', 'Elmwood Heights', 'Whitewater Springs', 'Cypress Bay', 'Pine Valley', 'Rivergate', 'Eagleport', 'Sandwood', 'Birchfield', 'Sunrise Grove', 'Meadow Brook', 'Bluffwood', 'Green Lake', 'Oceanstone', 'Shady Brook', 'Granite Ridge', 'Rockstone', 'Hollycrest', 'Summit Ridge', 'Edgewater Springs', 'Eagle Peak', 'Misty Hills', 'River Valley', 'Pineview', 'Lakeview Ridge', 'Stonewater', 'Silver Ridge', 'Greenstone Falls', 'Seaside Valley', 'Willowbend', 'Baystone', 'Sandbrook', 'Cliffside', 'Fernwood', 'Crystal Ridge', 'Oceancrest', 'Foxbridge', 'Seaview', 'Meadowridge', 'Canyon Hill', 'Whitestone Ridge', 'Lakeshore Hills', 'Timberland', 'Wolfstone', 'Willowridge', 'Granite Creek', 'Shadowridge', 'Ocean Bluff', 'Bright Creek', 'Evergreen Ridge', 'Lakeshore Heights', 'Fernhill Springs', 'Sandhill Grove', 'Glacier Hill', 'Clearwater Ridge', 'Stonewall Heights', 'Pine Ridge', 'Shady Grove', 'Timber Cove', 'Green Ridge', 'Iron Ridge', 'Hightower Point', 'Windy Ridge', 'Eagle Valley', 'Sunset Crest', 'Silver Heights', 'Seaside Springs', 'Misty Valley', 'Woodland Grove', 'Shadowbrook Grove', 'Shady Brook', 'Evergreen Crest', 'Stonegate Valley', 'Cypress Hills', 'Moonlight Valley', 'Cedar Valley', 'Brookhaven Springs', 'Riverbend Valley', 'Seaside Grove', 'Glacier Ridge', 'Ironstone Point', 'Foxwood Springs', 'Oceanstone Valley', 'Fernwood Cove', 'Lakeside Grove', 'Seabrook', 'Misty Lake', 'Greenfield Hill', 'Oceanview Ridge', 'Silver Creek', 'Redwood Valley', 'Riverstone Point', 'Clearwater Springs', 'Greenleaf Valley', 'Shadowbrook Grove', 'Sunset Hills', 'Treetop Heights', 'Windstone Hill', 'Willowford', 'Blueridge Grove', 'Timber Ridge', 'Misty River', 'Redwood Springs', 'Meadow Ridge', 'Lakeside Valley', 'Shady Cove', 'Crystal Shore', 'Granite Creek', 'Ironstone Valley', 'Foxwood Glen', 'Seaview Ridge', 'Treetop Hill', 'Baystone Valley', 'Blueridge Point', 'Pinebrook Ridge', 'Canyonbrook', 'Granite Springs', 'Riverstone Cove', 'Clearwater Valley', 'Silver Ridge', 'Eagle Creek', 'Willowbrook', 'Shady Creek', 'Timberstone Ridge', 'Meadowbrook', 'Bay Ridge', 'Sandridge Point', 'Eaglewood Heights', 'Misty Grove', 'Greenstone Point', 'Clearview', 'Silverstone Heights', 'Oceancrest Ridge', 'Granite Point', 'Meadowdale', 'Canyon Ridge', 'Bluffridge', 'Ironstone Ridge', 'Foxbrook Heights', 'Pine Ridge', 'Shoreline Crest', 'Timberland Ridge', 'Meadowcrest', 'Stonegate Grove', 'Fernwood Springs', 'Brookstone Valley', 'Evergreen Hills', 'Greenstone Ridge', 'Oceanstone Point', 'Brighton Crest', 'Canyonbrook', 'Wolfstone Ridge', 'Ironstone Cove', 'Fox Ridge', 'Pinehill Grove', 'Crystal River', 'Clearview Point', 'Seaside Valley', 'Hollow Ridge', 'Misty Creek', 'Shady Valley', 'Riverstone Heights', 'Blueridge Cove', 'Evergreen Grove', 'Greenfield Ridge', 'Timberstone Point', 'Shady Brook', 'Clearview Valley', 'Silverstone Hill', 'Oceanstone Springs', 'Fernhill Ridge', 'Fox Ridge', 'Meadowridge Point', 'Shady Crest', 'Timber Ridge', 'Evergreen Springs', 'Foxwood Glen', 'Seaview Heights', 'Granite Ridge', 'Ocean Ridge', 'Rivergate Valley', 'Seaside Grove', 'Clearview Springs', 'Silverstone Point', 'Foxwood Ridge', 'Timberstone Point', 'Pinebrook Crest', 'Riverstone Grove', 'Granite Ridge', 'Blueridge Valley', 'Meadowbrook Point', 'Ironstone Valley', 'Cypress Springs', 'Crystal Ridge', 'Evergreen Springs', 'Silver Creek', 'Greenridge Valley', 'Lakeside Ridge', 'Shady Ridge', 'Baystone Grove', 'Crystal Grove', 'Treetop Valley', 'Seaside Crest', 'Clearwater Ridge', 'Oceanstone Ridge', 'Bluffwood Grove', 'Fernhill Point', 'Silverstone Springs', 'Clearwater Point', 'Greenwood Valley', 'Shadybrook Ridge', 'Brightwood Ridge', 'Willowbrook Grove', 'Timberland Ridge', 'Crystal Springs', 'Granite Ridge', 'Foxbrook Springs', 'Lakeside Heights', 'Shady Brook', 'Greenstone Ridge', 'Oceancrest Valley', 'Blueridge Ridge', 'Canyon Ridge', 'Clearbrook Point', 'Fernhill Ridge', 'Pinecrest Heights', 'Ironstone Grove', 'Meadowstone Ridge', 'Baystone Heights', 'Crystal Valley', 'Seaside Springs', 'Silverton Springs', 'Evergreen Point', 'Granite Ridge', 'Meadowbrook Ridge', 'Lakeside Point', 'Clearwater Springs', 'Brightwood Point', 'Silverstone Ridge', 'Seaside Ridge', 'Crystal Shores', 'Evergreen Crest', 'Granite Point', 'Seaside Crest', 'Clearwater Valley', 'Fernhill Valley', 'Baystone Ridge', 'Riverstone Grove', 'Shadybrook Ridge', 'Foxbrook Point', 'Timberstone Point', 'Brightwood Ridge', 'Evergreen Springs', 'Seaside Ridge', 'Granite Valley', 'Crystal Ridge', 'Shadybrook Springs', 'Foxbrook Ridge', 'Pinecrest Grove', 'Willowbrook Valley', 'Canyon Ridge', 'Clearwater Ridge', 'Oceancrest Point', 'Seaside Heights', 'Shadybrook Ridge', 'Baystone Heights', 'Pinebrook Ridge', 'Foxbrook Valley', 'Granite Ridge', 'Shadybrook Valley', 'Clearwater Grove', 'Evergreen Ridge', 'Willowbrook Ridge', 'Granite Ridge', 'Shadybrook Grove', 'Willowbrook Grove', 'Foxbrook Point', 'Clearwater Ridge', 'Silverstone Ridge', 'Shadybrook Valley', 'Clearwater Ridge', 'Seaside Grove', 'Willowbrook Valley', 'Shadybrook Valley', 'Seaside Ridge', 'Willowbrook Ridge']


MAX_FUEL_LEVEL = 50
MIN_FUEL_LEVEL = 0.0
MILE_PER_GALLON = 20.0
MAX_BATTERY_VOLTAGE = 14.0
MIN_BATTERY_VOLTAGE = 10.0

DEFAULT_STATE = {
    "random_seed": 141053,
    "fuelLevel": 0.0,
    "batteryVoltage": 12.6,
    "engine_state": "stopped",
    "remainingUnlockedDoors": 4,
    "doorStatus": {
        "driver": "unlocked",
        "passenger": "unlocked",
        "rear_left": "unlocked",
        "rear_right": "unlocked",
    },
    "acTemperature": 25.0,
    "fanSpeed": 50,
    "acMode": "auto",
    "humidityLevel": 50.0,
    "headLightStatus": "off",
    "parkingBrakeStatus": "released",
    "_parkingBrakeForce": 0.0,
    "_slopeAngle": 0.0,
    "brakePedalStatus": "released",
    "brakePedalForce": 0.0,
    "distanceToNextVehicle": 50.0,
    "cruiseStatus": "inactive",
    "destination": "None",
    "frontLeftTirePressure": 32.0,
    "frontRightTirePressure": 32.0,
    "rearLeftTirePressure": 30.0,
    "rearRightTirePressure": 30.0,
}

class VehicleControlAPI:

    def __init__(self):
        """
        Initializes the vehicle control API with default values.
        """
        self.fuelLevel: float
        self.batteryVoltage: float
        self.engine_state: str
        self.remainingUnlockedDoors: int
        self.doorStatus: Dict[str, str]

        self.acTemperature: float
        self.fanSpeed: int
        self.acMode: str
        self.humidityLevel: float
        self.headLightStatus: str
        self.parkingBrakeStatus: str
        self._parkingBrakeForce: float
        self._slopeAngle: float
        self.brakePedalStatus: str
        self._brakePedalForce: float
        self.distanceToNextVehicle: float
        self.cruiseStatus: str
        self.destination: str
        self.frontLeftTirePressure: float
        self.frontRightTirePressure: float
        self.rearLeftTirePressure: float
        self.rearRightTirePressure: float
        self._api_description = "This tool belongs to the vehicle control system, which allows users to control various aspects of the car such as engine, doors, climate control, lights, and more."

    def _load_scenario(self, scenario: dict, long_context=False) -> None:
        """
        Loads the scenario for the vehicle control.
        Args:
            scenario (Dict): The scenario to load.
        """
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self._random = random.Random(
            (scenario.get("random_seed", DEFAULT_STATE_COPY["random_seed"]))
        )
        self.random_seed = scenario.get("random_seed", DEFAULT_STATE_COPY["random_seed"])
        self.fuelLevel = scenario.get(
            "fuelLevel", DEFAULT_STATE_COPY["fuelLevel"]
        )  # in gallons
        self.batteryVoltage = scenario.get(
            "batteryVoltage", DEFAULT_STATE_COPY["batteryVoltage"]
        )  # in volts
        self.engine_state = scenario.get(
            "engine_state", DEFAULT_STATE_COPY["engine_state"]
        )  # running, stopped
        self.remainingUnlockedDoors = scenario.get(
            "remainingUnlockedDoors", DEFAULT_STATE_COPY["remainingUnlockedDoors"]
        )  # driver, passenger, rear_left, rear_right
        self.doorStatus = scenario.get(
            "doorStatus",
            DEFAULT_STATE_COPY["doorStatus"],
        )
        self.remainingUnlockedDoors = 4 - len(
            [1 for door in self.doorStatus.keys() if self.doorStatus[door] == "locked"]
        )
        self.acTemperature = scenario.get(
            "acTemperature", DEFAULT_STATE_COPY["acTemperature"]
        )  # in degree Celsius
        self.fanSpeed = scenario.get("fanSpeed", DEFAULT_STATE_COPY["fanSpeed"])  # 0 to 100
        self.acMode = scenario.get(
            "acMode", DEFAULT_STATE_COPY["acMode"]
        )  # auto, cool, heat, defrost
        self.humidityLevel = scenario.get(
            "humidityLevel", DEFAULT_STATE_COPY["humidityLevel"]
        )  # in percentage
        self.headLightStatus = scenario.get(
            "headLightStatus", DEFAULT_STATE_COPY["headLightStatus"]
        )  # on, off
        self.parkingBrakeStatus = scenario.get(
            "parkingBrakeStatus", DEFAULT_STATE_COPY["parkingBrakeStatus"]
        )  # released, engaged
        self._parkingBrakeForce = scenario.get(
            "_parkingBrakeForce", DEFAULT_STATE_COPY["_parkingBrakeForce"]
        )  # in Newtons
        self._slopeAngle = scenario.get(
            "_slopeAngle", DEFAULT_STATE_COPY["_slopeAngle"]
        )  # in degrees
        self.brakePedalStatus = scenario.get(
            "brakePedalStatus", DEFAULT_STATE_COPY["brakePedalStatus"]
        )  # pressed, released
        self._brakePedalForce = scenario.get(
            "brakePedalForce", DEFAULT_STATE_COPY["brakePedalForce"]
        )  # in Newtons
        self.distanceToNextVehicle = scenario.get(
            "distanceToNextVehicle", DEFAULT_STATE_COPY["distanceToNextVehicle"]
        )  # in meters
        self.cruiseStatus = scenario.get(
            "cruiseStatus", DEFAULT_STATE_COPY["cruiseStatus"]
        )  # active, inactive
        self.destination = scenario.get("destination", DEFAULT_STATE_COPY["destination"])
        self.frontLeftTirePressure = scenario.get(
            "frontLeftTirePressure", DEFAULT_STATE_COPY["frontLeftTirePressure"]
        )
        self.frontRightTirePressure = scenario.get(
            "frontRightTirePressure", DEFAULT_STATE_COPY["frontRightTirePressure"]
        )
        self.rearLeftTirePressure = scenario.get(
            "rearLeftTirePressure", DEFAULT_STATE_COPY["rearLeftTirePressure"]
        )
        self.rearRightTirePressure = scenario.get(
            "rearRightTirePressure", DEFAULT_STATE_COPY["rearRightTirePressure"]
        )

        self.long_context = long_context

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, VehicleControlAPI):
            return False

        for attr_name in vars(self):
            if attr_name.startswith("_"):
                continue
            model_attr = getattr(self, attr_name)
            ground_truth_attr = getattr(value, attr_name)

            if model_attr != ground_truth_attr:
                return False

        return True

    def get_env_state(self):
        return {
            "random_seed": self.random_seed,
            "fuelLevel": self.fuelLevel,
            "batteryVoltage": self.batteryVoltage,
            "engine_state": self.engine_state,
            "remainingUnlockedDoors": self.remainingUnlockedDoors,
            "doorStatus": self.doorStatus,
            "acTemperature": self.acTemperature,
            "fanSpeed": self.fanSpeed,
            "acMode": self.acMode,
            "humidityLevel": self.humidityLevel,
            "headLightStatus": self.headLightStatus,
            "parkingBrakeStatus": self.parkingBrakeStatus,
            "_parkingBrakeForce": self._parkingBrakeForce,
            "_slopeAngle": self._slopeAngle,
            "brakePedalStatus": self.brakePedalStatus,
            "brakePedalForce": self._brakePedalForce,
            "distanceToNextVehicle": self.distanceToNextVehicle,
            "cruiseStatus": self.cruiseStatus,
            "destination": self.destination,
            "frontLeftTirePressure": self.frontLeftTirePressure,
            "frontRightTirePressure": self.frontRightTirePressure,
            "rearLeftTirePressure": self.rearLeftTirePressure,
            "rearRightTirePressure": self.rearRightTirePressure
        }

    def startEngine(self, ignitionMode: str) -> Dict[str, Union[str, float]]:
        """
        Starts the engine of the vehicle.
        Args:
            ignitionMode (str): The ignition mode of the vehicle. [Enum]: ["START", "STOP"]
        Returns:
            engineState (str): The state of the engine. [Enum]: ["running", "stopped"]
            fuelLevel (float): The fuel level of the vehicle in gallons.
            batteryVoltage (float): The battery voltage of the vehicle in volts.
        """
        if ignitionMode == "STOP":
            self.engine_state = "stopped"
            return {
                "engineState": self.engine_state,
                "fuelLevel": self.fuelLevel,
                "batteryVoltage": self.batteryVoltage,
            }
        
        if ignitionMode != "START":
            return {"error": "Invalid ignition mode."}

        if self.remainingUnlockedDoors > 0:
            return {
                "error": "All doors must be locked before starting the engine. Here are the unlocked doors: "
                + ", ".join(
                    [
                        door
                        for door, status in self.doorStatus.items()
                        if status == "unlocked"
                    ]
                )
            }
        if self.brakePedalStatus != "pressed":
            return {"error": "Brake pedal needs to be pressed when starting the engine."}
        if self._brakePedalForce != 1000.0:
            return {"error": "Must press the brake fully before starting the engine."}
        if self.fuelLevel < MIN_FUEL_LEVEL:
            return {"error": "Fuel tank is empty."}
            
        self.engine_state = "running"

        return {
            "engineState": self.engine_state,
            "fuelLevel": self.fuelLevel,
            "batteryVoltage": self.batteryVoltage,
        }

    def fillFuelTank(self, fuelAmount: float) -> Dict[str, Union[str, float]]:
        """
        Fills the fuel tank of the vehicle. The fuel tank can hold up to 50 gallons.
        Args:
            fuelAmount (float): The amount of fuel to fill in gallons; this is the additional fuel to add to the tank.
        Returns:
            fuelLevel (float): The fuel level of the vehicle in gallons.
        """
        if fuelAmount < 0:
            return {"error": "Fuel amount cannot be negative."}
        if self.fuelLevel + fuelAmount > MAX_FUEL_LEVEL:
            return {"error": "Cannot fill gas above the tank capacity."}
        if self.fuelLevel + fuelAmount < MIN_FUEL_LEVEL:
            return {"error": "Fuel tank is empty. Min fuel level is 0 gallons."}
        self.fuelLevel += fuelAmount
        return {"fuelLevel": self.fuelLevel}

    def lockDoors(self, unlock: bool, door: list[str]) -> Dict[str, Union[str, int]]:
        """
        Locks the doors of the vehicle.
        Args:
            unlock (bool): True if the doors are to be unlocked, False otherwise.
            door (List[str]): The list of doors to lock or unlock. [Enum]: ["driver", "passenger", "rear_left", "rear_right"]
        Returns:
            lockStatus (str): The status of the lock. [Enum]: ["locked", "unlocked"]
            remainingUnlockedDoors (int): The number of remaining unlocked doors.
        """
        if unlock:
            for d in door:
                if self.doorStatus[d] == "unlocked":
                    continue
                self.doorStatus[d] = "unlocked"
                self.remainingUnlockedDoors += 1
            return {
                "lockStatus": "unlocked",
                "remainingUnlockedDoors": self.remainingUnlockedDoors,
            }
        else:
            for d in door:
                if self.doorStatus[d] == "locked":
                    continue
                self.doorStatus[d] = "locked"
                self.remainingUnlockedDoors -= 1
            return {
                "lockStatus": "locked",
                "remainingUnlockedDoors": self.remainingUnlockedDoors,
            }

    def adjustClimateControl(
        self,
        temperature: float,
        unit: str = "celsius",
        fanSpeed: int = 50,
        mode: str = "auto",
    ) -> Dict[str, Union[str, float]]:
        """
        Adjusts the climate control of the vehicle.
        Args:
            temperature (float): The temperature to set in degree. Default to be celsius.
            unit (str): [Optional] The unit of temperature. [Enum]: ["celsius", "fahrenheit"]
            fanSpeed (int): [Optional] The fan speed to set from 0 to 100. Default is 50.
            mode (str): [Optional] The climate mode to set. [Enum]: ["auto", "cool", "heat", "defrost"]
        Returns:
            currentTemperature (float): The current temperature set in degree Celsius.
            climateMode (str): The current climate mode set.
            humidityLevel (float): The humidity level in percentage.
        """
        if not (0 <= fanSpeed <= 100):
            return {"error": "Fan speed must be between 0 and 100."}
        if unit not in ["celsius", "fahrenheit"]:
            return {"error": "Invalid unit."}
        self.acTemperature = temperature
        if unit == "fahrenheit":
            self.acTemperature = (temperature - 32) * 5 / 9
        self.fanSpeed = fanSpeed
        self.acMode = mode
        return {
            "currentACTemperature": self.acTemperature,
            "climateMode": mode,
            "humidityLevel": self.humidityLevel,
        }

    def get_outside_temperature_from_google(self) -> Dict[str, float]:
        """
        Gets the outside temperature.
        Returns:
            outsideTemperature (float): The outside temperature in degree Celsius.
        """
        if self.long_context:
            LONG_WEATHER_EXTENSION["outsideTemperature"] = self._random.uniform(-10.0, 40.0)
            return LONG_WEATHER_EXTENSION
        return {"outsideTemperature": self._random.uniform(-10.0, 40.0)}

    def get_outside_temperature_from_weather_com(self) -> Dict[str, float]:
        """
        Gets the outside temperature.
        Returns:
            outsideTemperature (float): The outside temperature in degree Celsius.
        """
        if self.long_context:
            LONG_WEATHER_EXTENSION["outsideTemperature"] = self._random.uniform(-10.0, 40.0)
            return LONG_WEATHER_EXTENSION
        return {"outsideTemperature": self._random.uniform(-10.0, 40.0)}

    def setHeadlights(self, mode: str) -> Dict[str, str]:
        """
        Sets the headlights of the vehicle.
        Args:
            mode (str): The mode of the headlights. [Enum]: ["on", "off", "auto"]
        Returns:
            headlightStatus (str): The status of the headlights. [Enum]: ["on", "off"]
        """
        if mode not in ["on", "off", "auto"]:
            return {"error": "Invalid headlight mode."}
        if mode == "on":
            self.headLightStatus = "on"
            return {"headlightStatus": "on"}
        else:
            self.headLightStatus = "off"
            return {"headlightStatus": "off"}

    def displayCarStatus(self, option: str) -> Dict[str, Union[str, float, Dict[str, str]]]:
        """
        Displays the status of the vehicle based on the provided display option.
        Args:
            option (str): The option to display. [Enum]: ["fuel", "battery", "doors", "climate", "headlights", "parkingBrake", "brakePedal", "engine"]
        Returns:
            status (Dict): The status of the vehicle based on the option.
                - fuelLevel (float): [Optional] The fuel level of the vehicle in gallons.
                - batteryVoltage (float): [Optional] The battery voltage of the vehicle in volts.
                - doorStatus (Dict): [Optional] The status of the doors.
                    - driver (str): The status of the driver door. [Enum]: ["locked", "unlocked"]
                    - passenger (str): The status of the passenger door. [Enum]: ["locked", "unlocked"]
                    - rear_left (str): The status of the rear left door. [Enum]: ["locked", "unlocked"]
                    - rear_right (str): The status of the rear right door. [Enum]: ["locked", "unlocked"]
                - currentACTemperature (float): [Optional] The current temperature set in degree Celsius.
                - fanSpeed (int): [Optional] The fan speed set from 0 to 100.
                - climateMode (str): [Optional] The climate mode set. [Enum]: ["auto", "cool", "heat", "defrost"]
                - humidityLevel (float): [Optional] The humidity level in percentage.
                - headlightStatus (str): [Optional] The status of the headlights. [Enum]: ["on", "off"]
                - parkingBrakeStatus (str): [Optional] The status of the brake. [Enum]: ["engaged", "released"]
                - parkingBrakeForce (float): [Optional] The force applied to the brake in Newtons.
                - slopeAngle (float): [Optional] The slope angle in degrees.
                - brakePedalStatus (str): [Optional] The status of the brake pedal. [Enum]: ["pressed", "released"]
                - brakePedalForce (float): [Optional] The force applied to the brake pedal in Newtons.
                - engineState (str): [Optional] The state of the engine. [Enum]: ["running", "stopped"]
                - metadata (str): [Optional] The metadata of the car.
        """
        status = {}
        if self.long_context:
            status["metadata"] = CAR_STATUS_METADATA_EXTENSION
        if option == "fuel":
            status["fuelLevel"] = self.fuelLevel
        elif option == "battery":
            status["batteryVoltage"] = self.batteryVoltage
        elif option == "doors":
            status["doorStatus"] = self.doorStatus
        elif option == "climate":
            status["currentACTemperature"] = self.acTemperature
            status["fanSpeed"] = self.fanSpeed
            status["climateMode"] = self.acMode
            status["humidityLevel"] = self.humidityLevel
        elif option == "headlights":
            status["headlightStatus"] = self.headLightStatus
        elif option == "parkingBrake":
            status["parkingBrakeStatus"] = self.parkingBrakeStatus
            status["parkingBrakeForce"] = self._parkingBrakeForce
            status["slopeAngle"] = self._slopeAngle
        elif option == "brakePedal":
            status["brakePedalStatus"] = self.brakePedalStatus
            status["brakePedalForce"] = self._brakePedalForce
        elif option == "engine":
            status["engineState"] = self.engine_state
        else:
            status["error"] = "Invalid option"
        return status

    def activateParkingBrake(self, mode: str) -> Dict[str, Union[str, float]]:
        """
        Activates the parking brake of the vehicle.
        Args:
            mode (str): The mode to set. [Enum]: ["engage", "release"]
        Returns:
            parkingBrakeStatus (str): The status of the brake. [Enum]: ["engaged", "released"]
            _parkingBrakeForce (float): The force applied to the brake in Newtons.
            _slopeAngle (float): The slope angle in degrees.
        """
        if mode not in ["engage", "release"]:
            return {"error": "Invalid mode"}
        if mode == "engage":
            self.parkingBrakeStatus = "engaged"
            self._parkingBrakeForce = 500.0
            self._slopeAngle = 10.0
            if self.long_context:
                return {
                    "parkingBrakeInstruction": PARKING_BRAKE_INSTRUCTION,
                    "parkingBrakeStatus": "engaged",
                    "_parkingBrakeForce": 500.0,
                    "_slopeAngle": 10.0,
                }
            return {"parkingBrakeStatus": "engaged", "_parkingBrakeForce": 500.0, "_slopeAngle": 10.0}
        else:
            self.parkingBrakeStatus = "released"
            self._parkingBrakeForce = 0.0
            self._slopeAngle = 10.0
            if self.long_context:
                return {
                    "parkingBrakeInstruction": PARKING_BRAKE_INSTRUCTION,
                    "parkingBrakeStatus": "released",
                    "_parkingBrakeForce": 0.0,
                    "_slopeAngle": 10.0,
                }
            return {"parkingBrakeStatus": "released", "_parkingBrakeForce": 0.0, "_slopeAngle": 10.0}

    def pressBrakePedal(self, pedalPosition: float) -> Dict[str, Union[str, float]]:
        """
        Presses the brake pedal based on pedal position. The brake pedal will be kept pressed until released.

        Args:
            pedalPosition (float): Position of the brake pedal, between 0 (not pressed) and 1 (fully pressed).
        Returns:
            brakePedalStatus (str): The status of the brake pedal. [Enum]: ["pressed", "released"]
            brakePedalForce (float): The force applied to the brake pedal in Newtons.
        """
        # Validate pedal position is within 0 to 1
        if not (0 <= pedalPosition <= 1):
            return {"error": "Pedal position must be between 0 and 1."}

        # Release the brake if pedal position is zero
        if pedalPosition == 0:
            self.brakePedalStatus = "released"
            self._brakePedalForce = 0.0
            return {"brakePedalStatus": "released", "brakePedalForce": 0.0}

        # Calculate force based on pedal position
        max_brake_force = 1000  # Max force in Newtons
        force = pedalPosition * max_brake_force

        # Update the brake pedal status and force
        self.brakePedalStatus = "pressed"
        self._brakePedalForce = force
        return {"brakePedalStatus": "pressed", "brakePedalForce": float(force)}

    def releaseBrakePedal(self) -> Dict[str, Union[str, float]]:
        """
        Releases the brake pedal of the vehicle.
        Returns:
            brakePedalStatus (str): The status of the brake pedal. [Enum]: ["pressed", "released"]
            brakePedalForce (float): The force applied to the brake pedal in Newtons.
        """
        self.brakePedalStatus = "released"
        self._brakePedalForce = 0.0
        return {"brakePedalStatus": "released", "brakePedalForce": 0.0}

    def setCruiseControl(
        self, speed: float, activate: bool, distanceToNextVehicle: float
    ) -> Dict[str, Union[str, float]]:
        """
        Sets the cruise control of the vehicle.
        Args:
            speed (float): The speed to set in m/h. The speed should be between 0 and 120 and a multiple of 5.
            activate (bool): True to activate the cruise control, False to deactivate.
            distanceToNextVehicle (float): The distance to the next vehicle in meters.
        Returns:
            cruiseStatus (str): The status of the cruise control. [Enum]: ["active", "inactive"]
            currentSpeed (float): The current speed of the vehicle in km/h.
            distanceToNextVehicle (float): The distance to the next vehicle in meters.
        """
        distanceToNextVehicle = float(distanceToNextVehicle)
        speed = float(speed)

        if activate and self.engine_state == "stopped":
            return {"error": "Start the engine before activating the cruise control."}
            
        if activate:
            self.distanceToNextVehicle = distanceToNextVehicle
            if speed < 0 or speed > 120 or speed % 5 != 0:
                return {"error": "Invalid speed"}
            self.cruiseStatus = "active"
            return {
                "cruiseStatus": "active",
                "currentSpeed": speed,
                "distanceToNextVehicle": distanceToNextVehicle,
            }
        else:
            self.cruiseStatus = "inactive"
            self.distanceToNextVehicle = distanceToNextVehicle
            return {
                "cruiseStatus": "inactive",
                "currentSpeed": speed,
                "distanceToNextVehicle": distanceToNextVehicle,
            }

    def get_current_speed(self) -> Dict[str, float]:
        """
        Gets the current speed of the vehicle.
        Returns:
            currentSpeed (float): The current speed of the vehicle in km/h.
        """
        return {"currentSpeed": self._random.uniform(0.0, 120.0)}

    def display_log(self, messages: List[str]):
        """
        Displays the log messages.
        Args:
            messages (List[str]): The list of messages to display.
        Returns:
            log (List[str]): The list of messages displayed.
        """
        return {"log": messages}

    def estimate_drive_feasibility_by_mileage(self, distance: float) -> Dict[str, bool]:
        """
        Estimates the milage of the vehicle given the distance needed to drive.
        Args:
            distance (float): The distance to travel in miles.
        Returns:
            canDrive (bool): True if the vehicle can drive the distance, False otherwise.
        """
        if self.fuelLevel * MILE_PER_GALLON < distance:
            return {"canDrive": False}
        else:
            return {"canDrive": True}

    def liter_to_gallon(self, liter: float) -> Dict[str, float]:
        """
        Converts the liter to gallon.
        Args:
            liter (float): The amount of liter to convert.
        Returns:
            gallon (float): The amount of gallon converted.
        """
        return {"gallon": liter * 0.264172}

    def gallon_to_liter(self, gallon: float) -> Dict[str, float]:
        """
        Converts the gallon to liter.
        Args:
            gallon (float): The amount of gallon to convert.
        Returns:
            liter (float): The amount of liter converted.
        """
        return {"liter": gallon * 3.78541}

    def estimate_distance(self, cityA: str, cityB: str) -> Dict[str, float]:
        """
        Estimates the distance between two cities.
        Args:
            cityA (str): The zipcode of the first city.
            cityB (str): The zipcode of the second city.
        Returns:
            distance (float): The distance between the two cities in km.
            intermediaryCities (List[str]): [Optional] The list of intermediary cities between the two cities.
        """
        if (cityA == "83214" and cityB == "74532") or (
            cityA == "74532" and cityB == "83214"
        ):
            distance = {"distance": 750.0}
        elif (cityA == "56108" and cityB == "62947") or (
            cityA == "62947" and cityB == "56108"
        ):
            distance = {"distance": 320.0}
        elif (cityA == "71354" and cityB == "83462") or (
            cityA == "83462" and cityB == "71354"
        ):
            distance = {"distance": 450.0}
        elif (cityA == "47329" and cityB == "52013") or (
            cityA == "52013" and cityB == "47329"
        ):
            distance = {"distance": 290.0}
        elif (cityA == "69238" and cityB == "51479") or (
            cityA == "51479" and cityB == "69238"
        ):
            distance = {"distance": 630.0}
        elif (cityA == "94016" and cityB == "83214") or (
            cityA == "83214" and cityB == "94016"
        ):
            distance = {"distance": 980.0}
        elif (cityA == "94016" and cityB == "94704") or (
            cityA == "94704" and cityB == "94016"
        ):
            distance = {"distance": 600.0}
        elif (cityA == "94704" and cityB == "08540") or (
            cityA == "08540" and cityB == "94704"
        ):
            distance = {"distance": 2550.0}
        elif (cityA == "94016" and cityB == "08540") or (
            cityA == "08540" and cityB == "94016"
        ):
            distance = {"distance": 1950.0}
        elif (cityA == "62947" and cityB == "47329") or (
            cityA == "47329" and cityB == "62947"
        ):
            distance = {"distance": 1053.0}
        elif (cityA == "94016" and cityB == "62947") or (
            cityA == "62947" and cityB == "94016"
        ):
            distance = {"distance": 780.0}
        elif (cityA == "74532" and cityB == "94016") or (
            cityA == "94016" and cityB == "74532"
        ):
            distance = {"distance": 880.0}
        else:
            distance = {"error": "distance not found in database."}

        if self.long_context:
            distance["intermediaryCities"] = INTERMEDIARY_CITIES
        return distance

    def get_zipcode_based_on_city(self, city: str) -> Dict[str, str]:
        """
        Gets the zipcode based on the city.
        Args:
            city (str): The name of the city.
        Returns:
            zipcode (str): The zipcode of the city.
        """
        if city == "Rivermist":
            return {"zipcode": "83214"}
        elif city == "Stonebrook":
            return {"zipcode": "74532"}
        elif city == "Maplecrest":
            return {"zipcode": "56108"}
        elif city == "Silverpine":
            return {"zipcode": "62947"}
        elif city == "Shadowridge":
            return {"zipcode": "71354"}
        elif city == "Sunset Valley":
            return {"zipcode": "83462"}
        elif city == "Oakendale":
            return {"zipcode": "47329"}
        elif city == "Willowbend":
            return {"zipcode": "52013"}
        elif city == "Crescent Hollow":
            return {"zipcode": "69238"}
        elif city == "Autumnville":
            return {"zipcode": "51479"}
        elif city == "San Francisco":
            return {"zipcode": "94016"}
        else:
            return {"zipcode": "00000"}

    def set_navigation(self, destination: str) -> Dict[str, str]:
        """
        Navigates to the destination.
        Args:
            destination (str): The destination to navigate in the format of street, city, state.
        Returns:
            status (str): The status of the navigation.
        """
        self.destination = destination
        return {"status": "Navigating to " + destination}

    def check_tire_pressure(self):
        """
        Checks the tire pressure of the vehicle.
        Returns:
            tirePressure (Dict): The tire pressure of the vehicle.
                - frontLeftTirePressure (float): The pressure of the front left tire in psi.
                - frontRightTirePressure (float): The pressure of the front right tire in psi.
                - rearLeftTirePressure (float): The pressure of the rear left tire in psi.
                - rearRightTirePressure (float): The pressure of the rear right tire in psi.
                - healthy_tire_pressure (bool): True if the tire pressure is healthy, False otherwise.
                - car_info (Dict): The metadata of the car.
        """
        # This is the healthy standard the vehicle use, though the user might have different preferences
        healthy_tire_pressure = (
            30 <= (
                self.frontLeftTirePressure
                + self.frontRightTirePressure
                + self.rearLeftTirePressure
                + self.rearRightTirePressure
            ) / 4 <= 35
        )

        tire_status = {
            "frontLeftTirePressure": self.frontLeftTirePressure,
            "frontRightTirePressure": self.frontRightTirePressure,
            "rearLeftTirePressure": self.rearLeftTirePressure,
            "rearRightTirePressure": self.rearRightTirePressure,
            "healthy_tire_pressure": healthy_tire_pressure,
            "car_info": {},
        }

        if self.long_context:
            tire_status["car_info"] = CAR_STATUS_METADATA_EXTENSION
        return tire_status

    def find_nearest_tire_shop(self) -> Dict[str, str]:
        """
        Finds the nearest tire shop.
        Returns:
            shopLocation (str): The location of the nearest tire shop.
        """
        return {"shopLocation": "456 Oakwood Avenue, Rivermist, 83214"}

__TEST_CASES__ = [
    {
        'name': 'Engine and Fuel Workflow (Normal & State-change)',
        'steps': [
            {'expect_success': True, 'tool_call': "env['vehicle_control'].fillFuelTank(fuelAmount=10.5)"},
            {'expect_success': True, 'tool_call': "env['vehicle_control'].displayCarStatus(option='fuel')"},
            {'expect_success': True, 'tool_call': "env['vehicle_control'].lockDoors(unlock=False, door=['driver', 'passenger', 'rear_left', 'rear_right'])"},
            {'expect_success': True, 'tool_call': "env['vehicle_control'].pressBrakePedal(pedalPosition=1.0)"},
            {'expect_success': True, 'tool_call': "env['vehicle_control'].startEngine(ignitionMode='START')"},
            {'expect_success': True, 'tool_call': "env['vehicle_control'].displayCarStatus(option='engine')"},
            {'expect_success': True, 'tool_call': "env['vehicle_control'].startEngine(ignitionMode='STOP')"}
        ]
    },
    {
        'name': 'Doors and Headlights (Normal & State-change)',
        'steps': [
            {'expect_success': True, 'tool_call': "env['vehicle_control'].lockDoors(unlock=False, door=['driver', 'passenger'])"},
            {'expect_success': True, 'tool_call': "env['vehicle_control'].displayCarStatus(option='doors')"},
            {'expect_success': True, 'tool_call': "env['vehicle_control'].setHeadlights(mode='on')"},
            {'expect_success': True, 'tool_call': "env['vehicle_control'].displayCarStatus(option='headlights')"}
        ]
    },
    {
        'name': 'Climate Control (Normal & Boundary values)',
        'steps': [
            {'expect_success': True, 'tool_call': "env['vehicle_control'].adjustClimateControl(temperature=22.0, unit='celsius', fanSpeed=0, mode='cool')"},
            {'expect_success': True, 'tool_call': "env['vehicle_control'].adjustClimateControl(temperature=100.0, unit='fahrenheit', fanSpeed=100, mode='heat')"},
            {'expect_success': True, 'tool_call': "env['vehicle_control'].displayCarStatus(option='climate')"}
        ]
    },
    {
        'name': 'Brake System Workflow (Cross-method)',
        'steps': [
            {'expect_success': True, 'tool_call': "env['vehicle_control'].pressBrakePedal(pedalPosition=0.5)"},
            {'expect_success': True, 'tool_call': "env['vehicle_control'].displayCarStatus(option='brakePedal')"},
            {'expect_success': True, 'tool_call': "env['vehicle_control'].activateParkingBrake(mode='engage')"},
            {'expect_success': True, 'tool_call': "env['vehicle_control'].displayCarStatus(option='parkingBrake')"},
            {'expect_success': True, 'tool_call': "env['vehicle_control'].releaseBrakePedal()"},
            {'expect_success': True, 'tool_call': "env['vehicle_control'].activateParkingBrake(mode='release')"}
        ]
    },
    {
        'name': 'Cruise Control and Speed (Normal & Boundary)',
        'steps': [
            {'expect_success': True, 'tool_call': "env['vehicle_control'].lockDoors(unlock=False, door=['driver', 'passenger', 'rear_left', 'rear_right'])"},
            {'expect_success': True, 'tool_call': "env['vehicle_control'].pressBrakePedal(pedalPosition=1.0)"},
            {'expect_success': True, 'tool_call': "env['vehicle_control'].startEngine(ignitionMode='START')"},
            {'expect_success': True, 'tool_call': "env['vehicle_control'].setCruiseControl(speed=60.0, activate=True, distanceToNextVehicle=100.0)"},
            {'expect_success': True, 'tool_call': "env['vehicle_control'].get_current_speed()"},
            {'expect_success': True, 'tool_call': "env['vehicle_control'].setCruiseControl(speed=0.0, activate=False, distanceToNextVehicle=0.0)"}
        ]
    },
    {
        'name': 'Navigation and Distance Estimation (Cross-method)',
        'steps': [
            {'expect_success': True, 'tool_call': "env['vehicle_control'].get_zipcode_based_on_city(city='San Francisco')"},
            {'expect_success': True, 'tool_call': "env['vehicle_control'].get_zipcode_based_on_city(city='Rivermist')"},
            {'expect_success': True, 'tool_call': "env['vehicle_control'].estimate_distance(cityA='94016', cityB='83214')"},
            {'expect_success': True, 'tool_call': "env['vehicle_control'].estimate_drive_feasibility_by_mileage(distance=380.0)"},
            {'expect_success': True, 'tool_call': "env['vehicle_control'].set_navigation(destination='123 Main St, San Francisco, CA')"}
        ]
    },
    {
        'name': 'Tires and Weather (Normal)',
        'steps': [
            {'expect_success': True, 'tool_call': "env['vehicle_control'].check_tire_pressure()"},
            {'expect_success': True, 'tool_call': "env['vehicle_control'].find_nearest_tire_shop()"},
            {'expect_success': True, 'tool_call': "env['vehicle_control'].get_outside_temperature_from_google()"},
            {'expect_success': True, 'tool_call': "env['vehicle_control'].get_outside_temperature_from_weather_com()"}
        ]
    },
    {
        'name': 'Utilities and Logs (Normal & Boundary)',
        'steps': [
            {'expect_success': True, 'tool_call': "env['vehicle_control'].liter_to_gallon(liter=100.0)"},
            {'expect_success': True, 'tool_call': "env['vehicle_control'].gallon_to_liter(gallon=26.4172)"},
            {'expect_success': True, 'tool_call': "env['vehicle_control'].display_log(messages=['Test message 1', 'Test message 2'])"},
            {'expect_success': True, 'tool_call': "env['vehicle_control'].display_log(messages=[])"},
            {'expect_success': True, 'tool_call': "env['vehicle_control'].get_env_state()"}
        ]
    },
    {
        'name': 'Error Paths - Invalid Parameters (Error)',
        'steps': [
            {'expect_success': False, 'tool_call': "env['vehicle_control'].startEngine(ignitionMode='FLY')"},
            {'expect_success': False, 'tool_call': "env['vehicle_control'].fillFuelTank(fuelAmount=-10.0)"},
            {'expect_success': False, 'tool_call': "env['vehicle_control'].adjustClimateControl(temperature=20.0, unit='kelvin', fanSpeed=50, mode='auto')"},
            {'expect_success': False, 'tool_call': "env['vehicle_control'].setHeadlights(mode='blinking')"},
            {'expect_success': False, 'tool_call': "env['vehicle_control'].displayCarStatus(option='wings')"}
        ]
    },
    {
        'name': 'Error Paths - Missing Required Fields & Wrong Types (Error)',
        'steps': [
            {'expect_success': False, 'tool_call': "env['vehicle_control'].lockDoors(unlock=True)"},
            {'expect_success': False, 'tool_call': "env['vehicle_control'].pressBrakePedal(pedalPosition=1.5)"},
            {'expect_success': False, 'tool_call': "env['vehicle_control'].setCruiseControl(speed=62.0, activate=True, distanceToNextVehicle=50.0)"},
            {'expect_success': False, 'tool_call': "env['vehicle_control'].estimate_distance(cityA='90001')"}
        ]
    }
]