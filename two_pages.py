

def two_pages(num, img):
    overlap_pct = 0.20
    width, height = img.size
    middle = width // 2

    base_part_height = height / num
    overlap_px = int(base_part_height * overlap_pct)
    
    first_page_paths = []
    second_page_paths = []
    
    for i in range(num):
        y0 = max(0, int(i * base_part_height) - overlap_px)
        y1 = min(height, int((i + 1) * base_part_height) + overlap_px)

        left_segment = img.crop((0, y0, middle, y1))

        file_name = f"left_part_{i+1}_of_{num}.png"
        left_segment.save(file_name)
        first_page_paths.append(file_name)
        
        print(f"Zapisano Lewą stronę część {i+1}/{num}")

    for i in range(num):
        y0 = max(0, int(i * base_part_height) - overlap_px)
        y1 = min(height, int((i + 1) * base_part_height) + overlap_px)

        right_segment = img.crop((middle, y0, width, y1))

        file_name = f"right_part_{i+1}_of_{num}.png"
        right_segment.save(file_name)
        second_page_paths.append(file_name)
        
        print(f"Zapisano Prawą stronę część {i+1}/{num}")
    
    return first_page_paths, second_page_paths



