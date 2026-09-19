# Wrist-camera manipulation experiment

## Goal

Test whether wrist-camera temporal change can provide useful object-relative evidence around the telemetry-detected manipulation window.

## Method

1. use a pre-grasp wrist frame as a reference;
2. analyze frames around the grasp-to-release window;
3. estimate simple global x/y translation with phase correlation;
4. align the current frame to the reference;
5. measure residual changed pixels and their centroid.

## Real Episode 0 result

The code executed correctly, but the simple translation model did **not** provide reliable compensation on the real moving wrist camera. The strongest compensated frames still showed very large changed fractions (roughly 0.72–0.80 in the observed run), with implausibly large shifts on several frames.

Therefore this experiment is retained as a documented baseline only. Its centroids are **not** used to mark Approach or Place as PASS.

A stronger future method could use feature-based geometric alignment, optical flow, or task-specific segmentation. Those methods are outside the frozen demo scope.
