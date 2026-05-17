import { LandmarkList } from '@mediapipe/hands';

export type Gesture = 'point' | 'pinch' | 'swipe_right' | 'fist' | 'none';

let swipeHistory: { x: number; timestamp: number }[] = [];

export const detectGesture = (landmarks: LandmarkList): Gesture => {
  if (!landmarks || landmarks.length < 21) return 'none';

  const indexTip = landmarks[8];
  const thumbTip = landmarks[4];
  const middleTip = landmarks[12];
  const ringTip = landmarks[16];
  const pinkyTip = landmarks[20];

  // 1. Pinch Detection (Index + Thumb)
  const pinchDistance = Math.hypot(indexTip.x - thumbTip.x, indexTip.y - thumbTip.y);
  if (pinchDistance < 0.04) return 'pinch';

  // 2. Fist Detection (All fingers folded towards palm)
  // Check if finger tips are below their respective mid-joints (simplified)
  const isFist = 
    indexTip.y > landmarks[6].y && 
    middleTip.y > landmarks[10].y && 
    ringTip.y > landmarks[14].y && 
    pinkyTip.y > landmarks[18].y;
  
  if (isFist) return 'fist';

  // 3. Swipe Detection (Tracking movement over time)
  const now = Date.now();
  swipeHistory.push({ x: indexTip.x, timestamp: now });
  swipeHistory = swipeHistory.filter(h => now - h.timestamp < 300); // Keep last 300ms

  if (swipeHistory.length > 5) {
    const startX = swipeHistory[0].x;
    const endX = swipeHistory[swipeHistory.length - 1].x;
    const deltaX = endX - startX;

    // Moving left in camera (which is mirrored) = Swipe Right for user
    if (deltaX < -0.3) {
      swipeHistory = []; // Reset after detection
      return 'swipe_right';
    }
  }

  // 4. Default to pointing
  return 'point';
};
