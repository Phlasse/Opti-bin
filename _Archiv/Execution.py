import pyinputplus as pyip
import fivebin

def main():
    print()
    print()
    print("#############################")
    print("###     Binning tools     ###")
    print("#############################")
    print()
    print("Willkommen zu den Jens Tools")
    print(f"Folgende Tools sind bisher im Programm:\n ")
    tools = {1 : "Fivebin", 9 : "Beende das Programm"}

    choice = True
    while choice == True:
        for key in tools:
            print(f'[{key}] - {tools[key]}')
        choice = pyip.inputNum(f"\nWelches Tool moechtest du verwenden?\n")

        if choice==1:
            choice = fivebin.main()
        elif choice==9:
            choice = False
        else:
            print(f"Ich konnte das Programm nicht finden \n")
            continue
    print(f"\n Auf wiedersehen!")
    return False

if __name__ == '__main__':
    main()
    #mid_iterator()
