"""
Pokedex card capture — uses a fixed on-screen alignment region instead of
contour detection, since contour-based detection breaks down when a hand
partially covers the card's outline.

Flow:
  1. User holds the card inside the on-screen guide box.
  2. Once the region looks "occupied" (has enough edge content, i.e. isn't
     just an empty background) for a few consecutive frames, we start
     sampling multiple crops over a short window to let autofocus catch up.
  3. The sharpest sample is kept and handed off to your recognition step.
  4. After capture, wait for the region to go empty again before allowing
     a new capture.

Press 'q' to quit.
"""

import cv2


# ---------- Configuration ----------

# x1, y1, x2, y2 — tune these to match your camera framing / physical card slot
CAPTURE_REGION = (170, 100, 460, 400)

STABLE_FRAMES_NEEDED = 8       # consecutive "occupied" frames before we start sampling
MISSING_FRAMES_TO_RESET = 15   # consecutive "empty" frames before allowing a new capture
FLICKER_TOLERANCE = 4          # consecutive missed frames allowed without resetting progress
SAMPLE_COUNT = 10              # number of candidate crops to collect per capture
SAMPLE_INTERVAL = 3            # frames between samples (spreads samples out in time)

OCCUPANCY_EDGE_THRESHOLD = 15.0  # min average edge intensity to consider region "occupied" — tune to your setup


# ---------- Helpers ----------

def get_region_crop(frame, region=CAPTURE_REGION):
    x1, y1, x2, y2 = region
    return frame[y1:y2, x1:x2]


def is_region_occupied(crop, threshold=OCCUPANCY_EDGE_THRESHOLD):
    """
    Rough occupancy check: an empty background has very little edge content,
    while a card (with a border, artwork, text) has much more. This avoids
    needing to find/track a precise contour at all.
    """
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    return edges.mean() > threshold


def sharpness_score(image):
    """Higher = sharper. Variance of Laplacian is a standard focus-quality measure."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()


def expand_crop(frame, region, pad_ratio=0.05):
    """Grab the region with an extra pad_ratio margin on each side, clamped to frame bounds."""
    x1, y1, x2, y2 = region
    w = x2 - x1
    h = y2 - y1
    pad_x = int(w * pad_ratio)
    pad_y = int(h * pad_ratio)

    fh, fw = frame.shape[:2]
    x1 = max(0, x1 - pad_x)
    y1 = max(0, y1 - pad_y)
    x2 = min(fw, x2 + pad_x)
    y2 = min(fh, y2 + pad_y)

    return frame[y1:y2, x1:x2]


# ---------- Main loop ----------

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Could not open camera. Check the device index (try 1, 2, ...).")

    stable_count = 0
    missing_count = 0
    flicker_count = 0
    captured = False

    sampling = False
    samples = []
    frames_since_last_sample = 0

    print("Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        display = frame.copy()
        region_crop = get_region_crop(frame)
        occupied = is_region_occupied(region_crop)

        if occupied:
            missing_count = 0
            flicker_count = 0

            if not captured and not sampling:
                stable_count += 1
                if stable_count >= STABLE_FRAMES_NEEDED:
                    sampling = True
                    samples = []
                    frames_since_last_sample = 0

            if sampling:
                frames_since_last_sample += 1
                if frames_since_last_sample >= SAMPLE_INTERVAL:
                    frames_since_last_sample = 0
                    crop = expand_crop(frame, CAPTURE_REGION, pad_ratio=0.05)
                    score = sharpness_score(crop)
                    samples.append((score, crop))

                    if len(samples) >= SAMPLE_COUNT:
                        best_score, best_crop = max(samples, key=lambda s: s[0])
                        cv2.imshow("Isolated crop", best_crop)

                        # result = recognize(best_crop)   # <-- hook your recognition model here
                        print(f"Captured best of {SAMPLE_COUNT} samples (sharpness={best_score:.1f})")

                        sampling = False
                        captured = True

        else:
            missing_count += 1

            if not captured:
                flicker_count += 1
                if flicker_count > FLICKER_TOLERANCE:
                    stable_count = 0
                    if sampling:
                        sampling = False  # genuinely empty, not just a flicker

            if missing_count >= MISSING_FRAMES_TO_RESET:
                captured = False

        # --- draw guide box + status ---
        x1, y1, x2, y2 = CAPTURE_REGION
        box_color = (0, 255, 0) if occupied else (255, 255, 0)
        cv2.rectangle(display, (x1, y1), (x2, y2), box_color, 2)
        cv2.putText(display, "Align card here", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, box_color, 2)

        if sampling:
            status = f"focusing... {len(samples)}/{SAMPLE_COUNT}"
        elif captured:
            status = "card locked in - remove to scan next"
        else:
            status = "waiting for new card"

        cv2.putText(display, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.imshow("Feed", display)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()