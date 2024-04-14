import mysql.connector
import serial
import time
import re
from datetime import datetime

# variables for database connection
db_host = "localhost"
db_user = "pi"
db_password = "102767763"
db_name = "energy_management_system"

def checkLatestTimestamp(device_type, device_name, table_name, duration):
    try:
        # Open connection to the database
        mydb = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
        cursor = mydb.cursor()

        # Query to get the timestamp of the latest entry
        cursor.execute("SELECT MAX(timestamp) FROM {} WHERE {} = %s".format(table_name, device_type), (device_name,))
        latest_timestamp = cursor.fetchone()[0]

        if latest_timestamp:
            # Calculate the difference between the current time and the latest timestamp
            current_time = datetime.now()
            time_difference = current_time - latest_timestamp

            # Check if the time difference is greater than duration set
            if time_difference.total_seconds() >= duration:
                return True
            
            else:
                # Close the connection
                cursor.close()
                mydb.close()
                return False
        
        else:
            # if database is empty
            return True
            
        # Close the connection
        cursor.close()
        mydb.close()
    except Exception as e:
        print("a")
        print("Error:", e)
    
    return False

def lastMotionDetected():
    try:
        # Open connection to the database
        mydb = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
        cursor = mydb.cursor()

        # Query to get the timestamp of the latest PIR sensor entry with value 1.0
        cursor.execute("SELECT MAX(timestamp) FROM sensor_log WHERE sensor_type = 'PIR' AND value = 1.0")
        latest_motion_timestamp = cursor.fetchone()[0]

        # Query to get the timestamp of the latest PIR sensor entry with value 0.0
        cursor.execute("SELECT MAX(timestamp) FROM sensor_log WHERE sensor_type = 'PIR' AND value = 0.0")
        latest_no_motion_timestamp = cursor.fetchone()[0]

        if latest_motion_timestamp and latest_no_motion_timestamp:
            # Calculate the difference between the timestamps
            motion_time_difference = latest_motion_timestamp - latest_no_motion_timestamp
            # Convert the time difference to seconds
            time_difference_seconds = motion_time_difference.total_seconds()

            time_diffrence_minutes = time_difference_seconds / 60
            
            return time_diffrence_minutes
            
    except Exception as e:
        print("Error:", e)
    
    finally:
        # Close the connection
        cursor.close()
        mydb.close()
        
    return None

def readFromParamDatabase(device_name):
    try:
        # Open connection to the database
        mydb = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
        cursor = mydb.cursor()

        # Define the query to select the param_value based on the param_name (device_name)
        sql = "SELECT param_value FROM param_table WHERE param_name = %s"
        val = (device_name,)
        cursor.execute(sql, val)

        # Fetch the result
        result = cursor.fetchone()

        # Close the cursor and database connection
        cursor.close()
        mydb.close()

        if result:
            return result[0]  # Return the param_value
        else:
            return None  # Return None if no result found
    except Exception as e:
        print("b")
        print("Error:", e)
        return None

def logDataToActuatorDatabase(device_name, status):
    try:
        # Open connection to the database
        mydb = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
        cursor = mydb.cursor()
        
        # Insert data into the actuator table
        current_time = datetime.now()
        sql = "INSERT INTO {} (actuator_type, status, timestamp) VALUES (%s, %s, %s)".format("actuator_log")
        val = (device_name, status, current_time)
        cursor.execute(sql, val)
        
        # Commit the transaction
        mydb.commit()
        
        # Close the connection
        cursor.close()
        mydb.close()
    except Exception as e:
        print("c")
        print("Error:", e)
        
def logDataToSensorDatabase(device_name, status):
    try:
        # Open connection to the database
        mydb = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
        cursor = mydb.cursor()
        
        # Insert data into the actuator table
        current_time = datetime.now()
        sql = "INSERT INTO {} (sensor_type, value, timestamp) VALUES (%s, %s, %s)".format("sensor_log")
        val = (device_name, status, current_time)
        cursor.execute(sql, val)
        
        # Commit the transaction
        mydb.commit()
        
        # Close the connection
        cursor.close()
        mydb.close()
    except Exception as e:
        print("d")
        print("Error:", e)
        
def updateParamValue(paramName, paramValue):
    try:
        # Open connection to the database
        mydb = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
        cursor = mydb.cursor()

        sql = "UPDATE param_table SET param_value = %s WHERE param_name = %s"
        val = (paramValue, paramName)  
        cursor.execute(sql, val)

        # Commit the transaction
        mydb.commit()

        # Close the cursor and database connection
        cursor.close()
        mydb.close()

        return True
    except Exception as e:
        print("e")
        print("Error:", e)
        return False

def tempSensor(data):
    # Use regular expressions to extract numeric values from the data
    humidity_match = re.search(r'Current humidity = (\d+\.\d+)', data)
    temperature_match = re.search(r'temperature = (\d+\.\d+)', data)
    
    # If both humidity and temperature values are found, print them
    if humidity_match and temperature_match:
        humidity = float(humidity_match.group(1))
        temperature = float(temperature_match.group(1))
        
        updateParamValue("tempSensor", temperature)
        
        #print("Humidity:", humidity)
        #print("Temperature:", temperature)
        if (checkLatestTimestamp("sensor_type", "temp_sensor", "sensor_log", 60)):
            logDataToSensorDatabase("temp_sensor", temperature)
        else:
            return
        
def lightSensor(data):
    # use regex to extract light sensor value
    light_match = re.search(r'Light sensor = (\d+)', data)
    
    if light_match:
        light = float(light_match.group(1))
        
        updateParamValue("lightSensor", light)
        
        #print("Light: ", light)
        if (checkLatestTimestamp("sensor_type", "light_sensor", "sensor_log", 10)):
            logDataToSensorDatabase("light_sensor", light)
        else:
            return
        
def motionSensor(data):
    # use regex to extract motion sensor value
    motion_match = re.search(r'Motion sensor = (\d+)', data)
    
    if motion_match:
        motion = float(motion_match.group(1))
        
        updateParamValue("PIR", motion)
        
        #print("Motion: ", motion)
        if (checkLatestTimestamp("sensor_type", "PIR", "sensor_log", 5)):
            logDataToSensorDatabase("PIR", motion)
        else:
            return 
        
def lcd(data):
    # use regex to extract lcd status
    lcd_match = re.search(r'LCD Display = (On|Off)', data)
    
    if lcd_match:
        lcd = lcd_match.group(1)

        #print("LCD: ", lcd)
        if (checkLatestTimestamp("actuator_type", "LCD", "actuator_log", 60)):
            logDataToActuatorDatabase("LCD", lcd)
        else:
            return 
        
def fan(data):
    # use regex to extract fan status
    fan_match = re.search(r'Fan = (On|Off)', data)
    
    if fan_match:
        fan = fan_match.group(1)
        
        #print("Fan: ", fan)
        if (checkLatestTimestamp("actuator_type", "fan", "actuator_log", 60)):
            logDataToActuatorDatabase("fan", fan)
        else:
            return
        
def redLED(data):
    # use regex to extract red LED status
    redLED_match = re.search(r'Red LED = (On|Off)', data)
    
    if redLED_match:
        redLED = redLED_match.group(1)
        
        #print("Red LED: ", redLED)
        if (checkLatestTimestamp("actuator_type", "redLED", "actuator_log", 10)):
            logDataToActuatorDatabase("redLED", redLED)
        else:
            return
        
def yellowLED(data):
    # use regex to extract yellow LED status
    yellowLED_match = re.search(r'Yellow LED = (On|Off)', data)
    
    if yellowLED_match:
        yellowLED = yellowLED_match.group(1)
        
        #print("Yellow LED: ", yellowLED)
        if (checkLatestTimestamp("actuator_type", "yellowLED", "actuator_log", 10)):
            logDataToActuatorDatabase("yellowLED", yellowLED)
        else:
            return
        
def greenLED(data):
    # use regex to extract green LED status
    greenLED_match = re.search(r'Green LED = (On|Off)', data)
    
    if greenLED_match:
        greenLED = greenLED_match.group(1)
        
        #print("Green LED: ", greenLED)
        if (checkLatestTimestamp("actuator_type", "greenLED", "actuator_log", 10)):
            logDataToActuatorDatabase("greenLED", greenLED)
        else:
            return
        
if __name__ == "__main__":
    ser = serial.Serial('/dev/ttyUSB0', 9600, timeout = 1)
    time.sleep(3) # to give time for the Arduino to setup
    
    while True:
        # read database (param database)
        temp = readFromParamDatabase("tempSensor")
        light = readFromParamDatabase("lightSensor")
        motion = readFromParamDatabase("PIR")

        redLEDState = readFromParamDatabase("redLED")
        yellowLEDState = readFromParamDatabase("yellowLED")
        greenLEDState = readFromParamDatabase("greenLED")
        fanState = readFromParamDatabase("fan")
        lcdState = readFromParamDatabase("LCD")

        onTimeLED = readFromParamDatabase("onTimeLED")
        offTimeLED = readFromParamDatabase("offTimeLED")
        tempFanLow = readFromParamDatabase("tempFanLow")
        tempFanHigh = readFromParamDatabase("tempFanHigh")
        motionAppliances = readFromParamDatabase("motionAppliances")
        adaptiveControl = readFromParamDatabase("adaptiveControl")

        if (adaptiveControl == "Off"):
            if (redLEDState == "On"):
                message = "Red LED On\n"
                ser.write(message.encode('utf-8'))
            if (redLEDState == "Off"):
                message = "Red LED Off\n"
                ser.write(message.encode('utf-8'))
            if (yellowLEDState == "On"):
                message = "Yellow LED On\n"
                ser.write(message.encode('utf-8'))
            if (yellowLEDState == "Off"):
                message = "Yellow LED Off\n"
                ser.write(message.encode('utf-8'))
            if (greenLEDState == "On"):
                message = "Green LED On\n"
                ser.write(message.encode('utf-8'))
            if (greenLEDState == "Off"):
                message = "Green LED Off\n"
                ser.write(message.encode('utf-8'))
            if (lcdState == "On"):
                message = "LCD On\n"
                ser.write(message.encode('utf-8'))
            if (lcdState == "Off"):
                message = "LCD Off\n"
                ser.write(message.encode('utf-8'))
            if (fanState == "Off"):
                message = "Fan Off\n"
                ser.write(message.encode('utf-8'))
            if (fanState == "1"):
                message = "Fan 1\n"
                ser.write(message.encode('utf-8'))
            if (fanState == "2"):
                message = "Fan 2\n"
                ser.write(message.encode('utf-8'))
            if (fanState == "3"):
                message = "Fan 3\n"
                ser.write(message.encode('utf-8'))
        elif (adaptiveControl == "On"): # follow logic of adaptive controls in database
            try:
                # LEDs
                if (onTimeLED == "0000" and offTimeLED == "0000"):
                    if (float(light) < 100):
                        message = "Red LED On\n"
                        ser.write(message.encode('utf-8'))
                        message = "Yellow LED On\n"
                        ser.write(message.encode('utf-8'))
                        message = "Green LED On\n"
                        ser.write(message.encode('utf-8'))
                    else:
                        message = "Red LED Off\n"
                        ser.write(message.encode('utf-8'))
                        message = "Yellow LED Off\n"
                        ser.write(message.encode('utf-8'))
                        message = "Green LED Off\n"
                        ser.write(message.encode('utf-8'))
                else:
                    try:
                        # Get the current time
                        current_time = datetime.now().time()

                        # Convert onTimeLED and offTimeLED to datetime objects for comparison
                        on_time = datetime.strptime(onTimeLED, "%H%M").time()
                        off_time = datetime.strptime(offTimeLED, "%H%M").time()

                        if on_time <= current_time <= off_time:
                            message = "Red LED On\n"
                            ser.write(message.encode('utf-8'))
                            message = "Yellow LED On\n"
                            ser.write(message.encode('utf-8'))
                            message = "Green LED On\n"
                            ser.write(message.encode('utf-8'))
                        else:
                            message = "Red LED Off\n"
                            ser.write(message.encode('utf-8'))
                            message = "Yellow LED Off\n"
                            ser.write(message.encode('utf-8'))
                            message = "Green LED Off\n"
                            ser.write(message.encode('utf-8'))
                    except:
                        pass

                # fan
                try:
                    if (int(temp) < (int(tempFanLow) - 5)):
                        message = "Fan Off\n"
                        ser.write(message.encode('utf-8'))
                    elif (int(temp) < int(tempFanLow)):
                        message = "Fan 1\n"
                        ser.write(message.encode('utf-8'))
                    elif (int(tempFanLow) < int(temp) < int(tempFanHigh)):
                        message = "Fan 2\n"
                        ser.write(message.encode('utf-8'))
                    elif (int(temp) > tempFanHigh):
                        message = "Fan 3\n"
                        ser.write(message.encode('utf-8'))
                
                except:
                    pass

                # motion
                try:
                    if (motionAppliances != "Off"):
                        latestMotionDuration = lastMotionDetected()

                        try:
                            if (int(motionAppliances) > latestMotionDuration):
                                message = "Red LED Off\n"
                                ser.write(message.encode('utf-8'))
                                message = "Yellow LED Off\n"
                                ser.write(message.encode('utf-8'))
                                message = "Green LED Off\n"
                                ser.write(message.encode('utf-8'))
                                message = "LCD Off\n"
                                ser.write(message.encode('utf-8'))
                                message = "Fan Off\n"
                                ser.write(message.encode('utf-8'))
                                while True: # continue the loop only when param database updates to 1.0
                                    motion = readFromParamDatabase("PIR")
                                    if motion == "1.0":
                                        break
                        except:
                            pass
                except:
                    pass

            except:
                pass

        
        # read from the Arduino, then update the database (all will update logs, sensors will update param table)
        if ser.in_waiting > 0:
            line = ser.readline().decode("utf-8")
            motionSensor(line)
            tempSensor(line)
            lightSensor(line)
            
            lcd(line)
            fan(line)
            redLED(line)
            yellowLED(line)
            greenLED(line)
    
    ser.flush()