

def one_page(num, img):
    overlap_pct = 0.20
    width, height = img.size
    
    base_part_height = height / num
    overlap_px = int(base_part_height * overlap_pct)

    parts_path = []

    for i in range(num):
        y0 = max(0, int(i * base_part_height) - overlap_px)
        y1 = min(height, int((i + 1) * base_part_height) + overlap_px)

        crop = img.crop((0, y0, width, y1))

        file_name = f"segment_{i+1}_of_{num}.png"
        crop.save(file_name)
        
        print(f"Zapisano część {i+1}/{num}: {y0}px do {y1}px")
    
    return parts_path





