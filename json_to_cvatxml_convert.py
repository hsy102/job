import json
import xml.etree.ElementTree as ET
import os
from xml.dom import minidom
from tqdm import tqdm
import argparse 



def format_point(value):
    return f"{value:.2f}" if isinstance(value, float) else f"{value:.2f}"

def create_object_element(annotation):
    obj = ET.Element("object")
    
    name = ET.SubElement(obj, "name")
    name.text = str(annotation["id"])

    deleted = ET.SubElement(obj, "deleted")
    deleted.text = "0"

    verified = ET.SubElement(obj, "verified")
    verified.text = "0"

    occluded = ET.SubElement(obj, "occluded")
    occluded.text = "no"

    date = ET.SubElement(obj, "date")
    date.text = "" 

    id_elem = ET.SubElement(obj, "id")
    id_elem.text = str(annotation["id"])

    parts = ET.SubElement(obj, "parts")
    hasparts = ET.SubElement(parts, "hasparts")
    hasparts.text = ""
    ispartof = ET.SubElement(parts, "ispartof")
    ispartof.text = ""

    polygon = ET.SubElement(obj, "polygon")

    # 모든 pt 추가
    for point in annotation["segmentation"][0][0]:
        pt = ET.SubElement(polygon, "pt")
        x = ET.SubElement(pt, "x")
        x.text = format_point(point[0])
        y = ET.SubElement(pt, "y")
        y.text = format_point(point[1])

    # username 태그 추가
    username = ET.SubElement(polygon, "username")
    username.text = ""

    # attributes 태그 추가
    attributes = ET.SubElement(obj, "attributes")
    attributes.text = "" 

    return obj

def create_xml_element(data):
    annotation = ET.Element("annotation")

    # filename, folder, source
    filename = ET.SubElement(annotation, "filename")
    filename.text = data["images"]["file_name"]

    folder = ET.SubElement(annotation, "folder")
    folder.text = ""  

    source = ET.SubElement(annotation, "source")
    source_image = ET.SubElement(source, "sourceImage")
    source_image.text = "" 
    source_annotation = ET.SubElement(source, "sourceAnnotation")
    source_annotation.text = "Datumaro"  

    # imagesize 값 불러오기
    imagesize = ET.SubElement(annotation, "imagesize")
    nrows = ET.SubElement(imagesize, "nrows")
    nrows.text = str(data["images"]["height"])
    ncols = ET.SubElement(imagesize, "ncols")
    ncols.text = str(data["images"]["width"])

    # 모든 object 추가
    for ann in data["annotations"]:
        obj_element = create_object_element(ann)
        annotation.append(obj_element)

    return annotation  

def convert_json_to_xml(json_data):
    annotation_element = create_xml_element(json_data)
    return annotation_element 

def main(input_folder):
    json_files = [f for f in os.listdir(input_folder) if f.endswith('.json')]
    error_files = []  # 오류 파일을 저장할 리스트
    
    # 진행률 바 생성
    for json_file in tqdm(json_files, desc="Converting JSON to XML"):
        try:
            with open(os.path.join(input_folder, json_file), 'r', encoding='utf-8') as file:
                json_data = json.load(file)
            
            xml_root = convert_json_to_xml(json_data) 

            output_file_name = os.path.splitext(json_file)[0] + '.xml'
            output_file_path = os.path.join(input_folder, output_file_name)

            xml_str = ET.tostring(xml_root, encoding='utf-8')
            pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="  ")

            pretty_xml_lines = pretty_xml.splitlines()
            final_xml = []
            for line in pretty_xml_lines:
                if line.strip().endswith("/>"):
                    tag_name = line.split("<")[-1].split("/>")[0].strip()
                    final_xml.append(f"<{tag_name}></{tag_name}>")
                elif line.strip() != "<?xml version=\"1.0\" ?>": 
                    final_xml.append(line)

            with open(output_file_path, 'w', encoding='utf-8') as xml_file:
                xml_file.write("\n".join(final_xml))
        
        except Exception as e:
            error_files.append(json_file)  # 오류가 발생한 파일을 리스트에 추가

    # 모든 파일 처리가 끝난 후 오류 파일 출력
    if error_files:
        print("The following files could not be processed:")
        for error_file in error_files:
            print(error_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_folder", type=str, required=True, help="Path to the input folder containing JSON files")
    args = parser.parse_args()
    main(args.input_folder)
