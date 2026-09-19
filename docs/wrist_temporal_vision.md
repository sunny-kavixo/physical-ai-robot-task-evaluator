# Wrist-camera manipulation evidence

The exterior-camera validation showed that generic YOLO fragmented the pot area
into multiple tracks and did not reliably identify the marker or gripper.

The next perception path therefore uses the DROID wrist camera and robot
telemetry together:

1. telemetry supplies the grasp/release manipulation window;
2. a pre-grasp wrist frame becomes the visual reference;
3. temporal image change is measured through the manipulation window;
4. changed-region centroids provide inspectable spatial evidence;
5. later stages can use this evidence to localize approach/place without
   pretending a generic COCO label is a robot-task identity.

This is currently an evidence extractor, not a claim of automatic Approach or
Place success. It must first be validated on real DROID episodes.
