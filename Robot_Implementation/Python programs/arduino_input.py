import progress_task as p

try:
    while(1):
        if(serial_communication.in_waiting>0):
            response = serial_communication.readline()
            print(response)
        else:
            s = input().split()
            p.talk_to_arduino(*s)
