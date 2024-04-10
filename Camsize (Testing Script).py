import cv2 

def main():
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        cv2.imshow('yolv8', frame)
        
        print(frame.shape)
        break


if __name__ == '__main__':
    main()