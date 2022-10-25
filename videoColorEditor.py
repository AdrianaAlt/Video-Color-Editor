import argparse
import numpy as np
import cv2

wait_time = 3
selected_color = None
hsv_color_range = np.array([10, 10, 10])

def detect_selected_color(frame):
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    light_color = np.array([selected_color[0] - hsv_color_range[0], selected_color[1]-hsv_color_range[1], selected_color[2]-hsv_color_range[2]])
    dark_color = np.array([selected_color[0] + hsv_color_range[0], selected_color[1]+2*hsv_color_range[1], selected_color[2]+2*hsv_color_range[2]])
    mask = cv2.inRange(hsv_frame, light_color, dark_color)
    return mask

def handle_click_color(event, x, y, flags, frame):
    global selected_color
    if event == cv2.EVENT_LBUTTONDOWN:
        hsv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        selected_color = hsv_img[y, x, :]
        print(f'Selected color: hsv={selected_color}')

def shift_color_hue(math_term):
    if 0 <= hsv_color_range[0] + math_term < 180: 
        hsv_color_range[0] += math_term

def shift_color_saturation(math_term):
    if 0 <= hsv_color_range[1] + math_term < 256:
        hsv_color_range[1] += math_term

def shift_color_value(math_term):
    if 0 <= hsv_color_range[2] + math_term < 256:
        hsv_color_range[2] += math_term

hsv_range_keybinding = {
    ord('a'): lambda: shift_color_hue(1),
    ord('z'): lambda: shift_color_hue(-1),
    ord('s'): lambda: shift_color_saturation(1),
    ord('x'): lambda: shift_color_saturation(-1),
    ord('d'): lambda: shift_color_value(1),
    ord('c'): lambda: shift_color_value(-1)
}

def show_video(video_path):
    video_capture = cv2.VideoCapture(video_path)
    if not video_capture.isOpened():
        print(f"Error reading the video file at path {video_path}")
        return
        
    paused, filtered_by_color = False, False

    while (True):
        if not paused:
            captured, frame = video_capture.read()
            if not captured:
                break
        
        pressed_key = cv2.waitKey(wait_time)
        if pressed_key == ord('q'):
            break
        elif pressed_key == ord('p'):
            paused = not paused
        elif pressed_key == ord('e') and selected_color is not None:
            filtered_by_color = not filtered_by_color
        elif pressed_key in hsv_range_keybinding:
            hsv_range_keybinding[pressed_key]()

        if filtered_by_color is True:
            processed_frame = frame.copy()
            selected_color_mask = detect_selected_color(processed_frame)
            processed_frame = cv2.bitwise_and(processed_frame, processed_frame, mask = selected_color_mask)
            cv2.imshow('Video', processed_frame)
        else:
            cv2.imshow('Video', frame)
        cv2.setMouseCallback('Video', handle_click_color, frame)

    video_capture.release()
    cv2.destroyAllWindows()

def parse_arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-i', '--video_path', type=str, required=True, help='Path to the video')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()
    show_video(args.video_path)