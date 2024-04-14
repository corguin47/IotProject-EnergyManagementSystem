import mysql.connector
import serial
from flask import Flask, request, render_template, jsonify
from datetime import datetime, timedelta

# variables for database connection
db_host = "localhost"
db_user = "pi"
db_password = "102767763"
db_name = "energy_management_system"

ser = serial.Serial('/dev/ttyUSB0', 9600)
app = Flask(__name__)

def defaultDatabaseSetup():
    # open connection to the MariaDB MySQL server
    mydb = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)

    # seize control of the server's cursor to input SQL statements
    cursor = mydb.cursor()
    
    # Execute the query to delete all existing data from the param_table
    # cursor.execute("DELETE FROM param_table;")
    
    cursor.execute("SELECT COUNT(*) FROM param_table;")
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Execute the queries to insert values into the param_table
        cursor.execute("INSERT INTO param_table (param_name, param_value) VALUES (%s, %s);", ("LCD", "Off"))
        cursor.execute("INSERT INTO param_table (param_name, param_value) VALUES (%s, %s);", ("fan", "Off"))
        cursor.execute("INSERT INTO param_table (param_name, param_value) VALUES (%s, %s);", ("redLED", "Off"))
        cursor.execute("INSERT INTO param_table (param_name, param_value) VALUES (%s, %s);", ("yellowLED", "Off"))
        cursor.execute("INSERT INTO param_table (param_name, param_value) VALUES (%s, %s);", ("greenLED", "Off"))
        cursor.execute("INSERT INTO param_table (param_name, param_value) VALUES (%s, %s);", ("PIR", "0"))
        cursor.execute("INSERT INTO param_table (param_name, param_value) VALUES (%s, %s);", ("tempSensor", "0"))
        cursor.execute("INSERT INTO param_table (param_name, param_value) VALUES (%s, %s);", ("lightSensor", "0"))
        cursor.execute("INSERT INTO param_table (param_name, param_value) VALUES (%s, %s);", ("onTimeLED", "0800"))
        cursor.execute("INSERT INTO param_table (param_name, param_value) VALUES (%s, %s);", ("offTimeLED", "1700"))
        cursor.execute("INSERT INTO param_table (param_name, param_value) VALUES (%s, %s);", ("tempFanLow", "30"))
        cursor.execute("INSERT INTO param_table (param_name, param_value) VALUES (%s, %s);", ("tempFanHigh", "35"))
        cursor.execute("INSERT INTO param_table (param_name, param_value) VALUES (%s, %s);", ("motionAppliances", "On"))
        cursor.execute("INSERT INTO param_table (param_name, param_value) VALUES (%s, %s);", ("adaptiveControl", "On"))
        cursor.execute("INSERT INTO param_table (param_name, param_value) VALUES (%s, %s);", ("adaptiveControlMode", "Custom"))
        mydb.commit()

    # after one round of operations, release the cursor back to the server
    cursor.close()

    # terminate the server connection
    mydb.close()
    
def update_param_value(param_name, param_value):
    try:
        # Open connection to the database
        mydb = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
        cursor = mydb.cursor()

        # Define the query to update the param_value based on the param_name
        sql = "UPDATE param_table SET param_value = %s WHERE param_name = %s"
        val = (param_value, param_name)  # Use the provided param_name and param_value
        cursor.execute(sql, val)

        # Commit the transaction
        mydb.commit()

        # Close the cursor and database connection
        cursor.close()
        mydb.close()

        return True
    except Exception as e:
        print("Error:", e)
        return False

def query_state(name):
    try:
        # Open connection to the database
        mydb = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
        cursor = mydb.cursor()

        # Define the query to fetch state from param_table based on name
        cursor.execute("SELECT param_value FROM param_table WHERE param_name = %s", (name,))
        result = cursor.fetchone()

        if result:
            return result[0]  # Return the state
        else:
            return 'Unknown'  # If no result found, return 'Unknown'
    except Exception as e:
        print("Error:", e)
        return 'Unknown'

@app.route('/get_led_state/<color>')
def fetch_led_state(color):
    if (color == "red"):
        led_state = query_state("redLED")
    elif (color == "yellow"):
        led_state = query_state("yellowLED")
    elif (color == "green"):
        led_state = query_state("greenLED")
  
    return jsonify({'color': color, 'status': led_state})

@app.route('/get_lcd_state')
def fetch_lcd_state():
    lcd_state = query_state("LCD")

    return jsonify({'status': lcd_state})

@app.route('/get_fan_state')
def fetch_fan_state():
    fan_state = query_state("fan")
    
    return jsonify({'status': fan_state})

# Function to query param database for motion detection state
def query_motion_detection_state():
    try:
        # Open connection to the database
        mydb = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
        cursor = mydb.cursor()

        # Define the query to fetch motion detection state from param_table
        cursor.execute("SELECT param_value FROM param_table WHERE param_name = 'PIR'")
        result = cursor.fetchone()

        # If result is 1, motion is detected; otherwise, not detected
        motion_detected = True if result and result[0] == '1' else False

        # Close cursor and database connection
        cursor.close()
        mydb.close()

        return motion_detected
    except Exception as e:
        print("Error:", e)
        return None

# Function to query param database for temperature
def query_temperature():
    try:
        # Open connection to the database
        mydb = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
        cursor = mydb.cursor()

        # Define the query to fetch temperature from param_table
        cursor.execute("SELECT param_value FROM param_table WHERE param_name = 'tempSensor'")
        result = cursor.fetchone()

        # Close cursor and database connection
        cursor.close()
        mydb.close()

        return result[0] if result else None
    except Exception as e:
        print("Error:", e)
        return None

# Function to query param database for light
def query_light():
    try:
        # Open connection to the database
        mydb = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
        cursor = mydb.cursor()

        # Define the query to fetch light from param_table
        cursor.execute("SELECT param_value FROM param_table WHERE param_name = 'lightSensor'")
        result = cursor.fetchone()

        # Close cursor and database connection
        cursor.close()
        mydb.close()

        return result[0] if result else None
    except Exception as e:
        print("Error:", e)
        return None
    
def query_adaptive_control_settings():
    try:
        # Open connection to the database
        mydb = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
        cursor = mydb.cursor()

        # Define the query to fetch adaptive control settings from param_table
        cursor.execute("SELECT param_name, param_value FROM param_table WHERE param_name IN ('onTimeLED', 'offTimeLED', 'tempFanLow', 'tempFanHigh', 'motionAppliances', 'adaptiveControl', 'adaptiveControlMode')")
        results = cursor.fetchall()

        # Close cursor and database connection
        cursor.close()
        mydb.close()

        # Create a dictionary to store adaptive control settings
        adaptive_control_settings = {}
        for param_name, param_value in results:
            adaptive_control_settings[param_name] = param_value

        return adaptive_control_settings
    except Exception as e:
        print("Error:", e)
        return None

@app.route('/update_adaptiveControlData', methods=['POST'])
def update_param():
    # Get parameter name and value from the request
    param_name = request.json.get('paramName')
    param_value = request.json.get('paramValue')
    print(param_name)
    print(param_value)

    # Update parameter value in the database
    if param_name and param_value:
        if update_param_value(param_name, param_value):
            return jsonify({'success': True, 'message': 'Parameter updated successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to update parameter'})
    else:
        return jsonify({'success': False, 'message': 'Invalid parameter name or value'})

# Route to fetch motion detection state
@app.route('/get_motion_detection_state')
def get_motion_detection_state():
    motion_detected = query_motion_detection_state()
    return jsonify({'motion_detected': motion_detected})

# Route to fetch temperature
@app.route('/get_temperature')
def get_temperature():
    temperature = query_temperature()
    return jsonify({'temperature': temperature})

# Route to fetch light
@app.route('/get_light')
def get_light():
    light = query_light()
    return jsonify({'light': light})

@app.route('/get_adaptive_control')
def get_adaptive_control():
    # Fetch adaptive control settings from the database
    adaptive_control_settings = query_adaptive_control_settings()
    
    # Check if adaptive control settings were fetched successfully
    if adaptive_control_settings is not None:
        return jsonify(adaptive_control_settings)
    else:
        return jsonify({'error': 'Failed to fetch adaptive control settings'})

@app.route('/update_adaptive_control_status', methods=['POST'])
def update_adaptive_control():
    data = request.json
    new_status = data.get('status')
    if new_status is not None:
        # Assuming 'adaptive_control_status' is the parameter name in the param_table
        if update_param_value('adaptiveControl', new_status):
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status': 'failed', 'message': 'Failed to update adaptive control status'})
    else:
        return jsonify({'error': 'Invalid request'})


def fetch_logs_from_database(type, log_type):
    try:
        # Open connection to the database
        mydb = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
        cursor = mydb.cursor(dictionary=True)

        # Define the query based on type and log_type
        if type == 'actuator':
            query = "SELECT actuator_log_id as id, actuator_type as device_sensor, status, timestamp FROM actuator_log WHERE actuator_type = %s ORDER BY timestamp DESC"
        elif type == 'sensor':
            query = "SELECT sensor_log_id as id, sensor_type as device_sensor, timestamp, value FROM sensor_log WHERE sensor_type = %s ORDER BY timestamp DESC"
        
        # Execute the query
        cursor.execute(query, (log_type,))
        logs = cursor.fetchall()

        # Close the cursor and database connection
        cursor.close()
        mydb.close()

        return logs
    except Exception as e:
        print("Error:", e)
        return []

def fetch_all_logs_from_database():
    try:
        # Open connection to the database
        mydb = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
        cursor = mydb.cursor(dictionary=True)

        # Define the query to fetch all logs from both tables
        query = """
            SELECT 'actuator' AS log_type, actuator_log_id AS id, actuator_type AS device_sensor, status AS status, timestamp 
            FROM actuator_log 
            UNION ALL
            SELECT 'sensor' AS log_type, sensor_log_id AS id, sensor_type AS device_sensor, value AS status, timestamp 
            FROM sensor_log 
            ORDER BY timestamp DESC;
        """

        # Execute the query
        cursor.execute(query)
        logs = cursor.fetchall()

        # Close the cursor and database connection
        cursor.close()
        mydb.close()

        return logs
    except Exception as e:
        print("Error:", e)
        return []

# Flask route to serve the logs based on type and log_type
@app.route('/get_logs', methods=['GET'])
def get_logs():
    type = request.args.get('type')
    log_type = request.args.get('log_type')
    
    if type == 'all' and log_type == 'all':
        logs = fetch_all_logs_from_database()
    else:
        logs = fetch_logs_from_database(type, log_type)
        
    return jsonify(logs)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/logs')
def logs():
    return render_template('logs.html')

# Function to fetch the first log of a device from the previous day
def fetch_first_log(log_type, device, start_time, end_time):
    logs = fetch_logs_from_database(log_type, device)
    for log in logs:
        if start_time <= log['timestamp'] <= end_time and log['status'] == 'On':
            return log
    return None

# Function to fetch the last log of a device from the previous day
def fetch_last_log(log_type, device, start_time, end_time):
    logs = fetch_logs_from_database(log_type, device)
    for log in reversed(logs):
        if start_time <= log['timestamp'] <= end_time and log['status'] == 'Off':
            return log
    return None

# Function to fetch the highest temperature from the previous day
def fetch_highest_temperature(start_time, end_time):
    temperature_logs = fetch_logs_from_database('sensor', 'temp_sensor')
    highest_temperature = None
    for log in temperature_logs:
        if start_time <= log['timestamp'] <= end_time:
            temperature = log['value']
            if highest_temperature is None or temperature > highest_temperature:
                highest_temperature = temperature
    return highest_temperature

# Function to fetch the lowest temperature from the previous day
def fetch_lowest_temperature(start_time, end_time):
    temperature_logs = fetch_logs_from_database('sensor', 'temp_sensor')
    lowest_temperature = None
    for log in temperature_logs:
        if start_time <= log['timestamp'] <= end_time:
            temperature = log['value']
            if lowest_temperature is None or temperature < lowest_temperature:
                lowest_temperature = temperature
    return lowest_temperature

# Function to fetch the longest duration of motion detection from the previous day
def fetch_longest_motion_duration(start_time, end_time):
    motion_logs = fetch_logs_from_database('sensor', 'PIR')
    longest_duration_seconds = 0
    current_duration_seconds = 0
    last_motion_time = None
    
    for log in motion_logs:
        if start_time <= log['timestamp'] <= end_time:
            motion_detected = log['value']
            
            if motion_detected == "1.0":
                if last_motion_time is not None:
                    # Calculate the duration since the last motion event
                    duration_since_last_motion_seconds = abs((last_motion_time - log['timestamp']).total_seconds())
                    print(duration_since_last_motion_seconds)
                    current_duration_seconds += duration_since_last_motion_seconds
                    # Check if the current duration is longer than the longest duration
                    if current_duration_seconds > longest_duration_seconds:
                        longest_duration_seconds = current_duration_seconds
                last_motion_time = log['timestamp']
            elif motion_detected == "0.0":
                last_motion_time = None
                current_duration_seconds = 0
    
    return longest_duration_seconds

@app.route('/automated_adaptive_settings_from_logs')
def automated_adaptive_settings_from_logs():
    # Get the date of the previous day (can adjust the days)
    previous_day = datetime.now() - timedelta(days=2)
    previous_day_start = datetime(previous_day.year, previous_day.month, previous_day.day, 0, 0, 0)
    previous_day_end = datetime(previous_day.year, previous_day.month, previous_day.day, 23, 59, 59)

    # Get the first and last logs of the previous day for each LED color
    first_red_led_log = fetch_first_log('actuator', 'redLED', previous_day_start, previous_day_end)
    last_red_led_log = fetch_last_log('actuator', 'redLED', previous_day_start, previous_day_end)
    first_yellow_led_log = fetch_first_log('actuator', 'yellowLED', previous_day_start, previous_day_end)
    last_yellow_led_log = fetch_last_log('actuator', 'yellowLED', previous_day_start, previous_day_end)
    first_green_led_log = fetch_first_log('actuator', 'greenLED', previous_day_start, previous_day_end)
    last_green_led_log = fetch_last_log('actuator', 'greenLED', previous_day_start, previous_day_end)

    # Get the highest and lowest temperature from the previous day
    highest_temperature = fetch_highest_temperature(previous_day_start, previous_day_end)
    lowest_temperature = fetch_lowest_temperature(previous_day_start, previous_day_end)

    # Get the longest duration of motion detection from the previous day
    longest_motion_duration = fetch_longest_motion_duration(previous_day_start, previous_day_end)

    # Prepare the JSON response
    json_response = {
        'red_led': {
            'first_log': first_red_led_log,
            'last_log': last_red_led_log
        },
        'yellow_led': {
            'first_log': first_yellow_led_log,
            'last_log': last_yellow_led_log
        },
        'green_led': {
            'first_log': first_green_led_log,
            'last_log': last_green_led_log
        },
        'highest_temperature': highest_temperature,
        'lowest_temperature': lowest_temperature,
        'longest_motion_duration': longest_motion_duration
    }

    return jsonify(json_response)

@app.route('/control_led', methods=['POST'])
def control_led():
    led_status = request.json['led']
    
    # update database based on data updated on client
    data = request.json
    led_color = data['led']  # Access the 'led' key from the JSON data (led color)
    led_status = data['status']  # Access the 'status' key from the JSON data
    
    if (led_color == "red"):
        update_param_value("redLED", led_status)
    elif (led_color == "yellow"):
        update_param_value("yellowLED", led_status)
    elif (led_color == "green"):
        update_param_value("greenLED", led_status)

    # Return success message
    return jsonify({'success': True})

@app.route('/control_lcd', methods=['POST'])
def control_lcd():
    lcd_status = request.json['lcd']
    
    # update database based on data updated on client
    data = request.json
    lcd_status = data['lcd']
    
    update_param_value("LCD", lcd_status)
    return jsonify({'success': True})

@app.route('/control_fan', methods=['POST'])
def control_fan():
    fan_speed = request.json['fan']
    
    # update database based on data updated on client
    data = request.json
    fan_status = data['fan']  
    
    update_param_value("fan", fan_status)
    return jsonify({'success': True})

if __name__ == '__main__':
    defaultDatabaseSetup()
    app.run(host='0.0.0.0', port = 8080, debug = False)
    