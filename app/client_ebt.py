import minimalmodbus
import json
import requests
import time
import datetime
import csv

url = "http://10.46.10.128:5000/monitoring_ebt"
headers = {
'Content-Type': 'application/json'
}

# --------------------- JUDUL TABEL ---------------------#
header_added = False
table_header = ['client_id_6', 'send_to_db_at', 'processing_time_6', 'voltage_6', 'current_6', 'power_6', 'energy_6', 'client_id_7', 'data_created_at', 'processing_time_7', 'voltage_7', 'current_7', 'power_7', 'energy_7', 'power_factor'] 
with open('logger_surya_v6_real_new.csv','a', newline='') as f:
    writer = csv.writer(f)
    if not header_added:
        writer.writerow(i for i in table_header)
        header_added = True

# ------------------ ID PZEM --------------------- #
mb_address_AC = 1 # Modbus address of sensor
mb_address_DC = 2 # Modbus address of sensor

while True:
    try:
        # --------------------- TIME --------------------------#
        time_awal_6 = time.time()
        time_awal_7 = time.time()
        # ---------------- INISIASI SENSOR ------------------ #
        # -------------------- SENSOR DC ---------------------------- #

        instrument_DC = minimalmodbus.Instrument('/dev/ttyUSB1', mb_address_DC)	# Make an "instrument" object called instrument_DC (port name, slave address (in decimal))
        # print(instrument_DC)
        instrument_DC.serial.baudrate = 9600				# BaudRate
        instrument_DC.serial.bytesize = 8					# Number of data bits to be requested
        instrument_DC.serial.parity = minimalmodbus.serial.PARITY_NONE	# Parity Setting here is NONE but can be ODD or EVEN
        instrument_DC.serial.stopbits = 2					# Number of stop bits
        instrument_DC.serial.timeout  = 3					# Timeout time in seconds
        instrument_DC.mode = minimalmodbus.MODE_RTU				# Mode to be used (RTU or ascii mode)

        # Good practice to clean up before and after each execution
        instrument_DC.clear_buffers_before_each_transaction = True
        instrument_DC.close_port_after_each_call = True

        # --------------------------------- SENSOR AC ---------------- #
        instrument_AC = minimalmodbus.Instrument('/dev/ttyUSB0',mb_address_AC)	# Make an "instrument" object called instrument_AC (port name, slave address (in decimal))
        # print(instrument_AC)
        instrument_AC.serial.baudrate = 9600				# BaudRate
        instrument_AC.serial.bytesize = 8					# Number of data bits to be requested
        instrument_AC.serial.parity = minimalmodbus.serial.PARITY_NONE	# Parity Setting here is NONE but can be ODD or EVEN
        instrument_AC.serial.stopbits = 1					# Number of stop bits
        instrument_AC.serial.timeout  = 2					# Timeout time in seconds
        instrument_AC.mode = minimalmodbus.MODE_RTU				# Mode to be used (RTU or ascii mode)

        # Good practice to clean up before and after each execution
        instrument_AC.clear_buffers_before_each_transaction = True
        instrument_AC.close_port_after_each_call = True

        """PEMBACAAN DATA DARI SENSOR"""
        data_1 = instrument_DC.read_registers(0, 8, 4) 
        data_2 = instrument_AC.read_registers(0, 10, 4)

        """PZEM 017"""
        client_id_6 = 6
        voltage_6 = data_1[0]/100
        current_6 = data_1[1]/100
        power_6 = round(voltage_6*current_6,5)
        # power_6 = (data_1[3] << 16) + (data_1[2])/10
        energy_6 = round(power_6*5/60,5)
        time_akhir_6 = time.time()
        processing_time_6 = time_akhir_6-time_awal_6

        """PZEM 004T"""
        client_id_7 = 7
        voltage_7 = data_2[0] / 10.0
        current_7 = (data_2[1] + (data_2[2] << 16)) / 1000.0
        power_7 = round(voltage_7*current_7,5)
        energy_7 = round(power_7*5/60,5)
        power_factor = data_2[8]/100.0
        time_akhir_7 = time.time()
        processing_time_7 = time_akhir_7-time_awal_7

        """DATA CREATED AT"""
        data_created_at = datetime.datetime.now()+datetime.timedelta(hours=7)

        """CSV"""
        data = [client_id_6, data_created_at, processing_time_6, voltage_6, current_6, power_6, energy_6, client_id_7, data_created_at, processing_time_7, voltage_7, current_7, power_7, energy_7, power_factor]
        with open('logger_surya_v6_real_new.csv','a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(data)

        """SEND TO SERVER -> DATABASE"""
        """PZEM 017"""
        send_to_db_at_6 = datetime.datetime.now()+datetime.timedelta(hours=7)
        payload_6 = json.dumps(
            {'client_id':client_id_6,
                'data':
            {
            'send_to_db_at': str(send_to_db_at_6),
            'processing_time': str(processing_time_6),
            'voltage': voltage_6,
            'current': current_6,
            'power': power_6,
            'energy': energy_6,
            'power_factor' : 0,
            }   
            }
        )

        response_6 = requests.request("POST", url, headers=headers, data=payload_6)

        """PZEM 004T"""
        send_to_db_at_7 = datetime.datetime.now()+datetime.timedelta(hours=7)
        payload_7 = json.dumps(
            {'client_id':client_id_7,
            'data':
            {
            'send_to_db_at': str(send_to_db_at_7),
            'processing_time': str(processing_time_7),
            'voltage': voltage_7,
            'current': current_7,
            'power': power_7,
            'energy': energy_7,
            'power_factor' : power_factor,
            }   
            }
        )

        response_7 = requests.request("POST", url, headers=headers, data=payload_7)

        print(response_6.text)
        print(response_7.text)

        # print(payload_6)
        # print(payload_7)

        print("--------------------------------")
        time.sleep(300)

    except:
        try:
            # --------------------- TIME --------------------------#
            time_awal_6 = time.time()
            # ---------------- INISIASI SENSOR ------------------ #
            # -------------------- SENSOR DC ---------------------------- #

            instrument_DC = minimalmodbus.Instrument('/dev/ttyUSB1', mb_address_DC)	# Make an "instrument" object called instrument_DC (port name, slave address (in decimal))
            # print(instrument_DC)
            instrument_DC.serial.baudrate = 9600				# BaudRate
            instrument_DC.serial.bytesize = 8					# Number of data bits to be requested
            instrument_DC.serial.parity = minimalmodbus.serial.PARITY_NONE	# Parity Setting here is NONE but can be ODD or EVEN
            instrument_DC.serial.stopbits = 2					# Number of stop bits
            instrument_DC.serial.timeout  = 3					# Timeout time in seconds
            instrument_DC.mode = minimalmodbus.MODE_RTU				# Mode to be used (RTU or ascii mode)

            # Good practice to clean up before and after each execution
            instrument_DC.clear_buffers_before_each_transaction = True
            instrument_DC.close_port_after_each_call = True

            """PEMBACAAN DATA DARI SENSOR"""
            data_1 = instrument_DC.read_registers(0, 8, 4) 

            """pzem 017"""
            client_id_6 = 6
            voltage_6 = data_1[0]/100
            current_6 = data_1[1]/100
            power_6 = round(voltage_6*current_6,5)
            # power_6 = (data_1[3] << 16) + (data_1[2])/10
            energy_6 = round(power_6*5/60,5)

            time_akhir_6 = time.time()
            processing_time_6 = time_akhir_6-time_awal_6
            
            """DATA CREATED AT"""
            data_created_at = datetime.datetime.now()+datetime.timedelta(hours=7)
                    
            """CSV"""
            data = [client_id_6, data_created_at, processing_time_6, voltage_6, current_6, power_6, energy_6, 7, data_created_at, 0, 0, 0, 0, 0, 0]
            with open('logger_surya_v6_real_new.csv','a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(data)

            """SEND TO SERVER -> DATABASE"""
            send_to_db_at_6 = datetime.datetime.now()+datetime.timedelta(hours=7)
            payload_6 = json.dumps(
                {'client_id':client_id_6,
                'data':
                {
                'send_to_db_at': str(send_to_db_at_6),
                'processing_time': str(processing_time_6),
                'voltage': voltage_6,
                'current': current_6,
                'power': power_6,
                'energy': energy_6,
                'power_factor' : 0,
                }   
                }
            )

            response_6 = requests.request("POST", url, headers=headers, data=payload_6)
            print(response_6.text)
            # print(payload_6)
            print("--------------------------------")
            time.sleep(300)
        except:
            # --------------------- TIME --------------------------#
            time_awal_7 = time.time()
            # --------------------------------- SENSOR AC ---------------- #
            instrument_AC = minimalmodbus.Instrument('/dev/ttyUSB0',mb_address_AC)	# Make an "instrument" object called instrument_AC (port name, slave address (in decimal))
            # print(instrument_AC)
            instrument_AC.serial.baudrate = 9600				# BaudRate
            instrument_AC.serial.bytesize = 8					# Number of data bits to be requested
            instrument_AC.serial.parity = minimalmodbus.serial.PARITY_NONE	# Parity Setting here is NONE but can be ODD or EVEN
            instrument_AC.serial.stopbits = 1					# Number of stop bits
            instrument_AC.serial.timeout  = 2					# Timeout time in seconds
            instrument_AC.mode = minimalmodbus.MODE_RTU				# Mode to be used (RTU or ascii mode)

            # Good practice to clean up before and after each execution
            instrument_AC.clear_buffers_before_each_transaction = True
            instrument_AC.close_port_after_each_call = True

            """PEMBACAAN DATA DARI SENSOR"""
            data_2 = instrument_AC.read_registers(0, 10, 4)
            
            """PZEM 004T"""
            client_id_7 = 7
            voltage_7 = data_2[0] / 10.0
            current_7 = (data_2[1] + (data_2[2] << 16)) / 1000.0
            power_7 = round(voltage_7*current_7,5)
            energy_7 = round(power_7*5/60,5)
            power_factor = data_2[8]/100.0

            time_akhir_7 = time.time()
            processing_time_7 = time_akhir_7-time_awal_7

            """DATA CREATED AT"""
            data_created_at = datetime.datetime.now()+datetime.timedelta(hours=7)
                    
            """CSV"""
            data = [6, data_created_at, 0, 0, 0, 0, 0, client_id_7, data_created_at, processing_time_7, voltage_7, current_7, power_7, energy_7, power_factor]
            with open('logger_surya_v6_real_new.csv','a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(data)

            """SEND TO SERVER -> DATABASE"""
            send_to_db_at_7 = datetime.datetime.now()+datetime.timedelta(hours=7)
            payload_7 = json.dumps(
                {'client_id':client_id_7,
                'data':
                {
                'send_to_db_at': str(send_to_db_at_7),
                'processing_time': str(processing_time_7),
                'voltage': voltage_7,
                'current': current_7,
                'power': power_7,
                'energy': energy_7,
                'power_factor' : power_factor,
                }   
                }
            )

            response_7 = requests.request("POST", url, headers=headers, data=payload_7)
            print(response_7.text)
            # print(payload_7)

            print("--------------------------------")
            time.sleep(300)
        else:
            # ------------------------ IF USB CONNECTION ERROR ------------------------- #
            print("PASS: DATA ERROR\n")
            """PZEM 017"""
            time_awal_6 = time.time()
            client_id_6 = 6 
            voltage_6 = 999999
            current_6 = 999999
            power_6 = 999999
            energy_6 = 999999
            power_factor_6 = 999999
            time_akhir_6 = time.time()
            processing_time_6 = time_akhir_6-time_awal_6

            """PZEM 004T"""
            time_awal_7 = time.time()
            client_id_7 = 7
            voltage_7 = 999999
            current_7 = 999999
            power_7 = 999999
            energy_7 = 999999
            power_factor = 999999
            time_akhir_7 = time.time()
            processing_time_7 = time_akhir_7-time_awal_7

            """DATA CREATED AT"""
            data_created_at = datetime.datetime.now()+datetime.timedelta(hours=7)

            """CSV"""
            data = [client_id_6, data_created_at, processing_time_6, voltage_6, current_6, power_6, energy_6, client_id_7, data_created_at, processing_time_7, voltage_7, current_7, power_7, energy_7, power_factor]
            with open('logger_surya_v6_real_new.csv','a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(data)

            """SEND TO SERVER -> DATABASE"""
            """PZEM 017"""
            send_to_db_at_6 = datetime.datetime.now()+datetime.timedelta(hours=7)
            payload_6 = json.dumps(
                {'client_id':client_id_6,
                'data':
                {
                'send_to_db_at': str(send_to_db_at_6),
                'processing_time': str(processing_time_6),
                'voltage': voltage_6,
                'current': current_6,
                'power': power_6,
                'energy': energy_6,
                'power_factor' : power_factor_6,
                }   
                }
            )

            response_6 = requests.request("POST", url, headers=headers, data=payload_6)

            """PZEM 004T"""
            send_to_db_at_7 = datetime.datetime.now()+datetime.timedelta(hours=7)
            payload_7 = json.dumps(
                {'client_id':client_id_7,
                'data':
                {
                'send_to_db_at': str(send_to_db_at_7),
                'processing_time': str(processing_time_7),
                'voltage': voltage_7,
                'current': current_7,
                'power': power_7,
                'energy': energy_7,
                'power_factor' : power_factor,
                }   
                }
            )

            response_7 = requests.request("POST", url, headers=headers, data=payload_7)

            print(response_6.text)
            print(response_7.text)

            # print(payload_6)
            # print(payload_7)
            print("--------------------------------")
            time.sleep(300)