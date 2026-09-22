import cv2
import numpy as np


def adjust_gamma(image, gamma=1.5):
    """গামা বাড়িয়ে ডার্ক পিক্সেল উজ্জ্বল করা (Gamma > 1.0 ডার্ক বুস্ট করে)"""
    inv_gamma = 1.0 / gamma
    table = np.array(
        [((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]
    ).astype("uint8")
    return cv2.LUT(image, table)


cap = cv2.VideoCapture(0)

# ল্যাপটপ ক্যামেরার এক্সপোজার বুস্ট করার চেষ্টা (ক্যামেরা হার্ডওয়্যারে সাপোর্টেড থাকলে কাজ করবে)
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.75)

# CLAHE অবজেক্ট তৈরি: Clip Limit নয়েজ নিয়ন্ত্রণ করে, Tile Grid লোকাল এরিয়া ভাগ করে
clahe = cv2.createCLAHE(clipLimit=3.5, tileGridSize=(8, 8))

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)

    # ১. গামা কারেকশন দিয়ে ডার্ক শ্যাডো লাইট করা
    brightened = adjust_gamma(frame, gamma=2.0)

    # ২. লুমিন্যান্স (Y-চ্যানেল) আলাদা করে কনট্রাস্ট বাড়ানো
    # BGR থেকে YCrCb কালার স্পেসে কনভার্ট (শুধু উজ্জ্বলতা নিয়ন্ত্রণ করতে)
    ycrcb = cv2.cvtColor(brightened, cv2.COLOR_BGR2YCrCb)
    y_channel, cr, cb = cv2.split(ycrcb)

    # ৩. লোকাল অ্যাডাপ্টিভ কনট্রাস্ট অ্যাপ্লাই
    enhanced_y = clahe.apply(y_channel)

    # ৪. কম আলোর সেন্সর নয়েজ স্মুথ করা (Edge অক্ষত রেখে)
    denoised_y = cv2.bilateralFilter(enhanced_y, d=5, sigmaColor=50, sigmaSpace=50)

    # ৫. থার্মাল হিটম্যাপে রূপান্তর
    # উন্নত করা লুমিন্যান্স চ্যানেলে সরাসরি JET কালারম্যাপ অ্যাপ্লাই
    night_thermal = cv2.applyColorMap(denoised_y, cv2.COLORMAP_JET)

    # অরিজিনাল ও প্রসেস করা ফ্রেম পাশাপাশি প্রদর্শন
    cv2.imshow("Low-Light Thermal View", night_thermal)
    cv2.imshow("Original WebCam", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()