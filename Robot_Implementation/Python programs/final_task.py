import arduino_input as a

l = [
    'I','O4','M1','L','M1','M1','L','T45','D','L','D','T-45','D','L','M1','M1',
    'M1','M1','R','T-45','D','R','D','T45','D','R','M1','M1','R','M1'
    'T-45','D','R','T45','D','R','T45','D','R','T45','D','R','R'
]
if __name__ == "__main__":
    try:
        while(1):
            for i in l:
                if(i == 'D'):
                    time.sleep(2)
                else:
                    talker.talk_to_arduino(i)
                time.sleep(1)
    except KeyboardInterrupt:
        talk_to_arduino("X")
        print("Closing")