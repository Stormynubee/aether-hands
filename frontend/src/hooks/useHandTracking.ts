import { useEffect, useRef, useState } from 'react';

export const useHandTracking = (onResults: (results: any) => void) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let camera: any = null;
    let hands: any = null;

    const init = async () => {
      try {
        console.log("Loading MediaPipe Hands...");
        // @ts-ignore
        const mpHands = window.Hands;
        // @ts-ignore
        const mpCamera = window.Camera;

        if (!mpHands || !mpCamera) {
          setError("MediaPipe scripts not loaded. Check index.html for CDN links.");
          return;
        }

        hands = new mpHands({
          locateFile: (file: string) => {
            return `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`;
          },
        });

        hands.setOptions({
          maxNumHands: 1,
          modelComplexity: 1,
          minDetectionConfidence: 0.5,
          minTrackingConfidence: 0.5,
        });

        hands.onResults(onResults);

        if (!videoRef.current) return;

        console.log("Starting Camera...");
        camera = new mpCamera(videoRef.current, {
          onFrame: async () => {
            if (videoRef.current) {
              await hands.send({ image: videoRef.current });
            }
          },
          width: 1280,
          height: 720,
        });

        await camera.start();
        console.log("Camera started successfully.");
        setIsLoaded(true);
      } catch (err: any) {
        console.error("Vision Init Error:", err);
        setError(err.message || "Failed to initialize vision system.");
      }
    };

    init();

    return () => {
      if (camera) camera.stop();
      if (hands) hands.close();
    };
  }, []);

  return { videoRef, isLoaded, error };
};
