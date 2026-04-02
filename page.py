from prompts import first_prompt
from api import gemini_api
from def_label import define_label
import json

class Page:
    overlap_pct = 0.2
    
    def __init__(self, num, img):
        self.num = num
        self.img = img

    def onePage(self):
        width, height = self.img.size

        structure = define_label(self.img)

        context_prompt = f"{first_prompt}\n\nStruktura dokumentu: {json.dumps(structure)}"
        
        base_part_height = height / self.num
        overlap_px = int(base_part_height * self.overlap_pct)

        final_data = []

        for i in range(self.num):
            y0 = max(0, int(i * base_part_height) - overlap_px)
            y1 = min(height, int((i + 1) * base_part_height) + overlap_px)

            crop = self.img.crop((0, y0, width, y1))

            try:
                response = gemini_api(context_prompt, crop)
                clean_text = response.text.replace('```json', '').replace('```', '').strip()
                
                json_response = json.loads(clean_text)

                json_response['meta_record_type'] = structure.get('record_type')
                final_data.append(json_response)

            except Exception as e:
                return f"Wystąpił błąd we fragmencie {i}: {e}"
        
        return final_data

    def twoPages(self):
        width, height = self.img.size
        middle = width // 2

        base_part_height = height / self.num
        overlap_px = int(base_part_height * self.overlap_pct)
        
        first_page_paths = []
        second_page_paths = []
        
        for i in range(self.num):
            y0 = max(0, int(i * base_part_height) - overlap_px)
            y1 = min(height, int((i + 1) * base_part_height) + overlap_px)

            left_segment = self.img.crop((0, y0, middle, y1))

            file_name = f"left_part_{i+1}_of_{self.num}.png"
            left_segment.save(file_name)
            first_page_paths.append(file_name)
            
            print(f"Zapisano Lewą stronę część {i+1}/{self.num}")

        for i in range(self.num):
            y0 = max(0, int(i * base_part_height) - overlap_px)
            y1 = min(height, int((i + 1) * base_part_height) + overlap_px)

            right_segment = self.img.crop((middle, y0, width, y1))

            file_name = f"right_part_{i+1}_of_{self.num}.png"
            right_segment.save(file_name)
            second_page_paths.append(file_name)
            
            print(f"Zapisano Prawą stronę część {i+1}/{self.num}")
        
        return first_page_paths, second_page_paths
