import cv2 
import argparse

from ultralytics import YOLO
import supervision as sv
import numpy as np


# #Polygons for number of objects 
# ZONE_POLYGON = np.array([
#     [0,0],
#     [1280//2,0],
#     [1250//2,720],
#     [0,720]
# ])

#return the resolution of the webcam
def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="YOLOv8 live")
    parser.add_argument(
        "--webcam-resolution",
        default=[1280,720],
        nargs=2,
        type=int
    )
    args = parser.parse_args()
    return args

#launching the webcam
def main():
    args = parse_arguments()
    frame_width, frame_height = args.webcam_resolution
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)    
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)    
    
    model = YOLO("best.pt")
    
    box_annotator = sv.BoxAnnotator(
        thickness=2,
        text_thickness=2,
        text_scale=1
    )
    
    #Polygon Controls 
    # zone = sv.PolygonZone(
    #     polygon=ZONE_POLYGON, 
    #     frame_resolution_wh = tuple(args.webcam_resolution)
    #     )
    # zone_annotator = sv.PolygonZoneAnnotator(
    #     zone=zone,
    #     color = sv.Color.red(),
    #     thickness=2,
    #     text_thickness=4,
    #     text_scale=2)
    
    while True:
        ret, frame = cap.read()
        
        cropped_frame = frame[200:700, 200:700]
        #enable the bounding box in the frame
        result = model(cropped_frame)[0]
        
        #Convert YOLOV8 detections to Supervision Bounding Box
        detections = sv.Detections.from_yolov8(result)
        
        #Label the bounding box with the class attached (from the weights), with the confidence
        labels = [
            f"{model.model.names[class_id]} {confidence:0.2f}"
            for _, confidence,class_id, _
            in detections
        ]
        
        frame = box_annotator.annotate(
            scene=cropped_frame, 
            detections= detections, 
            labels=labels
            )
       
        # Printing the coordinates of the Detection
        for i in range(len(detections.xyxy)):
            # Extract bounding box coordinates
            x1, y1, x2, y2 = detections.xyxy[i]
            
            # Calculate center coordinates
            x_center = (x1 + x2) / 2
            y_center = (y1 + y2) / 2
            
            
            #Limit the scope of the detected object to certain ranges
            if not (200 < x_center < 700) or not (200 < y_center < 700):
                continue
            
            # Extract confidence and class_id
            confidence = detections.confidence[i]
            class_id = detections.class_id[i]

            # Print or store the coordinates
            print(f"Object detected at X: {x_center}, Y: {y_center}, Confidence: {confidence}, Class ID: {class_id}")
       
        # Polygon Controls 
        # zone.trigger(detections = detections)
        # frame = zone_annotator.annotate(scene=frame)
        
        cv2.imshow('yolov8',frame)
        
        
        #press escape to exit the program
        if (cv2.waitKey(30)== 27):
            break
    
if __name__ == "__main__":
    main()