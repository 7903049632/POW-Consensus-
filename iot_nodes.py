import random
import serial
import time


class Node:

    def __init__(self, name):
        self.name = name
        self.status = "IDLE"
        self.busy_time = 0
        self.idle_time = 0


    def update(self):

        # UNO uses real sensor
        if self.name == "UNO":

            try:

                data = arduino.readline().decode(
                    errors='ignore'
                ).strip()

                if "Node Status : BUSY" in data:
                    self.status = "BUSY"

                elif "Node Status : IDLE" in data:
                    self.status = "IDLE"

            except:
                self.status = "IDLE"


        # Nano Mega simulated
        else:

            self.status = random.choice(
                ["BUSY","IDLE"]
            )


        if self.status=="BUSY":

            self.busy_time=random.randint(2,6)
            self.idle_time=0


        else:

            self.idle_time=random.randint(2,6)
            self.busy_time=0



    def show(self):

        print(
            f"{self.name} --> "
            f"{self.status}"
            f" | Busy:{self.busy_time}s"
            f" | Idle:{self.idle_time}s"
        )



arduino = serial.Serial(
        'COM9',
        9600,
        timeout=1
)

time.sleep(2)



nodes=[

    Node("UNO"),
    Node("NANO"),
    Node("MEGA")

]


print("IoT Nodes Started")


for epoch in range(1,11):


    print("\nEpoch",epoch)


    for node in nodes:

        node.update()
        node.show()


    time.sleep(1)



print("\nSimulation Completed")