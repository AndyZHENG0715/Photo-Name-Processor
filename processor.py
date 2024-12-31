import os
import shutil
from datetime import datetime
from PIL import Image
import zipfile

# Define source and destination directories
source_dir = 'media_unprocessed'
destination_dir = 'media_processed'
zip_filename = 'categorized_photos.zip'

# Define meal time ranges (24-hour format)
meal_times = {
    'bf': (6, 11),    # Breakfast: 06:00 - 11:59
    'luc': (12, 14),  # Lunch: 12:00 - 14:59
    'dn': (17, 20),   # Dinner: 17:00 - 20:59
}

# Create destination directory if it doesn't exist
if not os.path.exists(destination_dir):
    os.makedirs(destination_dir)

for filename in os.listdir(source_dir):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        filepath = os.path.join(source_dir, filename)
        try:
            with Image.open(filepath) as img:
                exif_data = img._getexif()
                if exif_data and 36867 in exif_data:
                    date_time_str = exif_data[36867]  # Format: 'YYYY:MM:DD HH:MM:SS'
                    date_part, time_part = date_time_str.split(' ')
                    date_str = date_part.replace(':', '')  # 'YYYYMMDD'
                    hour = int(time_part.split(':')[0])

                    # Determine meal category
                    meal_category = 'snac'  # Default to snacks
                    for meal, (start, end) in meal_times.items():
                        if start <= hour <= end:
                            meal_category = meal
                            break

                    # Create folder name
                    folder_name = f"{date_str}{meal_category}"
                    folder_path = os.path.join(destination_dir, folder_name)

                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)

                    # Construct new filename
                    new_filename = f"{date_str}{meal_category}{os.path.splitext(filename)[1]}"
                    destination_path = os.path.join(folder_path, new_filename)

                    # Move and rename the file
                    shutil.move(filepath, destination_path)
        except Exception as e:
            print(f"Error processing {filename}: {e}")

# Create a zip file of the categorized images
with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(destination_dir):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, destination_dir)
            zipf.write(file_path, arcname)

print(f"Categorized photos have been zipped into '{zip_filename}'.")